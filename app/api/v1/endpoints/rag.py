"""
Rag endpoints
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.application.services.rag_service import RAGService
from app.domain.schemas.rag import (
    QueryRequest,
    QueryResponse,
    RetrieveRequest,
    RetrieveResponse,
)

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_only(
    request: RetrieveRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> RetrieveResponse:
    """Retrieve only endpoint"""
    return await rag_service.retrieve(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
    )


@router.post("/query", response_model=QueryResponse)
async def rag_query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    """RAG query endpoint"""
    response = await rag_service.query(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        temperature=request.temperature,
        max_output_tokens=request.max_output_tokens,
    )

    if not request.include_sources:
        response.sources = []

    if not request.include_chunks:
        response.retrieved_chunks = []

    return response
