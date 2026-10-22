"""F6: Agent Channel dashboard data."""

from fastapi import APIRouter

from app.api.deps import not_built
from app.models import DashboardSummary

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard() -> DashboardSummary:
    not_built("07")
