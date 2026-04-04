"""
Dependencies for the FastAPI application.
"""
from functools import lru_cache

from app.application.services.rag_service import RAGService
from app.core.config import Settings, get_settings
from app.infrastructure.clients.gemini_client import GeminiClient
from app.infrastructure.clients.qdrant_client import QdrantSearchClient
from app.infrastructure.clients.voyage_client import VoyageClient


@lru_cache
def get_voyage_client() -> VoyageClient:
    """Get the VoyageClient instance."""
    settings: Settings = get_settings()
    return VoyageClient(settings)


@lru_cache
def get_qdrant_client() -> QdrantSearchClient:
    """Get the QdrantSearchClient instance."""
    settings: Settings = get_settings()
    return QdrantSearchClient(settings)


@lru_cache
def get_gemini_client() -> GeminiClient:
    """Get the GeminiClient instance."""
    settings: Settings = get_settings()
    return GeminiClient(settings)


@lru_cache
def get_rag_service() -> RAGService:
    """Get the RAGService instance."""
    settings: Settings = get_settings()
    return RAGService(
        settings=settings,
        voyage_client=get_voyage_client(),
        qdrant_client=get_qdrant_client(),
        gemini_client=get_gemini_client(),
    )
