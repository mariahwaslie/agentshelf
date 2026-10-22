"""API contract models, shared by every route and mirrored to TypeScript via OpenAPI.

These are fixed: changing a field here needs a decision record in docs/decisions/.
Database tables live in app/db/ and are mapped to these models; storage can change freely.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class Contract(BaseModel):
    """Base for every contract model. Unknown fields are rejected so drift fails loudly."""

    model_config = ConfigDict(extra="forbid")


# --- Enums -----------------------------------------------------------------------------------


class AppMode(StrEnum):
    LIVE = "live"
    REPLAY = "replay"


class Service(StrEnum):
    PAYPAL = "paypal"
    CHANNEL3 = "channel3"
    LLM = "llm"
    EMBEDDINGS = "embeddings"


class ServiceState(StrEnum):
    CONFIGURED = "configured"
    MISSING_KEYS = "missing_keys"
    REPLAY = "replay"
    LOCAL = "local"


class QuerySplit(StrEnum):
    TRAIN = "train"
    HELDOUT = "heldout"


class ItemOwner(StrEnum):
    MERCHANT = "merchant"
    COMPETITOR = "competitor"


class FixKind(StrEnum):
    MISSING_ATTRIBUTE = "missing_attribute"
    THIN_DESCRIPTION = "thin_description"
    PRICE_OUTLIER = "price_outlier"
    AVAILABILITY = "availability"


class SourceField(StrEnum):
    """Product text an enrichment proposal is allowed to cite."""

    TITLE = "title"
    DESCRIPTION = "description"
    NOTES = "notes"


class ProposalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class OrderStatus(StrEnum):
    """Mirrors PayPal Orders v2 statuses."""

    CREATED = "CREATED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    VOIDED = "VOIDED"


class OrderSource(StrEnum):
    AGENT = "agent"


class Confirmation(StrEnum):
    """How a capture was confirmed: the webhook, or the order-status polling fallback."""

    WEBHOOK = "webhook"
    POLLING = "polling"


class CacheOutcome(StrEnum):
    HIT = "hit"
    MISS = "miss"
    RECORDED = "recorded"
    REPLAYED = "replayed"


# Attribute values are kept JSON-simple so the approval grid can render and diff them.
AttributeValue = str | int | bool | list[str]


# --- Catalog ---------------------------------------------------------------------------------


class Money(Contract):
    """Integer cents avoid float rounding; PayPal's decimal strings are built at the client edge."""

    amount_cents: int = Field(ge=0)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")


class ProductAttributes(Contract):
    """Structured attributes agents filter on. PayPal Catalog can't hold these, so we do."""

    material: str | None = None
    waterproof: bool | None = None
    waterproof_rating: str | None = None
    fit: str | None = None
    use_cases: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    weight_grams: int | None = Field(default=None, ge=0)
    gender: str | None = None
    season: str | None = None
    extra: dict[str, str] = Field(default_factory=dict)


class Product(Contract):
    id: str
    sku: str
    title: str
    description: str
    notes: str = ""
    category: str
    price: Money
    in_stock: bool = True
    image_url: str | None = None
    attributes: ProductAttributes = Field(default_factory=ProductAttributes)
    paypal_product_id: str | None = None
    updated_at: datetime


class Competitor(Contract):
    """A live listing from Channel3.

    When DISPLAY_ANONYMIZED is on, the server replaces brand with "Competitor A/B/C", scrubs the
    brand from the title, and drops the URL, so real brands never reach the browser.
    """

    id: str
    channel3_id: str
    title: str
    brand: str
    description: str = ""
    price: Money
    in_stock: bool = True
    url: str | None = None
    attributes: ProductAttributes = Field(default_factory=ProductAttributes)
    anonymized: bool
    fetched_at: datetime


class ImportResult(Contract):
    created: int
    updated: int
    product_ids: list[str]


class SyncResult(Contract):
    """Outcome of pushing products to the PayPal Catalog Products API."""

    created: int
    updated: int
    paypal_product_ids: dict[str, str]


# --- Benchmark and diagnosis -----------------------------------------------------------------


class ShopperIntent(Contract):
    id: str
    query: str
    category: str
    price_max: Money | None = None
    required_attributes: dict[str, AttributeValue] = Field(default_factory=dict)
    split: QuerySplit


class RankedItem(Contract):
    rank: int = Field(ge=1)
    owner: ItemOwner
    item_id: str
    title: str
    price: Money
    score: float


class BenchmarkRequest(Contract):
    split: QuerySplit = QuerySplit.HELDOUT
    k: int = Field(default=5, ge=1, le=20)


class ProductScore(Contract):
    product_id: str
    queries_considered: int
    top_k_appearances: int
    mean_rank: float | None = None
    top_competitor_id: str | None = None


class BenchmarkRun(Contract):
    """One benchmark pass. Metric definitions: docs/EVALUATION.md."""

    id: str
    created_at: datetime
    catalog_version: str
    split: QuerySplit
    k: int
    n_queries: int
    mode: AppMode
    visibility_score: float = Field(ge=0, le=100)
    share_of_shelf: float = Field(ge=0, le=1)
    recall_at_k: float = Field(ge=0, le=1)
    mean_best_rank: float | None = None
    baseline_share_of_shelf: float = Field(ge=0, le=1)
    baseline_recall_at_k: float = Field(ge=0, le=1)
    product_scores: list[ProductScore] = Field(default_factory=list)


class IntentResult(Contract):
    """The ranked shelf for one query within a benchmark run, with the competitor listings on it."""

    run_id: str
    intent: ShopperIntent
    ranked: list[RankedItem]
    competitors: list[Competitor]


class Fix(Contract):
    product_id: str
    kind: FixKind
    attribute: str | None = None
    message: str
    estimated_impact: float
    rank: int = Field(ge=1)


# --- Enrichment and approval -----------------------------------------------------------------


class GroundingSpan(Contract):
    """Exact source text a proposed value came from; the validator checks it against the product."""

    source_field: SourceField
    start: int = Field(ge=0)
    end: int
    text: str

    @model_validator(mode="after")
    def _span_matches_text(self) -> Self:
        if self.end <= self.start or self.end - self.start != len(self.text):
            raise ValueError("span bounds must be non-empty and match the length of text")
        return self


class EnrichmentProposal(Contract):
    """A suggested change. Ungrounded ones show as "needs merchant input" and never auto-apply."""

    id: str
    product_id: str
    field: str
    old_value: AttributeValue | None = None
    new_value: AttributeValue
    spans: list[GroundingSpan] = Field(default_factory=list)
    grounded: bool
    status: ProposalStatus = ProposalStatus.PENDING
    rationale: str = ""


class ProposalRequest(Contract):
    product_ids: list[str] = Field(default_factory=list, description="Empty means all products.")


class ApprovalRequest(Contract):
    proposal_ids: list[str] = Field(min_length=1)
    decision: ApprovalDecision


class Approval(Contract):
    id: str
    proposal_ids: list[str]
    decision: ApprovalDecision
    decided_at: datetime
    paypal_synced_product_ids: list[str] = Field(default_factory=list)
    benchmark_run_id: str | None = None


# --- Shopper agent and orders ----------------------------------------------------------------


class ShopperRequest(Contract):
    query: str = Field(min_length=3, max_length=300)


class ShopperRecommendation(Contract):
    """The ranker's pick for a request. The LLM writes `explanation`; it never chooses `pick`."""

    id: str
    query: str
    intent: ShopperIntent
    pick: RankedItem | None = None
    ranked: list[RankedItem]
    explanation: str


class CreateOrderRequest(Contract):
    recommendation_id: str


class AgentOrder(Contract):
    """A PayPal order started by the shopper agent. `source` is set once capture is confirmed."""

    id: str
    paypal_order_id: str
    recommendation_id: str
    product_id: str
    query: str
    amount: Money
    status: OrderStatus
    capture_id: str | None = None
    source: OrderSource | None = None
    confirmed_by: Confirmation | None = None
    webhook_event_id: str | None = None
    created_at: datetime
    captured_at: datetime | None = None


class WebhookAck(Contract):
    event_id: str
    processed: bool = Field(description="False when this event ID was already handled.")


# --- Dashboard -------------------------------------------------------------------------------


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
    agent_order_count: int
    most_invisible: list[ProductScore]


# --- System, trace, feed ---------------------------------------------------------------------


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
    """What the browser needs at startup. The PayPal client ID is public by design (JS SDK)."""

    mode: AppMode
    display_anonymized: bool
    features: FeatureFlags
    paypal_client_id: str | None = None


class ResetResult(Contract):
    products: int


class AgentFeed(Contract):
    generated_at: datetime
    store_name: str
    products: list[Product]


JsonLdDocument = dict[str, JsonValue]
