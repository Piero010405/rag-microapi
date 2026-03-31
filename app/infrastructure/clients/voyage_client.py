from __future__ import annotations

import hashlib
import logging

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class VoyageClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.timeout = settings.http_timeout_seconds

    async def is_available(self) -> bool:
        if self.settings.use_mock_providers:
            return True
        return bool(self.settings.voyage_api_key)

    async def embed_query(self, text: str) -> list[float]:
        if self.settings.use_mock_providers:
            return self._mock_embedding(text)

        if not self.settings.voyage_api_key:
            raise ValueError("VOYAGE_API_KEY is not configured")

        url = "https://api.voyageai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.settings.voyage_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": [text],
            "model": self.settings.voyage_model,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["data"][0]["embedding"]

    def _mock_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in digest[:32]]
