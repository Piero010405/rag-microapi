"""
Ragas Dataset Schemas
"""
from typing import Any

from pydantic import BaseModel


class RagasSample(BaseModel):
    """
    Ragas Sample Schema
    """
    question: str
    contexts: list[str]
    answer: str
    ground_truth: str | None = None
    metadata: dict[str, Any] = {}


class RagasDatasetResponse(BaseModel):
    """
    Ragas Dataset Response Schema
    """
    total_samples: int
    samples: list[RagasSample]


class RagasClearResponse(BaseModel):
    """
    Ragas Clear Response Schema
    """
    status: str
    message: str
