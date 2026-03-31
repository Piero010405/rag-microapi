from pydantic import BaseModel, Field
from app.domain.schemas.common import RetrievedChunk, SourceReference


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Consulta del usuario")
    top_k: int | None = Field(default=None, ge=1, le=20)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    include_sources: bool = True
    include_chunks: bool = True
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_output_tokens: int | None = Field(default=None, ge=64, le=4096)


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class QueryMetadata(BaseModel):
    model: str
    embedding_model: str
    top_k: int
    score_threshold: float
    latency_ms: int


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    metadata: QueryMetadata


class RetrieveResponse(BaseModel):
    query: str
    retrieved_chunks: list[RetrievedChunk]
    metadata: QueryMetadata
