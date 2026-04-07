"""
Health check endpoint for the RAG microservice. This module defines an API endpoint that 
allows clients to check the health status of the service, including the availability of 
its dependencies such as the Qdrant vector database, the Voyage embeddings provider, and 
the Gemini language model provider. The endpoint returns a structured response indicating 
the overall health status, environment, version, and the connectivity status of each dependency.
"""
from fastapi import APIRouter, Query

from app.api.dependencies import get_gemini_client, get_qdrant_client, get_voyage_client
from app.core.config import get_settings
from app.domain.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    deep: bool = Query(default=False, description="Run deeper provider checks")
) -> HealthResponse:
    """
    Endpoint to check the health status of the RAG microservice. It performs basic 
    checks to verify the availability of the Qdrant vector database, the Voyage 
    embeddings provider, and the Gemini language model provider. If the `deep` 
    query parameter is set to `True`, it can perform more thorough checks on the 
    providers, which may involve making test API calls to ensure they are fully operational.
    """
    settings = get_settings()
    qdrant_ok = await get_qdrant_client().is_available()
    voyage_ok = await get_voyage_client().is_available()
    gemini_ok = await get_gemini_client().is_available()

    # Por ahora el modo deep no hace calls costosas reales,
    # pero dejamos listo el contrato para endurecerlo luego.
    if deep:
        qdrant_ok = await get_qdrant_client().is_available()
        voyage_ok = await get_voyage_client().is_available()
        gemini_ok = await get_gemini_client().is_available()

    return HealthResponse(
        status="ok" if qdrant_ok and voyage_ok and gemini_ok else "degraded",
        environment=settings.app_env,
        version=settings.app_version,
        qdrant_connected=qdrant_ok,
        embeddings_provider_available=voyage_ok,
        llm_provider_available=gemini_ok,
    )
