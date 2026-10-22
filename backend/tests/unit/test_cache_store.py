from datetime import UTC, datetime

import pytest

from app.cache.keys import fixture_key
from app.cache.store import (
    REDACTED,
    CacheAction,
    CacheMode,
    CallPolicy,
    Fixture,
    FixtureMissingError,
    cache_action,
    cache_mode_for,
)
from app.models import AppMode

TOKEN_KEY = fixture_key("paypal", "POST /v1/oauth2/token")


def test_replay_mode_never_calls_live() -> None:
    assert cache_mode_for(AppMode.REPLAY, record=False) is CacheMode.REPLAY
    assert cache_mode_for(AppMode.REPLAY, record=True) is CacheMode.REPLAY
    assert cache_action(CacheMode.REPLAY, CallPolicy.REUSABLE) is CacheAction.SERVE_FIXTURE
    assert cache_action(CacheMode.REPLAY, CallPolicy.ALWAYS_LIVE) is CacheAction.SERVE_FIXTURE


def test_live_mode_reuses_only_reusable_reads() -> None:
    assert cache_mode_for(AppMode.LIVE, record=False) is CacheMode.CACHE_FIRST
    assert cache_mode_for(AppMode.LIVE, record=True) is CacheMode.REFRESH
    assert cache_action(CacheMode.CACHE_FIRST, CallPolicy.REUSABLE) is CacheAction.REUSE_OR_RECORD
    assert cache_action(CacheMode.REFRESH, CallPolicy.REUSABLE) is CacheAction.CALL_AND_RECORD


@pytest.mark.parametrize("mode", [CacheMode.CACHE_FIRST, CacheMode.REFRESH])
def test_paypal_calls_always_go_live_outside_replay(mode: CacheMode) -> None:
    """Order status (polling fallback) and catalog GETs (proof of update) must be current."""
    assert cache_action(mode, CallPolicy.ALWAYS_LIVE) is CacheAction.CALL_AND_RECORD


def test_credentials_are_never_recorded() -> None:
    assert cache_action(CacheMode.CACHE_FIRST, CallPolicy.NEVER_RECORD) is CacheAction.CALL_ONLY
    assert cache_action(CacheMode.REFRESH, CallPolicy.NEVER_RECORD) is CacheAction.CALL_ONLY
    assert cache_action(CacheMode.REPLAY, CallPolicy.NEVER_RECORD) is CacheAction.STUB


def test_fixture_redacts_tokens_at_any_depth() -> None:
    fixture = Fixture(
        key=TOKEN_KEY,
        status_code=200,
        body={"access_token": "A21AAsecret", "nested": [{"refresh_token": "r"}], "app_id": "APP"},
        recorded_at=datetime(2026, 10, 22, tzinfo=UTC),
        headers={},
    )
    assert fixture.body == {
        "access_token": REDACTED,
        "nested": [{"refresh_token": REDACTED}],
        "app_id": "APP",
    }
    assert "A21AAsecret" not in str(fixture)


def test_fixture_keeps_only_allow_listed_headers() -> None:
    fixture = Fixture(
        key=TOKEN_KEY,
        status_code=200,
        body=None,
        recorded_at=datetime(2026, 10, 22, tzinfo=UTC),
        headers={"Content-Type": "application/json", "Set-Cookie": "s=1", "Paypal-Debug-Id": "x"},
    )
    assert fixture.headers == {"content-type": "application/json"}


def test_missing_fixture_error_names_the_file() -> None:
    key = fixture_key("paypal", "GET /v2/checkout/orders/123")
    error = FixtureMissingError(key)
    assert str(key.relative_path) in str(error)
    assert error.key == key
