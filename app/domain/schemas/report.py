""""
Report schemas
"""
from pydantic import BaseModel, Field


class DetectionInstance(BaseModel):
    """
    Defect detection instance representing a single detected defect with its associated 
    attributes. This model includes fields for severity, defect class, confidence level, 
    location on the printed board, dimensions (width and height in millimeters), calculated 
    area in square millimeters, and an optional reference string for additional context or 
    information about the defect.
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
    Report generation request model for aggregating multiple defect detections into a 
    comprehensive report. This model includes a list of defect detection instances, along 
    with optional fields for user questions, standard targets, product class, and board side. 
    The model is designed to facilitate the generation of detailed reports based on the 
    aggregated data from multiple defect detections, allowing for informed analysis and 
    decision-making in the context of printed board manufacturing defect assessment.
    """
    detections: list[DetectionInstance] = Field(min_length=1)
    user_question: str | None = None
    standard_target: str | None = None
    product_class: str | None = None
    board_side: str | None = None


class ReportSections(BaseModel):
    """
    Report sections model representing the structured components of a generated report. 
    This model includes fields for the detection summary, standards interpretation, technical
    risk assessment, recommendation, and a grounding disclaimer. Each field is designed to 
    capture specific aspects of the report, providing a comprehensive overview of the defect
    detections and their implications in the context of printed board manufacturing defect
    assessment.
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class ReportGenerationResponse(BaseModel):
    """
    Report generation response model representing the output of the report generation process. 
    This model includes fields for the structured report sections, the full report text, the 
    raw answer from the report generation process, a list of sources used in the report, 
    metadata about the report generation, normalized defect name, recommended standard 
    target, inspection scope, grounding strength, acceptability status, recommended 
    action, interpretation basis, and applicable standard. This comprehensive model is 
    designed to capture all relevant information resulting from the report generation 
    process, providing a detailed and informative response for further analysis and 
    decision-making in the context of printed board manufacturing defect assessment.
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
