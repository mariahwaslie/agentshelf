"""Record/replay cache interface. The httpx transport that uses it lands in prompt 02."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from pydantic import JsonValue

from app.cache.keys import FixtureKey
from app.models import AppMode


class CacheMode(StrEnum):
    REPLAY = "replay"
    """Serve fixtures only. A missing fixture raises FixtureMissingError, never a live call."""

    CACHE_FIRST = "cache_first"
    """Live: reuse a fixture when one exists, else call the service and record the response."""

    REFRESH = "refresh"
    """Live with RECORD=1: always call the service and overwrite the fixture."""


def cache_mode_for(app_mode: AppMode, *, record: bool) -> CacheMode:
    """Writes (PayPal order create/capture, catalog PATCH) always go live outside replay;
    the transport enforces that per request, whatever this mode says."""
    if app_mode is AppMode.REPLAY:
        return CacheMode.REPLAY
    return CacheMode.REFRESH if record else CacheMode.CACHE_FIRST


@dataclass(frozen=True)
class Fixture:
    key: FixtureKey
    status_code: int
    body: JsonValue
    recorded_at: datetime
    headers: dict[str, str]
    """Allow-listed response headers only (e.g. content-type); never auth or cookies."""


class FixtureMissingError(LookupError):
    """Replay mode asked for a request that was never recorded."""

    def __init__(self, key: FixtureKey) -> None:
        super().__init__(f"No fixture for {key.service} {key.operation} ({key.relative_path})")
        self.key = key


class FixtureStore(Protocol):
    def get(self, key: FixtureKey) -> Fixture | None: ...

    def put(self, fixture: Fixture) -> None: ...
