"""Reports which keys are set (`make keys-check`). Prints names only, never values."""

import sys

from pydantic import SecretStr, ValidationError

from app.settings import Settings

KEY_NAMES = (
    "PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
    "PAYPAL_WEBHOOK_ID",
    "CHANNEL3_API_KEY",
    "GEMINI_API_KEY",
    "LLM_MODEL",
    "AG_LICENSE_KEY",
)


def is_set(value: SecretStr | str | None) -> bool:
    if isinstance(value, SecretStr):
        return bool(value.get_secret_value())
    return bool(value)


def main() -> int:
    try:
        settings = Settings()
    except ValidationError as exc:
        # Field names only: the error text could echo a bad value back.
        bad = ", ".join(str(err["loc"][0]).upper() for err in exc.errors())
        print(f"Settings invalid: {bad}. Check those entries in .env.")
        return 1
    print(f"APP_MODE: {settings.app_mode.value}   PayPal URL: sandbox ✓")
    for name in KEY_NAMES:
        state = "present" if is_set(getattr(settings, name.lower())) else "missing"
        print(f"  {name:<22} {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
