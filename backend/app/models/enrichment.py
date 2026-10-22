"""F4 contracts: grounded enrichment proposals and the merchant's approval."""

from datetime import datetime
from typing import Self

from pydantic import Field, model_validator

from app.models.base import AttributeValue, Contract
from app.models.enums import ApprovalDecision, ProposalStatus, SourceField


class GroundingSpan(Contract):
    """Exact source text a proposed value came from; the validator checks it against the product.

    Offsets count Unicode code points (Python string indexing). The grid converts them before
    slicing JavaScript strings, which count UTF-16 units.
    """

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
    merchant_supplied: bool = Field(
        default=False, description="True when new_value was typed by the merchant on approval."
    )
    status: ProposalStatus = ProposalStatus.PENDING
    rationale: str = ""

    @model_validator(mode="after")
    def _grounding_rule(self) -> Self:
        if self.grounded and not self.spans:
            raise ValueError("a grounded proposal must cite at least one source span")
        approved = self.status is ProposalStatus.APPROVED
        if approved and not self.grounded and not self.merchant_supplied:
            raise ValueError("an ungrounded proposal can only be approved with a merchant value")
        return self


class ProposalRequest(Contract):
    product_ids: list[str] = Field(default_factory=list, description="Empty means all products.")


class ApprovalRequest(Contract):
    proposal_ids: list[str] = Field(min_length=1)
    decision: ApprovalDecision
    merchant_values: dict[str, AttributeValue] = Field(
        default_factory=dict,
        description="Merchant-typed values for 'needs merchant input' proposals, by ID.",
    )

    @model_validator(mode="after")
    def _merchant_values_match_proposals(self) -> Self:
        if self.merchant_values and self.decision is not ApprovalDecision.APPROVE:
            raise ValueError("merchant values only make sense when approving")
        unknown = set(self.merchant_values) - set(self.proposal_ids)
        if unknown:
            raise ValueError(
                f"merchant values for proposals not in this request: {sorted(unknown)}"
            )
        return self


class Approval(Contract):
    id: str
    proposal_ids: list[str]
    decision: ApprovalDecision
    decided_at: datetime
    paypal_synced_product_ids: list[str] = Field(default_factory=list)
    benchmark_run_id: str | None = None
