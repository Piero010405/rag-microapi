from pydantic import BaseModel
from app.domain.schemas.common import RetrievedChunk


class DebugResponse(BaseModel):
    query: str
    prompt_used: str
    retrieved_chunks: list[RetrievedChunk]
    final_context: str
    generated_answer: str
    timings_ms: dict
    config_used: dict
