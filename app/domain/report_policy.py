"""
Report policy module defines the parameters for report retrieval and generation, as well as functions to
infer grounding strength, acceptability status, and recommended actions based on the standards
interpretation and recommendations.
"""
REPORT_POLICY = {
    "report_retrieval_top_k": 5,
    "report_retrieval_score_threshold": 0.4,
    "report_generation_temperature": 0.1,
    "report_generation_max_output_tokens": 900,
}


def infer_grounding_strength(
    standards_interpretation: str,
    grounding_disclaimer: str,
) -> str:
    """
    Infer the grounding strength based on the presence of specific markers in the standards 
    interpretation and grounding disclaimer. The function checks for weak and moderate markers 
    to determine the overall grounding strength, which can be categorized as "weak", "moderate", 
    or "strong". This inference helps in assessing the reliability of the information provided 
    in the standards interpretation and grounding disclaimer, which is crucial for making 
    informed decisions regarding the acceptability status and recommended actions for the 
    analyzed conditions.
    """
    standards_text = standards_interpretation.lower()
    disclaimer_text = grounding_disclaimer.lower()

    weak_markers = [
        "does not contain specific criteria",
        "does not provide direct criteria",
        "does not directly define",
        "cannot be made",
        "insufficient",
        "not explicitly",
        "requires additional information",
    ]

    moderate_markers = [
        "can lead to",
        "may indicate",
        "related",
        "analogous",
        "suggests",
        "should be reviewed",
    ]

    if any(marker in standards_text or marker in disclaimer_text for marker in weak_markers):
        return "weak"

    if any(marker in standards_text or marker in disclaimer_text for marker in moderate_markers):
        return "moderate"

    return "strong"


def infer_acceptability_status(
    standards_interpretation: str,
    recommendation: str,
    grounding_strength: str,
) -> str:
    """
    Infer the acceptability status based on the presence of specific markers in the standards 
    interpretation and recommendation, as well as the grounding strength. The function checks for 
    nonconforming and review markers to determine the overall acceptability status, which can be 
    categorized as "nonconforming", "requires_additional_review", or "undetermined". This inference 
    helps in assessing the reliability of the information provided in the standards interpretation 
    and recommendation, as well as the grounding strength, which is crucial for making informed 
    decisions regarding the acceptability status and recommended actions for the analyzed conditions.
    """
    standards_text = standards_interpretation.lower()
    recommendation_text = recommendation.lower()

    if grounding_strength == "weak":
        return "requires_additional_review"

    nonconforming_markers = [
        "defect",
        "not acceptable",
        "shall not",
        "nonconforming",
        "reject",
        "short circuit",
        "electrical open",
        "unintended conductive connection",
    ]

    review_markers = [
        "evaluate",
        "review",
        "further investigation",
        "customer concurrence",
        "requires additional review",
    ]

    if any(marker in standards_text or marker in recommendation_text for marker in nonconforming_markers):
        return "nonconforming"

    if any(marker in standards_text or marker in recommendation_text for marker in review_markers):
        return "requires_additional_review"

    return "undetermined"


def infer_recommended_action(
    recommendation: str,
    acceptability_status: str,
    grounding_strength: str,
) -> str:
    """
    Infer the recommended action based on the recommendation text and acceptability status. 
    The function checks for specific markers in the recommendation text to determine the 
    appropriate recommended action, which can be categorized as "rework", "repair", "scrap",
    "engineering_review", "reject", or "document_and_review". This inference helps in guiding 
    the next steps for addressing the analyzed conditions based on the standards interpretation,
    recommendation, and grounding strength, which is crucial for making informed decisions 
    regarding the recommended actions for the analyzed conditions.
    """
    recommendation_text = recommendation.lower()

    if grounding_strength == "weak":
        return "engineering_review"

    if "rework" in recommendation_text:
        return "rework"
    if "repair" in recommendation_text:
        return "repair"
    if "scrap" in recommendation_text:
        return "scrap"
    if "review" in recommendation_text or acceptability_status == "requires_additional_review":
        return "engineering_review"
    if acceptability_status == "nonconforming":
        return "reject"

    return "document_and_review"


def infer_interpretation_basis(
    standards_interpretation: str,
    grounding_disclaimer: str,
) -> str:
    """
    Infer the interpretation basis based on the presence of specific markers in the standards
    interpretation and grounding disclaimer. The function checks for related_defect and
    insufficient_context markers to determine the overall interpretation basis, which can be
    categorized as "related_defect", "insufficient_context", or "direct". This inference helps in
    assessing the basis for the standards interpretation, which is crucial for understanding the
    context and rationale behind the interpretation, as well as for making informed decisions
    regarding the acceptability status and recommended actions for the analyzed conditions.
    """
    standards_text = standards_interpretation.lower()
    disclaimer_text = grounding_disclaimer.lower()

    if (
        "does not directly define" in standards_text
        or "related conditions" in standards_text
        or "related concept" in standards_text
        or "analogous" in standards_text
    ):
        return "related_defect"

    if (
        "insufficient" in standards_text
        or "cannot be made" in disclaimer_text
        or "does not contain explicit criteria" in disclaimer_text
    ):
        return "insufficient_context"

    return "direct"
