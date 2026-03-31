from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    qdrant_connected: bool
    embeddings_provider_available: bool
    llm_provider_available: bool
