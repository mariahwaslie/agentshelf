"""Dashboard, API Trace, health/config and feed contracts."""

from datetime import datetime
from typing import Literal

from pydantic import Field, JsonValue

from app.models.base import Contract, Money
from app.models.benchmark import ProductScore
from app.models.catalog import Product
from app.models.enums import AppMode, CacheOutcome, Service, ServiceState


class ScorePoint(Contract):
    run_id: str
    created_at: datetime
    visibility_score: float


class CategoryShare(Contract):
    category: str
    share_of_shelf: float = Field(ge=0, le=1)


class DashboardSummary(Contract):
    visibility_history: list[ScorePoint]
    share_by_category: list[CategoryShare]
    agent_revenue: Money
    other_revenue: Money
    other_revenue_synthetic: bool = Field(
        description="True while other_revenue comes from the seeded synthetic order history."
    )
    agent_order_count: int
    most_invisible: list[ProductScore]


class TraceEvent(Contract):
    """One external call, shown in the API Trace panel. Never holds secrets or auth headers."""

    seq: int = Field(ge=1)
    ts: datetime
    service: Service
    method: str
    endpoint: str
    status_code: int | None = None
    duration_ms: float = Field(ge=0)
    cache: CacheOutcome
    sandbox_ids: dict[str, str] = Field(default_factory=dict)
    error: str | None = None
    request_id: str | None = None


class HealthStatus(Contract):
    status: Literal["ok"] = "ok"
    mode: AppMode
    version: str
    services: dict[Service, ServiceState]


class FeatureFlags(Contract):
    studio_agent: bool
    ag_studio: bool
    shipment_tracking: bool
    feed_export: bool
    pick_model: bool


class AppConfig(Contract):
    """What the browser needs at startup. Both IDs below are public by design (they ship to the
    browser in any PayPal JS SDK / AG Grid Enterprise page); the PayPal secret never leaves the
    server."""

    mode: AppMode
    display_anonymized: bool
    features: FeatureFlags
    paypal_client_id: str | None = None
    ag_license_key: str | None = None


class ResetResult(Contract):
    products: int


class AgentFeed(Contract):
    generated_at: datetime
    store_name: str
    products: list[Product]


JsonLdDocument = dict[str, JsonValue]
