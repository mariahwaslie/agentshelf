"""Configuration, read only from the environment (and the repo-root .env during development)."""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models import AppMode, FeatureFlags, Service, ServiceState

REPO_ROOT = Path(__file__).resolve().parents[2]
PAYPAL_SANDBOX_URL = "https://api-m.sandbox.paypal.com"
REMOTE_SERVICES = (Service.PAYPAL, Service.CHANNEL3, Service.LLM)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_mode: AppMode = AppMode.REPLAY
    record: bool = False
    display_anonymized: bool = True
    seed: int = 42
    log_json: bool = False

    paypal_client_id: str | None = None
    paypal_client_secret: SecretStr | None = None
    paypal_base_url: str = PAYPAL_SANDBOX_URL
    paypal_webhook_id: str | None = None
    channel3_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    llm_model: str | None = None
    ag_license_key: SecretStr | None = None

    feature_studio_agent: bool = True
    feature_ag_studio: bool = True
    feature_shipment_tracking: bool = True
    feature_feed_export: bool = True
    feature_pick_model: bool = True

    data_dir: Path = REPO_ROOT / "data"
    frontend_dist: Path = REPO_ROOT / "frontend" / "dist"

    @field_validator("paypal_base_url")
    @classmethod
    def _sandbox_only(cls, url: str) -> str:
        """Refuse to start against live PayPal: this project never moves real money."""
        normalized = url.rstrip("/")
        if normalized != PAYPAL_SANDBOX_URL:
            raise ValueError(f"PAYPAL_BASE_URL must be the sandbox URL {PAYPAL_SANDBOX_URL}")
        return normalized

    @property
    def features(self) -> FeatureFlags:
        return FeatureFlags(
            studio_agent=self.feature_studio_agent,
            ag_studio=self.feature_ag_studio,
            shipment_tracking=self.feature_shipment_tracking,
            feed_export=self.feature_feed_export,
            pick_model=self.feature_pick_model,
        )

    def service_states(self) -> dict[Service, ServiceState]:
        """Which external services can be called. Replay mode needs no keys at all."""
        if self.app_mode is AppMode.REPLAY:
            remote = dict.fromkeys(REMOTE_SERVICES, ServiceState.REPLAY)
            return {**remote, Service.EMBEDDINGS: ServiceState.LOCAL}
        configured = {
            Service.PAYPAL: self.paypal_client_id is not None
            and self.paypal_client_secret is not None,
            Service.CHANNEL3: self.channel3_api_key is not None,
            Service.LLM: self.gemini_api_key is not None and self.llm_model is not None,
        }
        states = {
            service: ServiceState.CONFIGURED if ok else ServiceState.MISSING_KEYS
            for service, ok in configured.items()
        }
        return {**states, Service.EMBEDDINGS: ServiceState.LOCAL}


@lru_cache
def get_settings() -> Settings:
    return Settings()
