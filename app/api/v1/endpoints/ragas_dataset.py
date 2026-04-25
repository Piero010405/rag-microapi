"""
Ragas Dataset API Endpoints
"""
from fastapi import APIRouter

from app.domain.schemas.ragas_dataset import (
    RagasClearResponse,
    RagasDatasetResponse,
)
from app.metrics.ragas_dataset_store import (
    clear_ragas_dataset,
    export_ragas_dataset,
)

router = APIRouter(prefix="/ragas", tags=["ragas"])


@router.get("/dataset", response_model=RagasDatasetResponse)
async def get_ragas_dataset() -> RagasDatasetResponse:
    """
    Get the Ragas dataset, which includes all the samples that have been collected. Each sample 
    contains the question, contexts, answer, ground truth (if available), and metadata. The 
    response includes the total number of samples in the dataset and a list of all the samples. If 
    the dataset is empty, the total_samples will be 0 and the samples list will be empty.
    """
    samples = export_ragas_dataset()
    return RagasDatasetResponse(
        total_samples=len(samples),
        samples=samples,
    )


@router.delete("/dataset", response_model=RagasClearResponse)
async def delete_ragas_dataset() -> RagasClearResponse:
    """
    Ragas Clear Endpoint
    """
    clear_ragas_dataset()
    return RagasClearResponse(
        status="ok",
        message="RAGAS dataset cleared successfully.",
    )
