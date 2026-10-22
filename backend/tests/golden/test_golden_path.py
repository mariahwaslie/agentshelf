"""The golden demo path, end to end, in replay mode: the one thing that must always work.

xfail until the features exist; it must be green from prompt 06 on. If it goes red after that,
fixing it beats every other task. It must never pass because a result was hardcoded: every
assertion checks what the real ranker, PayPal client and webhook handler produced.
"""

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.settings import REPO_ROOT

# Draft from DEMO_SCRIPT.md; locked in prompt 03 together with the seed catalog.
GOLDEN_QUERY = "waterproof wide-fit hiking boots under $120"
# Her genuinely under-described boot; the real ID is set when the seed catalog lands (prompt 03).
HERO_PRODUCT_ID = "set-in-prompt-03"
# Recorded PAYMENT.CAPTURE.COMPLETED event for the golden order (prompt 06).
WEBHOOK_EVENT = REPO_ROOT / "data" / "fixtures" / "paypal" / "webhook_capture_completed.json"

pytestmark = pytest.mark.xfail(strict=False, reason="not built yet: lands in prompts 02-06")

# Response bodies are checked as plain JSON, the way the browser sees them.
Json = Any


def ok(response: Response) -> Json:
    request = response.request
    assert response.is_success, (
        f"{request.method} {request.url.path} → {response.status_code}: {response.text}"
    )
    return response.json()


def test_golden_path(client: TestClient) -> None:
    ok(client.post("/api/demo/reset"))

    # 1. Import the catalog; every product lands in the PayPal sandbox catalog.
    ok(client.post("/api/catalog/import"))
    synced = ok(client.post("/api/catalog/sync"))
    products = ok(client.get("/api/products"))
    assert products
    assert all(p["paypal_product_id"] for p in products)
    assert HERO_PRODUCT_ID in synced["paypal_product_ids"]

    # 2. Benchmark before enrichment: low score, and the agent picks a competitor.
    before = ok(client.post("/api/benchmark/runs", json={"split": "heldout", "k": 5}))
    before_pick = ok(client.post("/api/shopper/recommend", json={"query": GOLDEN_QUERY}))
    assert before_pick["pick"]["owner"] == "competitor"

    # 3. Enrichment proposes grounded fixes; ungrounded ones are never approved here.
    proposals = ok(client.post("/api/enrichment/proposals", json={"product_ids": []}))
    grounded = [p for p in proposals if p["grounded"]]
    assert grounded
    assert all(p["spans"] for p in grounded)

    # 4. Merchant approves; PayPal catalog is updated and the benchmark re-runs.
    approval = ok(
        client.post(
            "/api/enrichment/approvals",
            json={"proposal_ids": [p["id"] for p in grounded], "decision": "approve"},
        )
    )
    assert HERO_PRODUCT_ID in approval["paypal_synced_product_ids"]
    assert approval["benchmark_run_id"]

    # 5. Score rises on the held-out set, and the same request now picks her product.
    after = ok(client.get(f"/api/benchmark/runs/{approval['benchmark_run_id']}"))
    assert after["split"] == "heldout"
    assert after["share_of_shelf"] > before["share_of_shelf"]
    assert after["visibility_score"] > before["visibility_score"]
    after_pick = ok(client.post("/api/shopper/recommend", json={"query": GOLDEN_QUERY}))
    assert after_pick["pick"]["owner"] == "merchant"
    assert after_pick["pick"]["item_id"] == HERO_PRODUCT_ID

    # 6. PayPal order → (buyer approval recorded in fixtures) → capture.
    order = ok(client.post("/api/orders", json={"recommendation_id": after_pick["id"]}))
    assert order["paypal_order_id"]
    assert order["source"] is None
    captured = ok(client.post(f"/api/orders/{order['id']}/capture"))
    assert captured["status"] == "COMPLETED"
    assert captured["capture_id"]

    # 7. Webhook tags it agent-sourced, exactly once.
    event = json.loads(WEBHOOK_EVENT.read_text())
    first = ok(client.post("/webhooks/paypal", json=event))
    duplicate = ok(client.post("/webhooks/paypal", json=event))
    assert first["processed"] is True
    assert duplicate["processed"] is False
    tagged = ok(client.get(f"/api/orders/{order['id']}"))
    assert tagged["source"] == "agent"
    assert tagged["confirmed_by"] == "webhook"

    # 8. Dashboard counts it as agent-sourced revenue.
    dashboard = ok(client.get("/api/dashboard"))
    assert dashboard["agent_order_count"] >= 1
    assert dashboard["agent_revenue"]["amount_cents"] >= order["amount"]["amount_cents"]
