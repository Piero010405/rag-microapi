from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "rag-microapi"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    use_mock_providers: bool = True

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "pcb_knowledge_base"

    voyage_api_key: str | None = None
    voyage_model: str = "voyage-4-lite"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"

    default_top_k: int = 5
    default_score_threshold: float = 0.25
    default_temperature: float = 0.1
    default_max_output_tokens: int = 800

    http_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
