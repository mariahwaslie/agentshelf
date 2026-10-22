from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.main import create_app
from app.models import AppMode
from app.settings import Settings

# Every contract route not built yet, with the smallest valid body so validation passes.
UNBUILT_ROUTES = [
    ("POST", "/api/demo/reset", None),
    ("GET", "/api/trace", None),
    ("POST", "/api/catalog/import", None),
    ("POST", "/api/catalog/sync", None),
    ("GET", "/api/products", None),
    ("GET", "/api/products/p1", None),
    ("GET", "/api/intents", None),
    ("POST", "/api/benchmark/runs", {}),
    ("GET", "/api/benchmark/runs", None),
    ("GET", "/api/benchmark/runs/r1", None),
    ("GET", "/api/benchmark/runs/r1/intents/i1", None),
    ("GET", "/api/fixes", None),
    ("GET", "/api/products/p1/fixes", None),
    ("POST", "/api/enrichment/proposals", {}),
    ("GET", "/api/enrichment/proposals", None),
    ("POST", "/api/enrichment/approvals", {"proposal_ids": ["e1"], "decision": "approve"}),
    ("POST", "/api/shopper/recommend", {"query": "wide boots"}),
    ("POST", "/api/orders", {"recommendation_id": "rec_1"}),
    ("GET", "/api/orders", None),
    ("GET", "/api/orders/o1", None),
    ("POST", "/api/orders/o1/capture", None),
    ("POST", "/webhooks/paypal", {"id": "WH-1"}),
    ("GET", "/api/dashboard", None),
    ("GET", "/api/feed/jsonld", None),
    ("GET", "/api/feed/agent.json", None),
]


def test_health_reports_mode_and_services(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "mode": "replay",
        "version": __version__,
        "services": {
            "paypal": "replay",
            "channel3": "replay",
            "llm": "replay",
            "embeddings": "local",
        },
    }


def test_config_exposes_public_ids_but_no_secrets(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        app_mode=AppMode.LIVE,
        paypal_client_id="public-client-id",
        paypal_client_secret="never-sent",
        ag_license_key="public-ag-key",
        feature_ag_studio=False,
        frontend_dist=tmp_path,
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/config")
    body = response.json()
    assert body["mode"] == "live"
    assert body["display_anonymized"] is True
    assert body["features"]["ag_studio"] is False
    assert body["paypal_client_id"] == "public-client-id"
    assert body["ag_license_key"] == "public-ag-key"
    assert "never-sent" not in response.text


def test_request_id_is_echoed_when_well_formed(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "demo-123"})
    assert response.headers["X-Request-ID"] == "demo-123"


def test_malformed_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "bad id; drop table"})
    assert response.headers["X-Request-ID"] != "bad id; drop table"
    assert len(response.headers["X-Request-ID"]) == 32


def test_crash_still_returns_a_request_id(settings: Settings) -> None:
    app = create_app(settings)

    def boom() -> None:
        raise RuntimeError("simulated failure")

    app.add_api_route("/boom", boom)
    with TestClient(app) as client:
        response = client.get("/boom", headers={"X-Request-ID": "trace-me"})
    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "trace-me"
    assert response.json() == {"detail": "Internal server error"}


@pytest.mark.parametrize(("method", "path", "body"), UNBUILT_ROUTES)
def test_unbuilt_routes_answer_501_with_the_prompt(
    client: TestClient, method: str, path: str, body: object
) -> None:
    response = client.request(method, path, json=body)
    assert response.status_code == 501
    assert response.json()["detail"].startswith("Not built yet (prompt ")


def test_operation_ids_are_handler_names(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert schema["paths"]["/api/products/{product_id}"]["get"]["operationId"] == "get_product"


def test_built_frontend_is_served_with_spa_fallback(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<div id=root></div>")
    settings = Settings(_env_file=None, frontend_dist=tmp_path)
    with TestClient(create_app(settings)) as client:
        assert "id=root" in client.get("/").text
        assert "id=root" in client.get("/dashboard/agent-channel").text
        missing_api = client.get("/api/does-not-exist")
        missing_asset = client.get("/assets/missing.js")
    assert missing_api.status_code == 404
    assert "id=root" not in missing_api.text
    assert missing_asset.status_code == 404
