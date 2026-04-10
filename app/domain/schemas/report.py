""""
Report schemas
"""
from pydantic import BaseModel, Field


class ReportGenerationRequest(BaseModel):
    """
    Report generation request
    """
    defect_class: str
    instances_count: int
    location: str
    average_area_mm2: float
    confidence_avg: float
    severity: str
    user_question: str
    standard_target: str | None = None
    product_class: str | None = None
    board_side: str | None = None


class ReportSections(BaseModel):
    """
    Report sections
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class ReportGenerationResponse(BaseModel):
    """
    Report generation response
    """
    report: ReportSections
    report_text: str
    raw_answer: str
    sources: list
    metadata: dict
    normalized_defect_name: str
    recommended_standard_target: str
    inspection_scope: str
