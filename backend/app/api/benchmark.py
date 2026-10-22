"""F2: Agent Visibility benchmark over shopper intents and Channel3 competitors."""

from fastapi import APIRouter, status

from app.api.deps import not_built
from app.models import BenchmarkRequest, BenchmarkRun, IntentResult, QuerySplit, ShopperIntent

router = APIRouter(prefix="/api", tags=["benchmark"])


@router.get("/intents")
def list_intents(split: QuerySplit | None = None) -> list[ShopperIntent]:
    not_built("03")


@router.post("/benchmark/runs", status_code=status.HTTP_201_CREATED)
def create_benchmark_run(request: BenchmarkRequest) -> BenchmarkRun:
    """Rank merchant products against competitors for every intent in the split."""
    not_built("04")


@router.get("/benchmark/runs")
def list_benchmark_runs() -> list[BenchmarkRun]:
    not_built("04")


@router.get("/benchmark/runs/{run_id}")
def get_benchmark_run(run_id: str) -> BenchmarkRun:
    not_built("04")


@router.get("/benchmark/runs/{run_id}/intents/{intent_id}")
def get_intent_result(run_id: str, intent_id: str) -> IntentResult:
    """The ranked shelf one query produced in this run."""
    not_built("04")
