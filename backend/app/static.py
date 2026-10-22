"""Serves the built React app at /, so the whole product is one service at one URL."""

from pathlib import Path

from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

# Unknown API paths must stay 404s, not quietly become the app's HTML page.
_BACKEND_PREFIXES = ("api/", "webhooks/", "health")


class SpaStaticFiles(StaticFiles):
    """Unknown paths fall back to index.html so client-side routes survive a page refresh."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404 or path.startswith(_BACKEND_PREFIXES):
                raise
            return await super().get_response("index.html", scope)


def mount_frontend(app: FastAPI, dist: Path) -> None:
    """Mount only once `npm run build` has produced dist/; in development Vite serves the UI."""
    if (dist / "index.html").is_file():
        app.mount("/", SpaStaticFiles(directory=dist, html=True), name="frontend")
