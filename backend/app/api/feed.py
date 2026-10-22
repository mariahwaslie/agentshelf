"""Feed export (FEATURE_FEED_EXPORT): schema.org Product JSON-LD and an agent-feed file."""

from fastapi import APIRouter

from app.api.deps import not_built
from app.models import AgentFeed, JsonLdDocument

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("/jsonld")
def export_jsonld() -> list[JsonLdDocument]:
    not_built("07")


@router.get("/agent.json")
def export_agent_feed() -> AgentFeed:
    not_built("07")
