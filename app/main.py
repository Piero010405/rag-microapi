from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Micro API para pruebas y operación del módulo RAG",
)

app.include_router(api_router, prefix=settings.api_prefix)
