"""
Report generation endpoint for generating a report based on the provided defect information. This
endpoint receives a request containing the defect class, instances count, and location, and returns 
a structured report with sections such as detection summary, standards interpretation, technical risk, 
recommendation, and grounding disclaimer. The endpoint also includes the raw answer from the model, 
sources used for generating the report, and any additional metadata related to the report generation
process.
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.domain.schemas.report import ReportGenerationRequest, ReportGenerationResponse

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    rag_service=Depends(get_rag_service),
):
    """
    Generate a report based on the provided defect information, including the defect class, 
    instances count, and location.
    """
    result = await rag_service.generate_report(request)

    return ReportGenerationResponse(
        report=result["report"],
        report_text=result["report_text"],
        raw_answer=result["raw_answer"],
        sources=result["sources"],
        metadata=result["metadata"],
        normalized_defect_name=result["normalized_defect_name"],
        recommended_standard_target=result["recommended_standard_target"],
        inspection_scope=result["inspection_scope"],
    )
