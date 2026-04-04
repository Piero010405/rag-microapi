"""
Health check response schema for the health endpoint
"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Health response schema for the health endpoint
        - status: The overall health status of the application (e.g., "healthy", "
            unhealthy")
        - environment: The current environment the application is running in (e.g., "
            development", "production")
        - version: The current version of the application
        - qdrant_connected: A boolean indicating if the application is successfully 
            connected to Qdrant
        - embeddings_provider_available: A boolean indicating if the embeddings 
            provider is available
        - llm_provider_available: A boolean indicating if the language model provider is available
    """
    status: str
    environment: str
    version: str
    qdrant_connected: bool
    embeddings_provider_available: bool
    llm_provider_available: bool
