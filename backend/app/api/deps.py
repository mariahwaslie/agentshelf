"""Shared route dependencies."""

from typing import Annotated, NoReturn

from fastapi import Depends, HTTPException, Request, status

from app.settings import Settings


def app_settings(request: Request) -> Settings:
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise TypeError("create_app() must attach Settings to app.state")
    return settings


SettingsDep = Annotated[Settings, Depends(app_settings)]


def not_built(prompt: str) -> NoReturn:
    """Contract stub: the route is in OpenAPI now; its behavior lands in the named prompt."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail=f"Not built yet (prompt {prompt})")
