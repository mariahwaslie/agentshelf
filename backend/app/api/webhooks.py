"""PayPal webhooks: signature-verified, processed once per event ID."""

from fastapi import APIRouter, Request

from app.api.deps import not_built
from app.models import WebhookAck

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request) -> WebhookAck:
    """Async because signature verification needs the raw request body."""
    not_built("06")
