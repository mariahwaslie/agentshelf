from pathlib import Path

from fastapi.testclient import TestClient

from app import __version__
from app.main import create_app
from app.models import AppMode
from app.settings import Settings


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


def test_config_exposes_flags_but_no_secrets(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        app_mode=AppMode.LIVE,
        paypal_client_id="public-client-id",
        paypal_client_secret="never-sent",
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
    assert "never-sent" not in response.text


def test_request_id_is_echoed_when_well_formed(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "demo-123"})
    assert response.headers["X-Request-ID"] == "demo-123"


def test_malformed_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "bad id; drop table"})
    assert response.headers["X-Request-ID"] != "bad id; drop table"
    assert len(response.headers["X-Request-ID"]) == 32


def test_unbuilt_routes_answer_501_with_the_prompt(client: TestClient) -> None:
    response = client.get("/api/products")
    assert response.status_code == 501
    assert response.json() == {"detail": "Not built yet (prompt 03)"}


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
    assert missing_api.status_code == 404
    assert "id=root" not in missing_api.text
