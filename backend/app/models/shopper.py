"""F5 contracts: the shopper agent's recommendation and the PayPal order it starts."""

from datetime import datetime
from typing import Self

from pydantic import Field, model_validator

from app.models.base import Contract, Money
from app.models.benchmark import CallProvenance, RankedItem, ShopperIntent, check_ranking
from app.models.enums import CaptureStatus, Confirmation, OrderSource, OrderStatus


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
    provenance: CallProvenance

    @model_validator(mode="after")
    def _pick_is_the_rankers_first(self) -> Self:
        check_ranking(self.ranked)
        expected = self.ranked[0] if self.ranked else None
        if self.pick != expected:
            raise ValueError("pick must be the ranker's first item: the ranker decides")
        return self


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
    capture_status: CaptureStatus | None = None
    source: OrderSource | None = None
    confirmed_by: Confirmation | None = None
    webhook_event_id: str | None = None
    created_at: datetime
    captured_at: datetime | None = None

    @model_validator(mode="after")
    def _revenue_is_tagged_only_after_a_real_capture(self) -> Self:
        if (self.capture_id is None) != (self.capture_status is None):
            raise ValueError("capture_id and capture_status come together")
        if self.capture_id is not None and self.status is not OrderStatus.COMPLETED:
            raise ValueError("a capture only exists on a COMPLETED order")
        if (self.source is None) != (self.confirmed_by is None):
            raise ValueError("source and confirmed_by are set together")
        if self.source is not None and self.capture_status is not CaptureStatus.COMPLETED:
            raise ValueError("revenue is agent-sourced only once its capture is COMPLETED")
        if self.confirmed_by is Confirmation.WEBHOOK and self.webhook_event_id is None:
            raise ValueError("webhook confirmation needs the webhook event ID")
        return self


class WebhookAck(Contract):
    event_id: str
    processed: bool = Field(description="False when this event ID was already handled.")
