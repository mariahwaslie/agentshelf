"""HTTP routes, one router per product area. Every route is listed in docs/contracts.md."""

from fastapi import APIRouter

from app.api import (
    benchmark,
    catalog,
    dashboard,
    diagnosis,
    enrichment,
    feed,
    shopper,
    system,
    webhooks,
)

ROUTERS: tuple[APIRouter, ...] = (
    system.router,
    catalog.router,
    benchmark.router,
    diagnosis.router,
    enrichment.router,
    shopper.router,
    webhooks.router,
    dashboard.router,
    feed.router,
)
