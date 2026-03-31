from __future__ import annotations

from app.core.config import Settings
from app.domain.schemas.common import RetrievedChunk, SourceReference
from app.domain.schemas.debug import DebugResponse
from app.domain.schemas.rag import QueryMetadata, QueryResponse, RetrieveResponse
from app.infrastructure.clients.gemini_client import GeminiClient
from app.infrastructure.clients.qdrant_client import QdrantSearchClient
from app.infrastructure.clients.voyage_client import VoyageClient
from app.utils.prompt_loader import load_prompt
from app.utils.timers import Timer


class RAGService:
    def __init__(
        self,
        settings: Settings,
        voyage_client: VoyageClient,
        qdrant_client: QdrantSearchClient,
        gemini_client: GeminiClient,
    ) -> None:
        self.settings = settings
        self.voyage_client = voyage_client
        self.qdrant_client = qdrant_client
        self.gemini_client = gemini_client

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> RetrieveResponse:
        timer = Timer()

        top_k = top_k or self.settings.default_top_k
        score_threshold = (
            score_threshold
            if score_threshold is not None
            else self.settings.default_score_threshold
        )

        query_embedding = await self.voyage_client.embed_query(query)
        raw_chunks = await self.qdrant_client.search(
            vector=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        chunks = [
            RetrievedChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                score=item["score"],
                metadata=item["metadata"],
            )
            for item in raw_chunks
        ]

        metadata = QueryMetadata(
            model=self.settings.gemini_model,
            embedding_model=self.settings.voyage_model,
            top_k=top_k,
            score_threshold=score_threshold,
            latency_ms=timer.elapsed_ms(),
        )

        return RetrieveResponse(
            query=query,
            retrieved_chunks=chunks,
            metadata=metadata,
        )

    async def query(
        self,
        query: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> QueryResponse:
        timer = Timer()

        retrieve_response = await self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        system_prompt = load_prompt("system_prompt.txt")
        qa_prompt_template = load_prompt("technical_qa_prompt.txt")

        context = self._build_context(retrieve_response.retrieved_chunks)
        final_prompt = qa_prompt_template.format(query=query, context=context)

        temperature = (
            temperature if temperature is not None else self.settings.default_temperature
        )
        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.settings.default_max_output_tokens
        )

        answer = await self.gemini_client.generate(
            system_prompt=system_prompt,
            user_prompt=final_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        sources = self._build_sources(retrieve_response.retrieved_chunks)

        metadata = QueryMetadata(
            model=self.settings.gemini_model,
            embedding_model=self.settings.voyage_model,
            top_k=retrieve_response.metadata.top_k,
            score_threshold=retrieve_response.metadata.score_threshold,
            latency_ms=timer.elapsed_ms(),
        )

        return QueryResponse(
            query=query,
            answer=answer,
            sources=sources,
            retrieved_chunks=retrieve_response.retrieved_chunks,
            metadata=metadata,
        )

    async def debug(
        self,
        query: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> DebugResponse:
        total_timer = Timer()
        retrieval_timer = Timer()

        retrieve_response = await self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        retrieval_ms = retrieval_timer.elapsed_ms()

        system_prompt = load_prompt("system_prompt.txt")
        qa_prompt_template = load_prompt("technical_qa_prompt.txt")
        context = self._build_context(retrieve_response.retrieved_chunks)
        final_prompt = qa_prompt_template.format(query=query, context=context)

        generation_timer = Timer()
        answer = await self.gemini_client.generate(
            system_prompt=system_prompt,
            user_prompt=final_prompt,
            temperature=temperature if temperature is not None else self.settings.default_temperature,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.settings.default_max_output_tokens,
        )
        generation_ms = generation_timer.elapsed_ms()

        return DebugResponse(
            query=query,
            prompt_used=f"{system_prompt}\n\n---\n\n{final_prompt}",
            retrieved_chunks=retrieve_response.retrieved_chunks,
            final_context=context,
            generated_answer=answer,
            timings_ms={
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "total_ms": total_timer.elapsed_ms(),
            },
            config_used={
                "qdrant_collection": self.settings.qdrant_collection,
                "embedding_model": self.settings.voyage_model,
                "generation_model": self.settings.gemini_model,
                "default_top_k": self.settings.default_top_k,
                "default_score_threshold": self.settings.default_score_threshold,
            },
        )

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context retrieved."

        parts: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            title = chunk.metadata.get("document_title", "Unknown document")
            section = chunk.metadata.get("section", "Unknown section")
            page = chunk.metadata.get("page", "N/A")
            parts.append(
                f"[Chunk {idx}] Source: {title} | Section: {section} | Page: {page}\n"
                f"{chunk.text}"
            )
        return "\n\n".join(parts)

    def _build_sources(self, chunks: list[RetrievedChunk]) -> list[SourceReference]:
        sources: list[SourceReference] = []
        for chunk in chunks:
            md = chunk.metadata
            sources.append(
                SourceReference(
                    document_id=md.get("document_id", "unknown"),
                    document_title=md.get("document_title", "Unknown document"),
                    chunk_id=chunk.chunk_id,
                    score=chunk.score,
                    section=md.get("section"),
                    page=md.get("page"),
                )
            )
        return sources
