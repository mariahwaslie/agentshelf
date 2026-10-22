from app.cache.keys import fixture_key
from app.cache.store import CacheMode, FixtureMissingError, cache_mode_for
from app.models import AppMode


def test_replay_mode_never_calls_live() -> None:
    assert cache_mode_for(AppMode.REPLAY, record=False) is CacheMode.REPLAY
    assert cache_mode_for(AppMode.REPLAY, record=True) is CacheMode.REPLAY


def test_live_mode_reuses_fixtures_unless_recording() -> None:
    assert cache_mode_for(AppMode.LIVE, record=False) is CacheMode.CACHE_FIRST
    assert cache_mode_for(AppMode.LIVE, record=True) is CacheMode.REFRESH


def test_missing_fixture_error_names_the_file() -> None:
    key = fixture_key("paypal", "GET /v2/checkout/orders/123")
    error = FixtureMissingError(key)
    assert str(key.relative_path) in str(error)
    assert error.key == key
