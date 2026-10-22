"""FastAPI app factory: API routes, request IDs, and the built React app at /.

Run with `uvicorn --factory app.main:create_app` so importing this module has no side effects.
"""

import re
import time
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app import __version__
from app.api import ROUTERS
from app.log import configure_logging, get_logger
from app.settings import Settings, get_settings
from app.static import mount_frontend

_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9-]{1,64}$")
_QUIET_PATHS = frozenset({"/health", "/api/trace"})

log = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(json_logs=settings.log_json)
    app = FastAPI(
        title="AgentShelf API",
        version=__version__,
        separate_input_output_schemas=False,
        generate_unique_id_function=_operation_id,
    )
    app.state.settings = settings
    app.add_middleware(BaseHTTPMiddleware, dispatch=_request_context)
    for router in ROUTERS:
        app.include_router(router)
    mount_frontend(app, settings.frontend_dist)
    return app


def _operation_id(route: APIRoute) -> str:
    """Use the handler name, so generated TypeScript reads `getProduct`, not `get_product_api_…`."""
    return route.name


async def _request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Tag every log line and response with a request ID (the client's, if well-formed)."""
    incoming = request.headers.get("x-request-id", "")
    request_id = incoming if _VALID_REQUEST_ID.match(incoming) else uuid4().hex
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    if request.url.path not in _QUIET_PATHS:
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 1),
        )
    return response
