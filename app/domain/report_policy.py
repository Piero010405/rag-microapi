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
    text = (standards_interpretation + " " + grounding_disclaimer).lower()

    # 🔴 PRIORIDAD MÁXIMA → NO DEFINICIÓN EXPLÍCITA
    if any(
        phrase in text
        for phrase in [
            "not explicitly defined",
            "not directly defined",
            "not defined in the standard",
            "does not explicitly define",
            "no explicit criteria",
            "no direct definition",
            "not fully detailed",
            "not clearly defined",
        ]
    ):
        return "related_defect"

    # 🔴 ANALOGÍAS
    if any(
        phrase in text
        for phrase in [
            "related to",
            "analogous to",
            "similar to",
            "based on related",
        ]
    ):
        return "related_defect"

    # 🔴 FALTA DE CONTEXTO
    if any(
        phrase in text
        for phrase in [
            "insufficient context",
            "limited context",
            "not enough information",
        ]
    ):
        return "insufficient_context"

    return "direct"


def infer_acceptability_status(
    standards_interpretation: str,
    recommendation: str,
    grounding_strength: str,
    interpretation_basis: str,
) -> str:
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

    if any(marker in standards_text or marker in recommendation_text for marker in nonconforming_markers):
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
