"""F5: shopper agent recommendation and PayPal Orders v2 checkout."""

from fastapi import APIRouter, status

from app.api.deps import not_built
from app.models import AgentOrder, CreateOrderRequest, ShopperRecommendation, ShopperRequest

router = APIRouter(prefix="/api", tags=["shopper"])


@router.post("/shopper/recommend")
def recommend(request: ShopperRequest) -> ShopperRecommendation:
    """The benchmark's ranker picks; the LLM only explains the pick."""
    not_built("06")


@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(request: CreateOrderRequest) -> AgentOrder:
    """Create a PayPal order for a recommendation. The buyer approves it in the browser."""
    not_built("06")


@router.get("/orders")
def list_orders() -> list[AgentOrder]:
    not_built("06")


@router.get("/orders/{order_id}")
def get_order(order_id: str) -> AgentOrder:
    """Also refreshes status from PayPal: the polling fallback when a webhook is late."""
    not_built("06")


@router.post("/orders/{order_id}/capture")
def capture_order(order_id: str) -> AgentOrder:
    not_built("06")
