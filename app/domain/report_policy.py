"""
Report policy module defines the parameters for report retrieval and generation, as well as 
functions to infer grounding strength, acceptability status, and recommended actions based on the 
standards interpretation and recommendations.
"""
REPORT_POLICY = {
    "report_retrieval_top_k": 10,
    "report_retrieval_score_threshold": 0.35,
    "report_generation_temperature": 0.1,
    "report_generation_max_output_tokens": 900,
    "report_retrieval_per_query_top_k": 5,
    "report_retrieval_max_final_chunks": 8,
}


def infer_grounding_strength(
    standards_interpretation: str,
    grounding_disclaimer: str,
) -> str:
    """
    Infers the grounding strength (weak, moderate, strong) based on the presence of specific 
    markers in the standards interpretation and grounding disclaimer texts.
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
        "closest related",
        "suggests",
        "should be reviewed",
    ]

    if any(marker in standards_text or marker in disclaimer_text for marker in weak_markers):
        return "weak"

    if any(marker in standards_text or marker in disclaimer_text for marker in moderate_markers):
        return "moderate"

    return "strong"


def infer_interpretation_basis(
    standards_interpretation: str,
    grounding_disclaimer: str,
) -> str:
    """
    Infers the interpretation basis (direct, related_defect, insufficient_context) based on the 
    presence of specific markers in the standards interpretation and grounding disclaimer texts. 
    This helps to categorize the basis for the interpretation of the standards interpretation.
    """
    text = (standards_interpretation + " " + grounding_disclaimer).lower()

    related_markers = [
        "not explicitly defined",
        "not directly defined",
        "does not explicitly define",
        "does not directly define",
        "not explicitly present",
        "not fully detailed",
        "not clearly defined",
        "based on hints",
        "based on the provided hints",
        "based on related descriptions",
        "based on analogous",
        "based on the general principles",
        "the reference is a hint",
        "the reference hint",
        "while this defect is not explicitly defined",
        "while the standard identifies",
        "specific criteria are not detailed",
        "specific quantitative criteria",
        "not provided in the context",
        "not provided in the retrieved context",
        "the context does not provide explicit",
        "the assessment relies on",
    ]

    insufficient_markers = [
        "insufficient context",
        "limited context",
        "not enough information",
        "cannot determine definitively",
    ]

    if any(marker in text for marker in insufficient_markers):
        return "insufficient_context"

    if any(marker in text for marker in related_markers):
        return "related_defect"

    return "direct"


def infer_acceptability_status(
    standards_interpretation: str,
    recommendation: str,
    grounding_strength: str,
    interpretation_basis: str,
) -> str:
    """
    Infers the acceptability status (nonconforming, requires_additional_review, undetermined) 
    based on the presence of specific markers in the standards interpretation and recommendation 
    texts, as well as the grounding strength and interpretation basis.
    """
    standards_text = standards_interpretation.lower()
    recommendation_text = recommendation.lower()

    if grounding_strength == "weak" or interpretation_basis == "related_defect":
        return "requires_additional_review"

    nonconforming_markers = [
        "defect",
        "not acceptable",
        "shall not",
        "nonconforming",
        "reject",
        "electrical short",
        "electrical open",
    ]

    review_markers = [
        "evaluate",
        "review",
        "further investigation",
        "customer concurrence",
        "requires additional review",
    ]

    if any(
        marker in standards_text or marker in recommendation_text
        for marker in nonconforming_markers
    ):
        return "nonconforming"

    if any(marker in standards_text or marker in recommendation_text for marker in review_markers):
        return "requires_additional_review"

    return "undetermined"


def infer_recommended_action(
    recommendation: str,
    acceptability_status: str,
    grounding_strength: str,
    interpretation_basis: str,
) -> str:
    """
    Infers the recommended action (rework, repair, scrap, engineering_review, document_and_review)
    based on the presence of specific markers in the recommendation text, as well as the 
    acceptability status, grounding strength, and interpretation basis.
    """
    recommendation_text = recommendation.lower()

    if grounding_strength == "weak" or interpretation_basis == "related_defect":
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
