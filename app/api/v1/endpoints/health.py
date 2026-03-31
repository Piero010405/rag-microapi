from fastapi import APIRouter

from app.api.dependencies import get_gemini_client, get_qdrant_client, get_voyage_client
from app.core.config import get_settings
from app.domain.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
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
