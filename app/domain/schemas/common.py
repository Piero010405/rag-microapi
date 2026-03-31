from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    document_id: str = Field(..., description="Identificador del documento")
    document_title: str = Field(..., description="Título del documento")
    chunk_id: str = Field(..., description="Identificador del chunk")
    score: float = Field(..., description="Score de similitud")
    section: str | None = Field(default=None, description="Sección del documento")
    page: int | None = Field(default=None, description="Página del documento")


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: dict = Field(default_factory=dict)
