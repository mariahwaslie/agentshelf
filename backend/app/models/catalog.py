"""F1 contracts: the merchant's products and the competitor listings they're ranked against."""

from datetime import datetime

from pydantic import Field

from app.models.base import Contract, Money


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
    """A live listing from Channel3. Anonymization is applied server-side (docs/contracts.md)."""

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
