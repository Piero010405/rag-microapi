"""
VoyageClient is responsible for communicating with the Voyage API to generate 
embeddings for user queries. It handles authentication, request formatting, 
and error handling to ensure reliable integration with the external service.
"""
from __future__ import annotations

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError


class VoyageClient:
    """
    VoyageClient provides methods to interact with the Voyage API
    """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.timeout = settings.http_timeout_seconds
        self.url = "https://api.voyageai.com/v1/embeddings"

    async def is_available(self) -> bool:
        """
        Indicates whether the Voyage API is available for use based on the presence 
        of an API key in the settings.
        """
        return bool(self.settings.voyage_api_key)

    async def embed_query(self, text: str) -> list[float]:
        """
        Embeds the input text using the Voyage API and returns the resulting embedding vector.
        """
        headers = {
            "Authorization": f"Bearer {self.settings.voyage_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": [text],
            "model": self.settings.voyage_model,
            "input_type": "query",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"Voyage request failed: {exc}") from exc

        try:
            return data["data"][0]["embedding"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError("Invalid Voyage response format") from exc
