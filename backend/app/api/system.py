"""Health, frontend config, demo reset, and the API Trace feed."""

from fastapi import APIRouter, Query

from app import __version__
from app.api.deps import SettingsDep, not_built
from app.models import AppConfig, HealthStatus, ResetResult, TraceEvent

router = APIRouter(tags=["system"])


@router.get("/health")
def health(settings: SettingsDep) -> HealthStatus:
    return HealthStatus(
        mode=settings.app_mode, version=__version__, services=settings.service_states()
    )


@router.get("/api/config")
def get_config(settings: SettingsDep) -> AppConfig:
    return AppConfig(
        mode=settings.app_mode,
        display_anonymized=settings.display_anonymized,
        features=settings.features,
        paypal_client_id=settings.paypal_client_id,
        ag_license_key=settings.ag_license_key,
    )


@router.post("/api/demo/reset")
def reset_demo() -> ResetResult:
    """Restore the seeded "before" state so the demo can be run again from the start."""
    not_built("03")


@router.get("/api/trace")
def list_trace(after: int = Query(default=0, ge=0)) -> list[TraceEvent]:
    """Events with seq > after. The trace panel polls this about once a second."""
    not_built("02")
