"""Record/replay cache interface. The httpx transport that uses it lands in prompt 02.

Two things decide what happens to a call: the app-wide CacheMode, and the CallPolicy of the
operation being called. `cache_action` combines them; the transport just follows the result.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from pydantic import JsonValue

from app.cache.keys import FixtureKey
from app.models import AppMode

# Response body fields that hold credentials. Replaced before a fixture exists, so they can
# never be written to data/fixtures/ (which is committed to git).
SECRET_BODY_FIELDS = frozenset(
    {"access_token", "refresh_token", "id_token", "client_secret", "api_key", "nonce"}
)
REDACTED = "[redacted]"

# Response headers worth keeping for replay. Everything else (cookies, auth, debug IDs) is dropped.
ALLOWED_HEADERS = frozenset({"content-type"})


class CacheMode(StrEnum):
    REPLAY = "replay"
    """APP_MODE=replay: no network at all."""

    CACHE_FIRST = "cache_first"
    """APP_MODE=live: reusable reads may come from a recording."""

    REFRESH = "refresh"
    """APP_MODE=live with RECORD=1: re-record everything reusable."""


class CallPolicy(StrEnum):
    REUSABLE = "reusable"
    """Deterministic reads whose answer doesn't change under us: Channel3 search, LLM at
    temperature 0, embeddings."""

    ALWAYS_LIVE = "always_live"
    """Every PayPal call: writes, and reads that must reflect current state (order status for
    the polling fallback, catalog GET as proof of an update, webhook signature verification)."""

    NEVER_RECORD = "never_record"
    """Credential exchanges (the PayPal OAuth token). Never written to a fixture."""


class CacheAction(StrEnum):
    SERVE_FIXTURE = "serve_fixture"
    """Serve the recording; a missing one raises FixtureMissingError, never a live call."""

    STUB = "stub"
    """Replay of a credential call: don't call; the client substitutes a placeholder token."""

    REUSE_OR_RECORD = "reuse_or_record"
    """Serve the recording if one exists (traced as a hit), else call and record."""

    CALL_AND_RECORD = "call_and_record"
    """Always call; save the (redacted) response so replay mode can serve it."""

    CALL_ONLY = "call_only"
    """Always call; save nothing."""


_ACTIONS: dict[CacheMode, dict[CallPolicy, CacheAction]] = {
    CacheMode.REPLAY: {
        CallPolicy.REUSABLE: CacheAction.SERVE_FIXTURE,
        CallPolicy.ALWAYS_LIVE: CacheAction.SERVE_FIXTURE,
        CallPolicy.NEVER_RECORD: CacheAction.STUB,
    },
    CacheMode.CACHE_FIRST: {
        CallPolicy.REUSABLE: CacheAction.REUSE_OR_RECORD,
        CallPolicy.ALWAYS_LIVE: CacheAction.CALL_AND_RECORD,
        CallPolicy.NEVER_RECORD: CacheAction.CALL_ONLY,
    },
    CacheMode.REFRESH: {
        CallPolicy.REUSABLE: CacheAction.CALL_AND_RECORD,
        CallPolicy.ALWAYS_LIVE: CacheAction.CALL_AND_RECORD,
        CallPolicy.NEVER_RECORD: CacheAction.CALL_ONLY,
    },
}


def cache_mode_for(app_mode: AppMode, *, record: bool) -> CacheMode:
    if app_mode is AppMode.REPLAY:
        return CacheMode.REPLAY
    return CacheMode.REFRESH if record else CacheMode.CACHE_FIRST


def cache_action(mode: CacheMode, policy: CallPolicy) -> CacheAction:
    return _ACTIONS[mode][policy]


def redact(body: JsonValue) -> JsonValue:
    """Replace credential values at any depth, keeping the shape so replay still parses."""
    if isinstance(body, dict):
        return {
            k: REDACTED if k.lower() in SECRET_BODY_FIELDS else redact(v) for k, v in body.items()
        }
    if isinstance(body, list):
        return [redact(item) for item in body]
    return body


@dataclass(frozen=True)
class Fixture:
    """A recorded response. Redaction happens on construction, so no Fixture can hold a secret."""

    key: FixtureKey
    status_code: int
    body: JsonValue
    recorded_at: datetime
    headers: dict[str, str]

    def __post_init__(self) -> None:
        kept = {k.lower(): v for k, v in self.headers.items() if k.lower() in ALLOWED_HEADERS}
        object.__setattr__(self, "body", redact(self.body))
        object.__setattr__(self, "headers", kept)


class FixtureMissingError(LookupError):
    """Replay mode asked for a request that was never recorded."""

    def __init__(self, key: FixtureKey) -> None:
        super().__init__(f"No fixture for {key.service} {key.operation} ({key.relative_path})")
        self.key = key


class FixtureStore(Protocol):
    def get(self, key: FixtureKey) -> Fixture | None: ...

    def put(self, fixture: Fixture) -> None: ...
