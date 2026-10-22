"""The API matches docs/contracts.md exactly: no undocumented routes, no missing ones."""

import inspect

import pytest
from fastapi.testclient import TestClient

from app import models
from app.settings import REPO_ROOT

CONTRACT_ROUTES = {
    ("GET", "/health"),
    ("GET", "/api/config"),
    ("POST", "/api/demo/reset"),
    ("GET", "/api/trace"),
    ("POST", "/api/catalog/import"),
    ("POST", "/api/catalog/sync"),
    ("GET", "/api/products"),
    ("GET", "/api/products/{product_id}"),
    ("GET", "/api/intents"),
    ("POST", "/api/benchmark/runs"),
    ("GET", "/api/benchmark/runs"),
    ("GET", "/api/benchmark/runs/{run_id}"),
    ("GET", "/api/benchmark/runs/{run_id}/intents/{intent_id}"),
    ("GET", "/api/fixes"),
    ("GET", "/api/products/{product_id}/fixes"),
    ("POST", "/api/enrichment/proposals"),
    ("GET", "/api/enrichment/proposals"),
    ("POST", "/api/enrichment/approvals"),
    ("POST", "/api/shopper/recommend"),
    ("POST", "/api/orders"),
    ("GET", "/api/orders"),
    ("GET", "/api/orders/{order_id}"),
    ("POST", "/api/orders/{order_id}/capture"),
    ("POST", "/webhooks/paypal"),
    ("GET", "/api/dashboard"),
    ("GET", "/api/feed/jsonld"),
    ("GET", "/api/feed/agent.json"),
}


@pytest.fixture
def openapi(client: TestClient) -> dict[str, dict[str, dict[str, object]]]:
    schema: dict[str, dict[str, dict[str, object]]] = client.get("/openapi.json").json()
    return schema


def test_app_serves_exactly_the_contract_routes(
    openapi: dict[str, dict[str, dict[str, object]]],
) -> None:
    served = {(method.upper(), path) for path, ops in openapi["paths"].items() for method in ops}
    assert served == CONTRACT_ROUTES


def test_every_contract_route_is_documented() -> None:
    doc = (REPO_ROOT / "docs" / "contracts.md").read_text()
    undocumented = [f"{m} {p}" for m, p in sorted(CONTRACT_ROUTES) if f"`{m} {p}`" not in doc]
    assert undocumented == []


def test_every_contract_model_reaches_the_frontend(
    openapi: dict[str, dict[str, dict[str, object]]],
) -> None:
    """Generated TypeScript only includes schemas some route uses."""
    contract_models = {
        name
        for name, obj in inspect.getmembers(models, inspect.isclass)
        if issubclass(obj, models.Contract) and obj is not models.Contract
    }
    assert contract_models - set(openapi["components"]["schemas"]) == set()
