"""
Common schemas used across the application, such as source references and retrieved chunks.
"""
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """
    Schema representing a source reference for a retrieved chunk, including information
    about the source file, chunk index, chunk ID, similarity score, and optional 
    metadata such as document title, section, and page number.
    """
    source_file: str = Field(..., description="Nombre del archivo fuente")
    chunk_index: int = Field(..., description="Índice del chunk dentro del archivo")
    chunk_id: str = Field(..., description="ID derivado del chunk")
    score: float = Field(..., description="Score de similitud")
    document_title: str | None = None
    section: str | None = None
    page: int | None = None


class RetrievedChunk(BaseModel):
    """
    Retrieved chunk schema, representing a chunk of text retrieved from the vector database, along
    with its associated metadata such as source file, chunk index, similarity score, and any
    additional metadata.
    """
    chunk_id: str
    text: str
    score: float
    source_file: str
    chunk_index: int
    metadata: dict = Field(default_factory=dict)
