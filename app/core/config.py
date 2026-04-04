"""
Configuration for the application, using Pydantic's BaseSettings to load from
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the application
    - `app_name`: The name of the application
    - `app_env`: The environment the application is running in (e.g., development,
        production)
    - `app_version`: The version of the application
    - `api_prefix`: The prefix for all API routes
    - `use_mock_providers`: Whether to use mock providers for testing
    - `qdrant_url`: The URL for the Qdrant vector database
    - `qdrant_api_key`: The API key for Qdrant (if required)
    - `qdrant_collection`: The name of the Qdrant collection to use
    - `voyage_api_key`: The API key for the Voyage LLM provider
    - `voyage_model`: The model to use for the Voyage LLM provider
    - `gemini_api_key`: The API key for the Gemini LLM provider
    - `gemini_model`: The model to use for the Gemini LLM provider
    - `default_top_k`: The default number of top results to return from the vector
        database
    - `default_score_threshold`: The default score threshold for filtering vector
        database results
    - `default_temperature`: The default temperature for LLM generation
    - `default_max_output_tokens`: The default maximum number of tokens to generate
        from the LLM
    """
    app_name: str = "rag-microapi"
    app_env: str = "development"
    app_version: str = "0.2.0"
    api_prefix: str = "/api/v1"

    use_mock_providers: bool = False

    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_collection: str = "dev"

    voyage_api_key: str
    voyage_model: str = "voyage-4-lite"

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash-lite"

    default_top_k: int = 5
    default_score_threshold: float = 0.20
    default_temperature: float = 0.1
    default_max_output_tokens: int = 900

    http_timeout_seconds: int = 45

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get the settings from the environment variables."""
    return Settings()
