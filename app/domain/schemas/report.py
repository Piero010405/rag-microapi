""""
Report schemas
"""
from pydantic import BaseModel


class ReportGenerationRequest(BaseModel):
    """
    Report generation request schema defines the parameters required for generating a report based on a 
    user question and defect information. It includes fields for the user's question, details about the
    defect such as its class, count, location, average area, confidence level, severity, and 
    optional fields for standard target, product class, and board side.
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
    Report sections schema defines the structure of the generated report, including sections for detection summary, standards interpretation, technical risk assessment, recommendation, 
    and grounding disclaimer. Each section is represented as a string, and the schema serves 
    as a blueprint for the content of the report generated in response to a user's question 
    about a defect. The sections are designed to provide a comprehensive analysis of the defect,
    including a summary of the detection process, an interpretation of relevant standards, an 
    assessment of technical risks, specific recommendations for action, and any disclaimers 
    regarding the grounding of the report.
    """
    detection_summary: str
    standards_interpretation: str
    technical_risk: str
    recommendation: str
    grounding_disclaimer: str


class ReportGenerationResponse(BaseModel):
    """
    Report generation response schema defines the structure of the response returned after generating 
    a report. It includes fields for the report sections, the full text of the report, the raw 
    answer from the language model, a list of sources used in the report, metadata about the 
    report generation process, and additional fields for normalized defect name, recommended 
    standard target, inspection scope, grounding strength, acceptability status, and recommended 
    action. This schema serves as a comprehensive representation of the generated report and 
    its associated information.
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
