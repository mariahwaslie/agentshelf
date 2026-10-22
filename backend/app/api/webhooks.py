"""PayPal webhooks: signature-verified, processed once per event ID.

Unsigned or unverifiable events get a 400 and change nothing (docs/contracts.md).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import not_built
from app.models import WebhookAck

router = APIRouter(tags=["webhooks"])


async def raw_body(request: Request) -> bytes:
    """The exact bytes PayPal signed; re-serialized JSON would not verify."""
    return await request.body()


@router.post("/webhooks/paypal")
def paypal_webhook(request: Request, body: Annotated[bytes, Depends(raw_body)]) -> WebhookAck:
    """Sync on purpose: verification calls PayPal through the sync client in FastAPI's threadpool,
    so a slow PayPal response never blocks the event loop."""
    not_built("06")
