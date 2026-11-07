from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_origins(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AIVOA AI-Powered RCA"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./rca_ai.db"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    cors_origins: Annotated[list[str], BeforeValidator(_split_origins)] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )
    max_upload_mb: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
