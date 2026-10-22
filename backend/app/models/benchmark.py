"""F2/F3 contracts: shopper intents, the ranker's output, benchmark runs, and fixes."""

from collections.abc import Sequence
from datetime import datetime
from itertools import pairwise
from typing import Self

from pydantic import Field, model_validator

from app.models.base import AttributeValue, Contract, Money
from app.models.catalog import Competitor
from app.models.enums import AppMode, FixKind, ItemOwner, QuerySplit


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


def check_ranking(ranked: Sequence[RankedItem]) -> None:
    """A ranking runs 1..n with scores never rising: the shape only a real ranker produces."""
    if [item.rank for item in ranked] != list(range(1, len(ranked) + 1)):
        raise ValueError("ranks must run 1..n in order")
    if any(later.score > earlier.score for earlier, later in pairwise(ranked)):
        raise ValueError("scores must not increase down the ranking")


class CallProvenance(Contract):
    """Where a result's external data came from, so reused recordings are never shown as live."""

    live_calls: int = Field(default=0, ge=0)
    reused_recordings: int = Field(default=0, ge=0, description="Live mode served a recording.")
    replayed_calls: int = Field(default=0, ge=0)
    oldest_recording_at: datetime | None = None


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
    provenance: CallProvenance
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

    @model_validator(mode="after")
    def _ranked_by_the_ranker(self) -> Self:
        check_ranking(self.ranked)
        return self


class Fix(Contract):
    product_id: str
    kind: FixKind
    attribute: str | None = None
    message: str
    estimated_impact: float
    rank: int = Field(ge=1)
