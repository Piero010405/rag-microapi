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
    interpretation and grounding disclaimer. The function checks for weak and moderate markers to 
    determine the overall grounding strength, which can be classified as "weak", "moderate", or 
    "strong". If any weak markers are found, the grounding strength is classified as "weak". If any 
    moderate markers are found and no weak markers are present, the grounding strength is classified as
    "moderate". If neither weak nor moderate markers are found, the grounding strength is classified as 
    "strong".
    """
    standards_text = standards_interpretation.lower()
    disclaimer_text = grounding_disclaimer.lower()

    weak_markers = [
        "does not contain specific criteria",
        "does not provide direct criteria",
        "cannot be made",
        "insufficient",
        "not explicitly",
        "requires additional information",
    ]

    moderate_markers = [
        "can lead to",
        "may indicate",
        "related",
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
) -> str:
    """
    Infer the recommended action based on the presence of specific markers in the recommendation and the
    acceptability status. The function checks for markers indicating specific actions such as "rework",
    "repair", "scrap", and "review". If any of these markers are found in the recommendation text, 
    the corresponding action is returned. If the acceptability status indicates that additional 
    review is required, the recommended action is set to "engineering_review". If the acceptability 
    status indicates that the item is nonconforming, the recommended action is set to "reject". 
    If none of the specific markers are found and the acceptability status does not indicate a 
    need for review or rejection, the default recommended action is "document_and_review".
    """
    recommendation_text = recommendation.lower()

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
