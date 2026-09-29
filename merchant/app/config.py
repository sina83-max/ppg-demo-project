"""Application settings loaded from environment variables / `.env`.

The PPG target (local mock or real Jibit) is decided **only** by these values,
never by code changes. See docs/AGENTS.md section 11.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the merchant application.

    Environment variable names are the upper-cased field names
    (e.g. ``ppg_base_url`` -> ``PPG_BASE_URL``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---------------------------------------------------
    app_name: str = "PPG Demo Merchant"
    debug: bool = True
    log_level: str = "INFO"

    # --- PPG upstream (mock or real Jibit) ------------------------------
    # Mock : http://mock-ppg:8001
    # Real : https://napi.jibit.ir/ppg
    ppg_base_url: str = "http://mock-ppg:8001"
    ppg_api_key: str = "mock-key"
    ppg_secret_key: str = "mock-secret"
    ppg_timeout_seconds: float = 30.0

    # --- Merchant ------------------------------------------------------
    # Base URL used to build `callbackUrl` sent to PPG.
    merchant_callback_base: str = "http://localhost:8000"

    # --- Database ------------------------------------------------------
    database_url: str = "sqlite+aiosqlite:///./merchant.db"
    database_echo: bool = False

    # --- Dashboard -----------------------------------------------------
    # Kept in settings so the CDN reference is not hard-coded in templates.
    alpinejs_cdn_url: str = "https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance.

    Returns:
        Settings: Application configuration.
    """
    return Settings()


settings = get_settings()
