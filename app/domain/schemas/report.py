""""
Report schemas
"""
from pydantic import BaseModel, Field


class ReportGenerationRequest(BaseModel):
    """
    Reporte Generation Request model for generating a report based on the provided defect information.
    """
    defect_class: str
    instances_count: int
    location: str
    average_area_mm2: float
    confidence_avg: float
    severity: str
    user_question: str


class ReportSections(BaseModel):
    """
    Generated report sections based on the provided defect information, including detection summary,
    standards interpretation, technical risk, recommendation, and grounding disclaimer.
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class ReportGenerationResponse(BaseModel):
    """
    Report Generation Response model for returning the generated report sections, raw answer from 
    the model, sources used for generating the report, and any additional metadata related to the report generation process.
    """
    report: ReportSections
    raw_answer: str
    sources: list
    metadata: dict
