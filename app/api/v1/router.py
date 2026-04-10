"""
Router module
"""
from fastapi import APIRouter

from app.api.v1.endpoints.debug import router as debug_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.rag import router as rag_router
from app.api.v1.endpoints.report import router as report


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(rag_router)
api_router.include_router(debug_router)
api_router.include_router(report)
