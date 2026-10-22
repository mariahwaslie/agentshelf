from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models import AgentOrder, GroundingSpan, Money, OrderStatus, ProductAttributes, SourceField


def test_grounding_span_must_match_its_text() -> None:
    span = GroundingSpan(source_field=SourceField.DESCRIPTION, start=10, end=20, text="waterproof")
    assert span.text == "waterproof"
    with pytest.raises(ValidationError, match="span bounds"):
        GroundingSpan(source_field=SourceField.DESCRIPTION, start=10, end=15, text="waterproof")


def test_grounding_span_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="span bounds"):
        GroundingSpan(source_field=SourceField.NOTES, start=5, end=5, text="")


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


def test_order_is_not_agent_sourced_until_capture_is_confirmed() -> None:
    order = AgentOrder(
        id="ord_1",
        paypal_order_id="5O190127TN364715T",
        recommendation_id="rec_1",
        product_id="boot-1",
        query="waterproof boots",
        amount=Money(amount_cents=11900),
        status=OrderStatus.CREATED,
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
    )
    assert order.source is None
    assert order.confirmed_by is None
