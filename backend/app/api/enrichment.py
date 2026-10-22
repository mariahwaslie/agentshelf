"""F4: grounded enrichment proposals and merchant approval."""

from fastapi import APIRouter

from app.api.deps import not_built
from app.models import (
    Approval,
    ApprovalRequest,
    EnrichmentProposal,
    ProposalRequest,
    ProposalStatus,
)

router = APIRouter(prefix="/api/enrichment", tags=["enrichment"])


@router.post("/proposals")
def create_proposals(request: ProposalRequest) -> list[EnrichmentProposal]:
    """Extract attributes from each product's own text; every value must cite its source span."""
    not_built("05")


@router.get("/proposals")
def list_proposals(status: ProposalStatus | None = None) -> list[EnrichmentProposal]:
    not_built("05")


@router.post("/approvals")
def decide_proposals(request: ApprovalRequest) -> Approval:
    """Apply approved changes to the DB and PayPal Catalog, then re-run the benchmark."""
    not_built("05")
