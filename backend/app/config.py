from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Financial Digital Twin API"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "sqlite:///./twin.db"
    frontend_origin: str = "http://localhost:5173"

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()