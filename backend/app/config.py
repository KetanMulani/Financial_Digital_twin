from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Financial Digital Twin API"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "sqlite:///./twin.db"
    frontend_origin: str = "http://localhost:5173"

    # Natural-language scenario parser configuration.
    llm_provider: str = "gemini"
    llm_timeout_seconds: float = Field(default=30, gt=0, le=120)

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
