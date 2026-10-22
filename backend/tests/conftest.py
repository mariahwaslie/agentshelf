"""Shared fixtures. Tests never read the developer's .env and never touch the network."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import AppMode
from app.settings import Settings


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop any setting exported in the shell so each test states exactly what it needs."""
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(_env_file=None, app_mode=AppMode.REPLAY, frontend_dist=tmp_path / "no-dist")


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if os.environ.get("LIVE_TESTS") == "1":
        return
    skip_live = pytest.mark.skip(reason="calls the real sandbox; set LIVE_TESTS=1 to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
