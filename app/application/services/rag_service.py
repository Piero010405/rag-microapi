"""
RAG Service is responsible for handling the core logic of the Retrieval-Augmented
Generation (RAG) process, including retrieving relevant chunks from the vector
database and generating answers using the language model based on the retrieved
context. It also provides a debug method to return detailed information about the
query processing for analysis and debugging purposes.
"""
from __future__ import annotations

from app.core.config import Settings
from app.domain.schemas.common import (
    DebugRetrievedChunk,
    RetrievedChunk,
    SourceReference,
)
from app.domain.schemas.debug import DebugResponse
from app.domain.schemas.rag import QueryMetadata, QueryResponse, RetrieveResponse
from app.infrastructure.clients.gemini_client import GeminiClient
from app.infrastructure.clients.qdrant_client import QdrantSearchClient
from app.infrastructure.clients.voyage_client import VoyageClient
from app.utils.prompt_loader import load_prompt
from app.utils.timers import Timer


class RAGService:
    """
    Rag Service orchestrates the retrieval of relevant chunks from the vector database
    and the generation of answers using the language model. It provides methods for both
    retrieval and generation, as well as a debug method that returns detailed information
    about the query processing, including timings and configurations used. The service is
    designed to be modular and easily testable, with clear separation of concerns between
    retrieval and generation logic.
    """
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
        """
        Retrieves relevant chunks from the vector database based on the query embedding.
        It uses the VoyageClient to generate the query embedding and the QdrantSearchClient 
        to perform the search in the vector database. The method returns a RetrieveResponse 
        containing the original query, the list of retrieved
        """
        timer = Timer()

        effective_top_k = top_k or self.settings.default_top_k
        effective_score_threshold = (
            score_threshold
            if score_threshold is not None
            else self.settings.default_score_threshold
        )

        query_embedding = await self.voyage_client.embed_query(query)

        raw_chunks = await self.qdrant_client.search(
            vector=query_embedding,
            top_k=effective_top_k,
            score_threshold=effective_score_threshold,
        )

        chunks = [
            RetrievedChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                score=item["score"],
                source_file=item["source_file"],
                chunk_index=item["chunk_index"],
            )
            for item in raw_chunks
        ]

        metadata = QueryMetadata(
            model=self.settings.gemini_model,
            embedding_model=self.settings.voyage_model,
            qdrant_collection=self.settings.qdrant_collection,
            top_k=effective_top_k,
            score_threshold=effective_score_threshold,
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
        include_sources_in_answer: bool = True,
    ) -> QueryResponse:
        """
        Queries the RAG system by first retrieving relevant chunks based on the query and then 
        generating an answer using the Gemini language model. The method constructs a prompt 
        using the retrieved chunks
        """
        total_timer = Timer()

        retrieve_response = await self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        system_prompt = load_prompt("system_prompt.txt")
        qa_prompt_template = load_prompt("technical_qa_prompt.txt")

        context = self._build_context(retrieve_response.retrieved_chunks)
        citation_instruction = (
            "You may mention source file names when relevant."
            if include_sources_in_answer
            else (
                "Do not mention source file names, chunk indices, "
                "or internal references in the answer."
            )
        )

        final_prompt = qa_prompt_template.format(
            query=query,
            context=context,
            citation_instruction=citation_instruction,
        )

        effective_temperature = (
            temperature if temperature is not None else self.settings.default_temperature
        )
        effective_max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.settings.default_max_output_tokens
        )

        answer = await self.gemini_client.generate(
            system_prompt=system_prompt,
            user_prompt=final_prompt,
            temperature=effective_temperature,
            max_output_tokens=effective_max_output_tokens,
        )

        sources = self._build_sources(retrieve_response.retrieved_chunks)

        metadata = QueryMetadata(
            model=self.settings.gemini_model,
            embedding_model=self.settings.voyage_model,
            qdrant_collection=self.settings.qdrant_collection,
            top_k=retrieve_response.metadata.top_k,
            score_threshold=retrieve_response.metadata.score_threshold,
            latency_ms=total_timer.elapsed_ms(),
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
        """
        Debug method that processes the query through the RAG system and returns a 
        DebugResponse containing detailed information about the query processing, 
        including the prompt used, retrieved chunks, generated answer, timings for 
        retrieval and generation, and the configurations used. This method is useful 
        for analyzing the behavior of the RAG system and understanding how different 
        parameters affect the results. It provides insights into the internal workings 
        of the retrieval and generation steps, making it easier to identify potential 
        issues and optimize the system.
        """
        total_timer = Timer()

        retrieval_timer = Timer()
        retrieve_response = await self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        retrieval_ms = retrieval_timer.elapsed_ms()

        raw_chunks = await self.qdrant_client.search(
            vector=await self.voyage_client.embed_query(query),
            top_k=top_k or self.settings.default_top_k,
            score_threshold=score_threshold
            if score_threshold is not None
            else self.settings.default_score_threshold,
        )

        debug_chunks = [
            DebugRetrievedChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                score=item["score"],
                source_file=item["source_file"],
                chunk_index=item["chunk_index"],
                metadata=item["metadata"],
            )
            for item in raw_chunks
        ]

        system_prompt = load_prompt("system_prompt.txt")
        qa_prompt_template = load_prompt("technical_qa_prompt.txt")
        context = self._build_context(retrieve_response.retrieved_chunks)
        final_prompt = qa_prompt_template.format(
            query=query,
            context=context,
            citation_instruction="You may mention source file names when relevant.",
        )

        default = self.settings.default_temperature
        generation_timer = Timer()
        answer = await self.gemini_client.generate(
            system_prompt=system_prompt,
            user_prompt=final_prompt,
            temperature=temperature if temperature is not None else default,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.settings.default_max_output_tokens,
        )
        generation_ms = generation_timer.elapsed_ms()

        return DebugResponse(
            query=query,
            prompt_used=f"{system_prompt}\n\n---\n\n{final_prompt}",
            retrieved_chunks=debug_chunks,
            final_context=context,
            generated_answer=answer,
            timings_ms={
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "total_ms": total_timer.elapsed_ms(),
            },
            config_used={
                "qdrant_url": self.settings.qdrant_url,
                "qdrant_collection": self.settings.qdrant_collection,
                "embedding_model": self.settings.voyage_model,
                "generation_model": self.settings.gemini_model,
                "default_top_k": self.settings.default_top_k,
                "default_score_threshold": self.settings.default_score_threshold,
                "default_temperature": self.settings.default_temperature,
            },
        )

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context retrieved."

        parts: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            parts.append(
                f"[Chunk {idx}] Source file: {chunk.source_file} | "
                f"Chunk index: {chunk.chunk_index}\n"
                f"{chunk.text}"
            )
        return "\n\n".join(parts)

    def _build_sources(self, chunks: list[RetrievedChunk]) -> list[SourceReference]:
        return [
            SourceReference(
                source_file=chunk.source_file,
                chunk_index=chunk.chunk_index,
                chunk_id=chunk.chunk_id,
                score=chunk.score,
            )
            for chunk in chunks
        ]
    
    async def generate_report(
        self,
        request,
    ):
        """
        Generates a report based on the provided request.
        """
        retrieve_response = await self.retrieve(
            query=f"{request.defect_class} PCB defect standards IPC-A-610 acceptability",
        )

        context = self._build_context(retrieve_response.retrieved_chunks)

        prompt_template = load_prompt("report_generation_prompt.txt")

        final_prompt = prompt_template.format(
            defect_class=request.defect_class,
            instances_count=request.instances_count,
            location=request.location,
            average_area_mm2=request.average_area_mm2,
            confidence_avg=request.confidence_avg,
            severity=request.severity,
            user_question=request.user_question,
            context=context,
        )

        answer = await self.gemini_client.generate(
            system_prompt="You are a strict technical report generator.",
            user_prompt=final_prompt,
            temperature=0.1,
            max_output_tokens=800,
        )

        return {
            "raw_answer": answer,
            "sources": self._build_sources(retrieve_response.retrieved_chunks),
            "metadata": retrieve_response.metadata.dict(),
        }
