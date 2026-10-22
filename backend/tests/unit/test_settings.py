import pytest
from pydantic import ValidationError

from app.models import AppMode, Service, ServiceState
from app.settings import PAYPAL_SANDBOX_URL, REPO_ROOT, Settings


def test_refuses_live_paypal_url() -> None:
    with pytest.raises(ValidationError, match="sandbox"):
        Settings(_env_file=None, paypal_base_url="https://api-m.paypal.com")


def test_refuses_live_paypal_url_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAYPAL_BASE_URL", "https://api-m.paypal.com")
    with pytest.raises(ValidationError, match="sandbox"):
        Settings(_env_file=None)


def test_accepts_sandbox_url_with_trailing_slash() -> None:
    settings = Settings(_env_file=None, paypal_base_url=f"{PAYPAL_SANDBOX_URL}/")
    assert settings.paypal_base_url == PAYPAL_SANDBOX_URL


def test_env_example_parses_with_inline_comments() -> None:
    settings = Settings(_env_file=REPO_ROOT / ".env.example")
    assert settings.app_mode is AppMode.LIVE
    assert settings.display_anonymized is True
    assert settings.seed == 42


def test_empty_values_count_as_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHANNEL3_API_KEY", "")
    settings = Settings(_env_file=None, app_mode=AppMode.LIVE)
    assert settings.channel3_api_key is None
    assert settings.service_states()[Service.CHANNEL3] is ServiceState.MISSING_KEYS


def test_live_mode_reports_configured_services() -> None:
    settings = Settings(
        _env_file=None,
        app_mode=AppMode.LIVE,
        paypal_client_id="client-id",
        paypal_client_secret="client-secret",
        gemini_api_key="gemini-key",
    )
    states = settings.service_states()
    assert states[Service.PAYPAL] is ServiceState.CONFIGURED
    assert states[Service.CHANNEL3] is ServiceState.MISSING_KEYS
    assert states[Service.LLM] is ServiceState.MISSING_KEYS  # key without LLM_MODEL
    assert states[Service.EMBEDDINGS] is ServiceState.LOCAL


def test_replay_mode_needs_no_keys() -> None:
    states = Settings(_env_file=None, app_mode=AppMode.REPLAY).service_states()
    assert states[Service.PAYPAL] is ServiceState.REPLAY
    assert states[Service.LLM] is ServiceState.REPLAY
    assert states[Service.EMBEDDINGS] is ServiceState.LOCAL


def test_secrets_never_appear_in_repr_or_dump() -> None:
    settings = Settings(
        _env_file=None, paypal_client_secret="pp-secret-value", gemini_api_key="gm-secret-value"
    )
    rendered = repr(settings) + settings.model_dump_json()
    assert "pp-secret-value" not in rendered
    assert "gm-secret-value" not in rendered


def test_feature_flags_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_PICK_MODEL", "false")
    features = Settings(_env_file=None).features
    assert features.pick_model is False
    assert features.ag_studio is True
