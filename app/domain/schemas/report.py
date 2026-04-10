""""
Report schemas
"""
from pydantic import BaseModel


class ReportGenerationRequest(BaseModel):
    """
    Report generation request schema defines the structure of the input data required for generating 
    a report. It includes details about the defect, such as its class, count, location, average area
    and confidence, severity, user question, standard target, product class, and board side.
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
    Report sections schema defines the structure of the different sections that make up the 
    generated report. Each section provides specific information related to the analysis of the 
    defect and the applicable standards, including a summary of the detection results, interpretation 
    of the standards, assessment of the technical risk, recommendations for addressing the defect, 
    and any disclaimers regarding the grounding of the recommendations.
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class ReportGenerationResponse(BaseModel):
    """
    Report generation response schema defines the structure of the output data generated after processing
    the report generation request. It includes the different sections of the report, the full text of
    the report, the raw answer from the processing, the sources used for generating the report, and
    various metadata related to the analysis, such as the normalized defect name, recommended standard
    target, inspection scope, grounding strength, acceptability status, recommended action,
    interpretation basis, and applicable standard. This structured response allows for easy consumption
    and further processing of the generated report, as well as for maintaining consistency in the
    representation of the analysis results and recommendations.
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
