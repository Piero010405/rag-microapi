"""
Rag schemas
"""
from pydantic import BaseModel, Field
from app.domain.schemas.common import RetrievedChunk, SourceReference


class QueryRequest(BaseModel):
    """
    Query request schema for RAG endpoint
        - query: The user's query string (required, min length 3)
    """
    query: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    include_sources: bool = True
    include_chunks: bool = True
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_output_tokens: int | None = Field(default=None, ge=64, le=4096)


class RetrieveRequest(BaseModel):
    """
    Retrieve request schema for RAG endpoint
        - query: The user's query string (required, min length 3)
    """
    query: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class QueryMetadata(BaseModel):
    """
    Query metadata schema for RAG responses
        - model: The language model used for generating the answer
        - embedding_model: The embedding model used for retrieving relevant chunks
        - qdrant_collection: The Qdrant collection used for retrieval
        - top_k: The number of top relevant chunks retrieved
        - score_threshold: The minimum relevance score threshold for retrieved chunks
        - latency_ms: The total latency of the query processing in milliseconds
    """
    model: str
    embedding_model: str
    qdrant_collection: str
    top_k: int
    score_threshold: float
    latency_ms: int


class QueryResponse(BaseModel):
    """
    Query response schema for RAG endpoint
        - query: The original query string
        - answer: The generated answer from the language model
        - sources: A list of source references used to generate the answer
        - retrieved_chunks: A list of retrieved chunks that were relevant to the query
        - metadata: Metadata about the query and retrieval process
    """
    query: str
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    metadata: QueryMetadata


class RetrieveResponse(BaseModel):
    """
    Retrieve response schema for RAG endpoint
        - query: The original query string
        - retrieved_chunks: A list of retrieved chunks that were relevant to the query
        - metadata: Metadata about the query and retrieval process
    """
    query: str
    retrieved_chunks: list[RetrievedChunk]
    metadata: QueryMetadata
