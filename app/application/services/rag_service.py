"""
RAG Service is responsible for handling the core logic of the Retrieval-Augmented
Generation (RAG) process, including retrieving relevant chunks from the vector
database and generating answers using the language model based on the retrieved
context. It also provides a debug method to return detailed information about the
query processing for analysis and debugging purposes.
"""
from __future__ import annotations

import time
from app.core.config import Settings
from app.domain.schemas.common import (
    DebugRetrievedChunk,
    RetrievedChunk,
    SourceReference,
)
from app.domain.report_policy import (
    REPORT_POLICY,
    infer_acceptability_status,
    infer_grounding_strength,
    infer_interpretation_basis,
    infer_recommended_action,
)
from app.domain.source_normalization import infer_applicable_standard_from_sources
from app.domain.schemas.debug import DebugResponse
from app.domain.schemas.rag import QueryMetadata, QueryResponse, RetrieveResponse
from app.infrastructure.clients.gemini_client import GeminiClient
from app.infrastructure.clients.qdrant_client import QdrantSearchClient
from app.infrastructure.clients.voyage_client import VoyageClient
from app.utils.prompt_loader import load_prompt
from app.utils.timers import Timer
from app.domain.schemas.report import ReportSections
from app.utils.report_parser import parse_report_sections
from app.metrics.report_metrics_store import append_report_metric
from app.domain.defect_knowledge import get_defect_knowledge
from app.utils.report_aggregation import aggregate_detection_payload
from app.domain.schemas.common import RetrievedChunk

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

    def _build_natural_detection_summary(
        self,
        normalized_defect_name: str,
        instances_count: int,
        location: str,
        average_area_mm2: float,
        confidence_avg: float,
        severity: str,
        board_side: str,
        inspection_scope: str,
    ) -> str:
        return (
            f"The inspection system detected {instances_count} instance(s) of "
            f"{normalized_defect_name} in the {location} region of the {board_side} side, "
            f"within the {inspection_scope} scope. The average affected area was "
            f"{average_area_mm2:.2f} mm², with an average confidence score of "
            f"{confidence_avg:.2f}. The detection subsystem assigned a severity label of "
            f"'{severity}'."
        )
    
    def _build_report_retrieval_queries(
        self,
        normalized_defect_name: str,
        query_aliases: list[str],
        ipc_family: str,
        ipc_basis: str,
        description: str,
        engineering_justification: str,
        recommended_standard_target: str,
        inspection_scope: str,
        reference_hint: str | None,
        user_question: str,
    ) -> list[str]:
        queries = [
            f"{normalized_defect_name} {recommended_standard_target} acceptability criteria {inspection_scope}",
            f"{ipc_family} {ipc_basis} {recommended_standard_target} printed board defect",
            f"{description} {engineering_justification} {recommended_standard_target}",
            f"{' '.join(query_aliases)} {recommended_standard_target} {reference_hint or ''} {user_question}",
        ]

        # Elimina duplicados y vacíos
        cleaned = []
        seen = set()
        for q in queries:
            q = " ".join(q.split()).strip()
            if q and q not in seen:
                seen.add(q)
                cleaned.append(q)

        return cleaned

    async def _retrieve_multi_query(
        self,
        queries: list[str],
        top_k_per_query: int,
        score_threshold: float,
        max_final_chunks: int,
    ) -> list[RetrievedChunk]:
        merged: dict[str, RetrievedChunk] = {}

        for query in queries:
            partial_response = await self.retrieve(
                query=query,
                top_k=top_k_per_query,
                score_threshold=score_threshold,
            )

            for chunk in partial_response.retrieved_chunks:
                existing = merged.get(chunk.chunk_id)
                if existing is None or chunk.score > existing.score:
                    merged[chunk.chunk_id] = chunk

        ranked = sorted(
            merged.values(),
            key=lambda c: c.score,
            reverse=True,
        )

        return ranked[:max_final_chunks]
    
    async def generate_report(self, request):
        aggregated = aggregate_detection_payload(
            [d.model_dump() for d in request.detections]
        )

        defect_class = aggregated["defect_class"]
        instances_count = aggregated["instances_count"]
        confidence_avg = aggregated["confidence_avg"]
        average_area_mm2 = aggregated["average_area_mm2"]
        severity = aggregated["severity"]
        location_summary = aggregated["location_summary"]
        reference_hint = aggregated["reference_hint"]

        knowledge = get_defect_knowledge(defect_class)

        normalized_defect_name = knowledge["canonical_name"]
        query_aliases = knowledge["query_aliases"]
        recommended_standard_target = (
            request.standard_target
            if request.standard_target
            else knowledge["recommended_standard_targets"][0]
        )
        inspection_scope = knowledge["inspection_scope"]

        ipc_family = knowledge["ipc_family"]
        ipc_basis = knowledge["ipc_basis"]
        description = knowledge["description"]
        engineering_justification = knowledge["engineering_justification"]

        product_class = request.product_class if request.product_class else "unknown"
        board_side = request.board_side if request.board_side else "unknown"

        if request.user_question:
            user_question = request.user_question
        else:
            user_question = (
                f"What does {recommended_standard_target} indicate about this defect condition, "
                f"its acceptability, technical significance, and recommended disposition?"
            )
        
        started_at = time.perf_counter()

        retrieval_queries = self._build_report_retrieval_queries(
            normalized_defect_name=normalized_defect_name,
            query_aliases=query_aliases,
            ipc_family=ipc_family,
            ipc_basis=ipc_basis,
            description=description,
            engineering_justification=engineering_justification,
            recommended_standard_target=recommended_standard_target,
            inspection_scope=inspection_scope,
            reference_hint=reference_hint,
            user_question=user_question,
        )

        retrieved_chunks = await self._retrieve_multi_query(
            queries=retrieval_queries,
            top_k_per_query=REPORT_POLICY["report_retrieval_per_query_top_k"],
            score_threshold=REPORT_POLICY["report_retrieval_score_threshold"],
            max_final_chunks=REPORT_POLICY["report_retrieval_max_final_chunks"],
        )

        context = self._build_context(retrieved_chunks)

        prompt_template = load_prompt("report_generation_prompt.txt")

        final_prompt = prompt_template.format(
            defect_class=defect_class,
            normalized_defect_name=normalized_defect_name,
            instances_count=instances_count,
            location_summary=location_summary,
            average_area_mm2=average_area_mm2,
            confidence_avg=confidence_avg,
            severity=severity,
            board_side=board_side,
            product_class=product_class,
            standard_target=recommended_standard_target,
            inspection_scope=inspection_scope,
            ipc_family=ipc_family,
            ipc_basis=ipc_basis,
            description=description,
            engineering_justification=engineering_justification,
            reference_hint=reference_hint or "none",
            user_question=user_question,
            context=context,
        )

        raw_answer = await self.gemini_client.generate(
            system_prompt="You are a strict technical PCB report generator.",
            user_prompt=final_prompt,
            temperature=REPORT_POLICY["report_generation_temperature"],
            max_output_tokens=REPORT_POLICY["report_generation_max_output_tokens"],
        )

        parsed = parse_report_sections(raw_answer)

        natural_detection_summary = (
            f"The inspection system detected {instances_count} instance(s) of "
            f"{normalized_defect_name} distributed across the following region(s): "
            f"{location_summary}. The average affected area was {average_area_mm2:.2f} mm², "
            f"with an average confidence score of {confidence_avg:.2f}. "
            f"The dominant severity label assigned by the detection subsystem was '{severity}'."
        )

        standards_interpretation = parsed["standards_interpretation"]
        technical_risk = parsed["technical_risk"]
        recommendation = parsed["recommendation"]
        grounding_disclaimer = parsed["grounding_disclaimer"]

        grounding_strength = infer_grounding_strength(
            standards_interpretation=standards_interpretation,
            grounding_disclaimer=grounding_disclaimer,
        )

        interpretation_basis = infer_interpretation_basis(
            standards_interpretation=standards_interpretation,
            grounding_disclaimer=grounding_disclaimer,
        )

        acceptability_status = infer_acceptability_status(
            standards_interpretation=standards_interpretation,
            recommendation=recommendation,
            grounding_strength=grounding_strength,
            interpretation_basis=interpretation_basis,
        )

        recommended_action = infer_recommended_action(
            recommendation=recommendation,
            acceptability_status=acceptability_status,
            grounding_strength=grounding_strength,
            interpretation_basis=interpretation_basis,
        )

        sources = self._build_sources(retrieved_chunks)
        applicable_standard = infer_applicable_standard_from_sources(
            sources=sources,
            recommended_standard_target=recommended_standard_target,
        )

        report = ReportSections(
            detection_summary=natural_detection_summary,
            standards_interpretation=standards_interpretation,
            technical_risk=technical_risk,
            recommendation=recommendation,
            grounding_disclaimer=grounding_disclaimer,
        )

        report_text = (
            f"Detection Summary:\n{report.detection_summary}\n\n"
            f"Standards-Based Assessment:\n{report.standards_interpretation}\n\n"
            f"Technical Risk / Implication:\n{report.technical_risk}\n\n"
            f"Preliminary Disposition / Recommendation:\n{report.recommendation}\n\n"
            f"Limitations / Grounding Note:\n{report.grounding_disclaimer}"
        )

        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

        metadata = {
            "model": self.settings.gemini_model,
            "embedding_model": self.settings.voyage_model,
            "qdrant_collection": self.settings.qdrant_collection,
            "top_k": REPORT_POLICY["report_retrieval_per_query_top_k"],
            "score_threshold": REPORT_POLICY["report_retrieval_score_threshold"],
            "latency_ms": elapsed_ms,
            "report_retrieval_queries": retrieval_queries,
            "product_class": product_class,
            "board_side": board_side,
            "reference_hint": reference_hint,
        }

        append_report_metric(
            {
                "defect_class": defect_class,
                "normalized_defect_name": normalized_defect_name,
                "recommended_standard_target": recommended_standard_target,
                "inspection_scope": inspection_scope,
                "grounding_strength": grounding_strength,
                "interpretation_basis": interpretation_basis,
                "acceptability_status": acceptability_status,
                "recommended_action": recommended_action,
                "latency_ms": metadata.get("latency_ms", 0),
            }
        )

        return {
            "report": report,
            "report_text": report_text,
            "raw_answer": raw_answer,
            "sources": sources,
            "metadata": metadata,
            "normalized_defect_name": normalized_defect_name,
            "recommended_standard_target": recommended_standard_target,
            "inspection_scope": inspection_scope,
            "grounding_strength": grounding_strength,
            "acceptability_status": acceptability_status,
            "recommended_action": recommended_action,
            "interpretation_basis": interpretation_basis,
            "applicable_standard": applicable_standard,
        }
    