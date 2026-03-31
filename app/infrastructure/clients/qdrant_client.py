from __future__ import annotations

from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, ScoredPoint

from app.core.config import Settings


class QdrantSearchClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=settings.http_timeout_seconds,
        )

    async def is_available(self) -> bool:
        if self.settings.use_mock_providers:
            return True
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False

    async def search(
        self,
        vector: list[float],
        top_k: int,
        score_threshold: float,
        query_filter: Filter | None = None,
    ) -> list[dict[str, Any]]:
        if self.settings.use_mock_providers:
            return self._mock_search(vector=vector, top_k=top_k, score_threshold=score_threshold)

        results: list[ScoredPoint] = await self.client.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        parsed_results: list[dict[str, Any]] = []
        for item in results:
            payload = item.payload or {}
            parsed_results.append(
                {
                    "chunk_id": payload.get("chunk_id", str(item.id)),
                    "text": payload.get("text", ""),
                    "score": float(item.score),
                    "metadata": payload,
                }
            )

        return parsed_results

    def _mock_search(
        self,
        vector: list[float],
        top_k: int,
        score_threshold: float,
    ) -> list[dict[str, Any]]:
        samples = [
            {
                "chunk_id": "ipc-a-600m_001",
                "text": "Open circuit defects correspond to interruptions in the intended conductive path of the printed board.",
                "score": 0.91,
                "metadata": {
                    "document_id": "ipc-a-600m",
                    "document_title": "IPC-A-600M",
                    "section": "Conductive defects",
                    "page": 24,
                    "chunk_id": "ipc-a-600m_001",
                },
            },
            {
                "chunk_id": "nasa_workshop_g_014",
                "text": "PCB inspection procedures may include visual verification of conductor continuity and defect morphology.",
                "score": 0.84,
                "metadata": {
                    "document_id": "nasa-workshop-g",
                    "document_title": "NASA Workshop G",
                    "section": "Inspection procedures",
                    "page": 12,
                    "chunk_id": "nasa_workshop_g_014",
                },
            },
        ]
        return [x for x in samples if x["score"] >= score_threshold][:top_k]
