from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.application.services.rag_service import RAGService
from app.domain.schemas.debug import DebugResponse
from app.domain.schemas.rag import QueryRequest

router = APIRouter(prefix="/rag", tags=["debug"])


@router.post("/debug", response_model=DebugResponse)
async def rag_debug(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> DebugResponse:
    return await rag_service.debug(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        temperature=request.temperature,
        max_output_tokens=request.max_output_tokens,
    )
