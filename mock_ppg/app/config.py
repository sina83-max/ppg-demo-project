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


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance.

    Returns:
        Settings: Mock service configuration.
    """
    return Settings()


settings = get_settings()
