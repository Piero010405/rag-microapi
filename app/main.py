"""
Main module
"""
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.log_config import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Micro API real para pruebas del módulo RAG",
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)
