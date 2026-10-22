"""The golden demo path, end to end, in replay mode: the one thing that must always work.

xfail until the features exist; it must be green from prompt 06 on (remove the marker then).
If it goes red after that, fixing it beats every other task. It must never pass because a result
was hardcoded: PayPal work is checked through the API Trace, the flip is checked on a paraphrase
too, and the pick must be the ranker's first item.
"""

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.settings import REPO_ROOT

FIXTURES = REPO_ROOT / "data" / "fixtures"
# Draft from DEMO_SCRIPT.md; both queries are locked in prompt 03 with the seed catalog.
GOLDEN_QUERY = "waterproof wide-fit hiking boots under $120"
PARAPHRASE = "wide width waterproof hiking boot, budget 120 dollars"
# Her genuinely under-described boot; the real ID is set when the seed catalog lands (prompt 03).
HERO_PRODUCT_ID = "set-in-prompt-03"
# Recorded PAYMENT.CAPTURE.COMPLETED delivery: {"headers": {PAYPAL-*...}, "body": "<raw JSON>"}.
WEBHOOK_DELIVERY = FIXTURES / "paypal" / "webhook_capture_completed.json"

pytestmark = pytest.mark.xfail(strict=False, reason="not built yet: lands in prompts 02-06")

# Response bodies are checked as plain JSON, the way the browser sees them.
Json = Any


class Session:
    """Calls the API like the browser does and keeps every response body for the brand check."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.bodies: list[str] = []

    def call(self, method: str, path: str, **kwargs: Any) -> Json:
        response = self.client.request(method, path, **kwargs)
        self.bodies.append(response.text)
        assert response.is_success, f"{method} {path} → {response.status_code}: {response.text}"
        return response.json()

    def status_of(self, method: str, path: str, **kwargs: Any) -> int:
        response = self.client.request(method, path, **kwargs)
        self.bodies.append(response.text)
        return response.status_code


def paypal_trace(events: list[Json], method: str, endpoint: str) -> list[Json]:
    return [
        e
        for e in events
        if e["service"] == "paypal" and e["method"] == method and e["endpoint"] == endpoint
    ]


def values_for_key(node: Json, key: str) -> list[str]:
    if isinstance(node, dict):
        found = [str(node[key])] if key in node else []
        return found + [v for child in node.values() for v in values_for_key(child, key)]
    if isinstance(node, list):
        return [v for child in node for v in values_for_key(child, key)]
    return []


def recorded_competitor_brands() -> set[str]:
    paths = (FIXTURES / "channel3").glob("*.json")
    return {b for p in paths for b in values_for_key(json.loads(p.read_text()), "brand") if b}


def test_golden_path(client: TestClient) -> None:
    api = Session(client)
    api.call("POST", "/api/demo/reset")

    # 1. Import the catalog; every product lands in the PayPal sandbox catalog.
    api.call("POST", "/api/catalog/import")
    synced = api.call("POST", "/api/catalog/sync")
    products = api.call("GET", "/api/products")
    assert products
    assert all(p["paypal_product_id"] for p in products)
    hero_paypal_id = synced["paypal_product_ids"][HERO_PRODUCT_ID]

    # 2. Before enrichment: the agent picks a competitor, on the golden query and a paraphrase.
    before = api.call("POST", "/api/benchmark/runs", json={"split": "heldout", "k": 5})
    for query in (GOLDEN_QUERY, PARAPHRASE):
        pick = api.call("POST", "/api/shopper/recommend", json={"query": query})
        assert pick["pick"] == pick["ranked"][0]
        assert pick["pick"]["owner"] == "competitor"

    # 3. Enrichment proposes grounded fixes; only grounded ones are approved here.
    proposals = api.call("POST", "/api/enrichment/proposals", json={"product_ids": []})
    grounded = [p for p in proposals if p["grounded"]]
    assert grounded
    assert all(p["spans"] for p in grounded)

    # 4. Merchant approves; the PayPal catalog PATCH really happened (trace), benchmark re-runs.
    approval = api.call(
        "POST",
        "/api/enrichment/approvals",
        json={"proposal_ids": [p["id"] for p in grounded], "decision": "approve"},
    )
    assert HERO_PRODUCT_ID in approval["paypal_synced_product_ids"]
    trace = api.call("GET", "/api/trace", params={"after": 0})
    patches = paypal_trace(trace, "PATCH", "/v1/catalogs/products/{id}")
    assert any(e["sandbox_ids"].get("product_id") == hero_paypal_id for e in patches)
    assert all(e["cache"] == "replayed" for e in trace)

    # 5. Same benchmark, same queries: the held-out score rises and both requests now pick her.
    after = api.call("GET", f"/api/benchmark/runs/{approval['benchmark_run_id']}")
    assert (after["split"], after["k"], after["n_queries"]) == (
        before["split"],
        before["k"],
        before["n_queries"],
    )
    assert after["share_of_shelf"] > before["share_of_shelf"]
    assert after["visibility_score"] > before["visibility_score"]
    for query in (PARAPHRASE, GOLDEN_QUERY):
        after_pick = api.call("POST", "/api/shopper/recommend", json={"query": query})
        assert after_pick["pick"] == after_pick["ranked"][0]
        assert after_pick["pick"]["owner"] == "merchant"
        assert after_pick["pick"]["item_id"] == HERO_PRODUCT_ID

    # 6. PayPal order → (buyer approval recorded in fixtures) → capture, all visible in the trace.
    order = api.call("POST", "/api/orders", json={"recommendation_id": after_pick["id"]})
    assert order["source"] is None
    captured = api.call("POST", f"/api/orders/{order['id']}/capture")
    assert (captured["status"], captured["capture_status"]) == ("COMPLETED", "COMPLETED")
    trace = api.call("GET", "/api/trace", params={"after": 0})
    created = paypal_trace(trace, "POST", "/v2/checkout/orders")
    assert any(e["sandbox_ids"].get("order_id") == order["paypal_order_id"] for e in created)
    captures = paypal_trace(trace, "POST", "/v2/checkout/orders/{id}/capture")
    assert any(e["sandbox_ids"].get("capture_id") == captured["capture_id"] for e in captures)

    # 7. Webhook: unsigned and tampered deliveries are rejected and change nothing...
    delivery = json.loads(WEBHOOK_DELIVERY.read_text())
    raw: bytes = delivery["body"].encode()
    assert api.status_of("POST", "/webhooks/paypal", content=raw) == 400
    tampered = raw.replace(b"COMPLETED", b"COMPLETEd")
    headers = delivery["headers"]
    assert api.status_of("POST", "/webhooks/paypal", content=tampered, headers=headers) == 400
    assert api.call("GET", f"/api/orders/{order['id']}")["source"] is None

    # ...the real one tags the order agent-sourced, exactly once.
    signed = {"content": raw, "headers": delivery["headers"]}
    assert api.call("POST", "/webhooks/paypal", **signed)["processed"] is True
    assert api.call("POST", "/webhooks/paypal", **signed)["processed"] is False
    tagged = api.call("GET", f"/api/orders/{order['id']}")
    assert (tagged["source"], tagged["confirmed_by"]) == ("agent", "webhook")

    # 8. Dashboard counts it as agent-sourced revenue.
    dashboard = api.call("GET", "/api/dashboard")
    assert dashboard["agent_order_count"] >= 1
    assert dashboard["agent_revenue"]["amount_cents"] >= order["amount"]["amount_cents"]

    # 9. Trademark rule: no real competitor brand reached the browser anywhere on the path.
    brands = recorded_competitor_brands()
    assert brands
    leaked = {b for b in brands for body in api.bodies if b.lower() in body.lower()}
    assert leaked == set()
