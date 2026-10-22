"""Shared building blocks for every contract model."""

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    """Base for every contract model. Unknown fields are rejected so drift fails loudly."""

    model_config = ConfigDict(extra="forbid")


# Attribute values are kept JSON-simple so the approval grid can render and diff them.
AttributeValue = str | int | bool | list[str]


class Money(Contract):
    """Integer cents avoid float rounding; PayPal's decimal strings are built at the client edge."""

    amount_cents: int = Field(ge=0)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
