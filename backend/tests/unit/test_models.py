from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from app.models import (
    AgentOrder,
    ApprovalRequest,
    EnrichmentProposal,
    GroundingSpan,
    Money,
    ProductAttributes,
    ShopperRecommendation,
    SourceField,
)

PRICE = {"amount_cents": 11900}
INTENT = {"id": "i1", "query": "wide boots", "category": "boots", "split": "heldout"}
NO_CALLS: dict[str, int] = {}


def ranked(*scores: float) -> list[dict[str, Any]]:
    return [
        {"rank": i, "owner": "merchant", "item_id": f"p{i}", "title": "Boot", "price": PRICE}
        | {"score": score}
        for i, score in enumerate(scores, start=1)
    ]


def recommendation(**overrides: Any) -> ShopperRecommendation:
    fields: dict[str, Any] = {
        "id": "rec_1",
        "query": "wide boots",
        "intent": INTENT,
        "ranked": ranked(0.9, 0.7),
        "pick": ranked(0.9, 0.7)[0],
        "explanation": "Widest fit under budget.",
        "provenance": NO_CALLS,
    }
    return ShopperRecommendation.model_validate(fields | overrides)


def order(**overrides: Any) -> AgentOrder:
    fields: dict[str, Any] = {
        "id": "ord_1",
        "paypal_order_id": "5O190127TN364715T",
        "recommendation_id": "rec_1",
        "product_id": "boot-1",
        "query": "waterproof boots",
        "amount": PRICE,
        "status": "CREATED",
        "created_at": datetime(2026, 11, 1, tzinfo=UTC),
    }
    return AgentOrder.model_validate(fields | overrides)


CAPTURED = {"status": "COMPLETED", "capture_id": "CAP1", "capture_status": "COMPLETED"}


# --- Grounding --------------------------------------------------------------------------------


def test_grounding_span_must_match_its_text() -> None:
    span = GroundingSpan(source_field=SourceField.DESCRIPTION, start=10, end=20, text="waterproof")
    assert span.text == "waterproof"
    with pytest.raises(ValidationError, match="span bounds"):
        GroundingSpan(source_field=SourceField.DESCRIPTION, start=10, end=15, text="waterproof")


def test_grounding_span_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="span bounds"):
        GroundingSpan(source_field=SourceField.NOTES, start=5, end=5, text="")


def test_grounded_proposal_must_cite_a_span() -> None:
    with pytest.raises(ValidationError, match="at least one source span"):
        EnrichmentProposal(id="e1", product_id="p1", field="fit", new_value="wide", grounded=True)


def test_ungrounded_proposal_is_approved_only_with_a_merchant_value() -> None:
    base: dict[str, Any] = {"id": "e1", "product_id": "p1", "field": "fit", "new_value": "wide"}
    with pytest.raises(ValidationError, match="merchant value"):
        EnrichmentProposal.model_validate(base | {"grounded": False, "status": "approved"})
    approved = EnrichmentProposal.model_validate(
        base | {"grounded": False, "status": "approved", "merchant_supplied": True}
    )
    assert approved.merchant_supplied


def test_merchant_values_must_belong_to_the_request() -> None:
    with pytest.raises(ValidationError, match="not in this request"):
        ApprovalRequest(proposal_ids=["e1"], decision="approve", merchant_values={"e2": "wide"})
    with pytest.raises(ValidationError, match="only make sense when approving"):
        ApprovalRequest(proposal_ids=["e1"], decision="reject", merchant_values={"e1": "wide"})


# --- Ranker decides ---------------------------------------------------------------------------


def test_pick_must_be_the_rankers_first_item() -> None:
    assert recommendation().pick is not None
    with pytest.raises(ValidationError, match="ranker's first item"):
        recommendation(pick=ranked(0.9, 0.7)[1])


def test_no_pick_only_when_nothing_ranked() -> None:
    assert recommendation(ranked=[], pick=None).pick is None
    with pytest.raises(ValidationError, match="ranker's first item"):
        recommendation(pick=None)


def test_ranking_must_be_ordered_by_score() -> None:
    with pytest.raises(ValidationError, match="must not increase"):
        recommendation(ranked=ranked(0.5, 0.9), pick=ranked(0.5, 0.9)[0])
    bad_ranks = ranked(0.9, 0.7)
    bad_ranks[1]["rank"] = 3
    with pytest.raises(ValidationError, match=r"1\.\.n"):
        recommendation(ranked=bad_ranks, pick=bad_ranks[0])


# --- Agent-sourced revenue --------------------------------------------------------------------


def test_new_order_is_not_agent_sourced() -> None:
    assert order().source is None


def test_cannot_tag_revenue_before_capture_completes() -> None:
    with pytest.raises(ValidationError, match=r"set together|COMPLETED"):
        order(source="agent", confirmed_by="polling")
    pending = CAPTURED | {"capture_status": "PENDING"}
    with pytest.raises(ValidationError, match="capture is COMPLETED"):
        order(**pending, source="agent", confirmed_by="polling")


def test_webhook_confirmation_needs_the_event_id() -> None:
    with pytest.raises(ValidationError, match="webhook event ID"):
        order(**CAPTURED, source="agent", confirmed_by="webhook")
    tagged = order(**CAPTURED, source="agent", confirmed_by="webhook", webhook_event_id="WH-1")
    assert tagged.source == "agent"


def test_capture_only_on_completed_order() -> None:
    with pytest.raises(ValidationError, match="COMPLETED order"):
        order(status="APPROVED", capture_id="CAP1", capture_status="COMPLETED")
    with pytest.raises(ValidationError, match="come together"):
        order(status="COMPLETED", capture_id="CAP1")


def test_paypal_payer_action_required_status_is_accepted() -> None:
    assert order(status="PAYER_ACTION_REQUIRED").status == "PAYER_ACTION_REQUIRED"


# --- Basics -----------------------------------------------------------------------------------


def test_money_rejects_negative_and_bad_currency() -> None:
    assert Money(amount_cents=11900).currency == "USD"
    with pytest.raises(ValidationError):
        Money(amount_cents=-1)
    with pytest.raises(ValidationError):
        Money(amount_cents=100, currency="usd")


def test_contract_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="extra"):
        Money.model_validate({"amount_cents": 100, "cents": 100})


def test_attribute_lists_are_not_shared_between_instances() -> None:
    first = ProductAttributes()
    first.sizes.append("10W")
    assert ProductAttributes().sizes == []
