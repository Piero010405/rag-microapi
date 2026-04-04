"""
QdrantSearchClient is responsible for communicating with the Qdrant vector database 
to perform similarity searches.
"""
from __future__ import annotations

from typing import Any

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings
from app.core.exceptions import RetrievalError


class QdrantSearchClient:
    """
    QudrantSearchClient provides methods to interact with the Qdrant vector database for
    performing similarity searches based on vector embeddings.
    """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=settings.http_timeout_seconds,
        )

    async def is_available(self) -> bool:
        """
        Is the Qdrant client available for use by checking if the collection exists and 
        is accessible.
        """
        try:
            await self.client.get_collections()
            return True
        except (ConnectionError, TimeoutError, OSError):
            return False

    async def search(
        self,
        vector: list[float],
        top_k: int,
        score_threshold: float,
    ) -> list[dict[str, Any]]:
        """
        Searches the Qdrant collection for the most similar vectors to the input vector and
        returns a list of results with their associated metadata and similarity scores.
        """
        try:
            response = await self.client.query_points(
                collection_name=self.settings.qdrant_collection,
                query=vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

            results = response.points
        except Exception as exc:
            raise RetrievalError(f"Qdrant search failed: {exc}") from exc

        parsed_results: list[dict[str, Any]] = []

        for item in results:
            payload = item.payload or {}

            text = payload.get("text", "")
            source_file = payload.get("source_file", "unknown")
            chunk_index = payload.get("chunk_index", -1)
            chunk_index_value = int(chunk_index) if isinstance(chunk_index, (int, float)) else -1
            chunk_id = f"{source_file}__{chunk_index}"

            parsed_results.append(
                {
                    "chunk_id": chunk_id,
                    "text": text,
                    "score": float(item.score),
                    "source_file": source_file,
                    "chunk_index": chunk_index_value,
                    "metadata": payload,
                }
            )

        return parsed_results
