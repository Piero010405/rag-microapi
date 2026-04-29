""""
Report schemas
"""
from pydantic import BaseModel, Field


class DetectionInstance(BaseModel):
    """
    Detection instance schema
    """
    severity: str
    defect_class: str
    confidence: float
    location: str
    width_mm: float
    height_mm: float
    area_mm2: float
    reference: str | None = None


class ReportGenerationRequest(BaseModel):
    """
    Report generation request schema
    """
    path_to_labeled_img: str | None = None
    detections: list[DetectionInstance] = Field(min_length=1)
    standard_target: str | None = None
    product_class: str | None = None
    board_side: str | None = None
    user_question: str | None = None


class ReportSections(BaseModel):
    """
    Report sections schema
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class SingleClassReportResult(BaseModel):
    """
    Single class report result schema
    """
    report: ReportSections
    report_text: str
    raw_answer: str
    sources: list
    metadata: dict
    normalized_defect_name: str
    recommended_standard_target: str
    inspection_scope: str
    grounding_strength: str
    acceptability_status: str
    recommended_action: str
    interpretation_basis: str
    applicable_standard: str
    path_to_labeled_img: str | None = None


class ClassReportItem(BaseModel):
    """
    Class report item schema
    """
    defect_class: str
    instances_count: int
    result: SingleClassReportResult


class ReportSummary(BaseModel):
    """
    Report summary schema
    """
    total_detections: int
    unique_defect_classes: int
    classes: list[str]


class ReportGenerationResponse(BaseModel):
    """
    Report generation response schema
    """
    path_to_labeled_img: str | None = None
    summary: ReportSummary
    class_reports: list[ClassReportItem]
