"""Settings for the mock PPG service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the mock gateway."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Mock PPG"
    debug: bool = True
    log_level: str = "INFO"

    # The mock accepts any apiKey/secretKey (docs/AGENTS.md section 8);
    # these values are only echoed back for debugging.
    mock_api_key: str = "mock-key"
    mock_secret_key: str = "mock-secret"

    # Called back by the mock to simulate the PSP notifying the merchant.
    callback_timeout_seconds: float = 10.0

    # Demo knob: occasionally answer verify with UNKNOWN (docs/AGENTS.md section 8).
    unknown_answer_rate: float = 0.0

    # --- Database ------------------------------------------------------
    # The mock persists its purchases so it can reject duplicate
    # clientReferenceNumbers and paginate `GET /v3/purchases` with real SQL
    # (ADR-008). In Docker the compose file overrides this to /data/mock_ppg.db.
    database_url: str = "sqlite+aiosqlite:///./mock_ppg.db"
    database_echo: bool = False

    # --- URLs ----------------------------------------------------------
    # Base URL a browser uses to reach this mock; used to build pspSwitchingUrl.
    public_base_url: str = "http://localhost:8001"

    # Docker-only host rewrite for callbacks. The merchant builds callbackUrl from
    # MERCHANT_CALLBACK_BASE (e.g. http://localhost:8000) which is right for the
    # browser and for real Jibit PPG, but unreachable from inside this container.
    # Set to http://merchant:8000 under Docker; leave empty to disable.
    callback_base_url_override: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance.

    Returns:
        Settings: Mock service configuration.
    """
    return Settings()


settings = get_settings()
