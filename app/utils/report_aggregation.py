"""
Report aggregation utility for processing multiple defect detections into a summarized report 
format. This module provides functionality to take a list of individual defect detections, 
each containing details such as defect class, confidence level, area, severity, location, and 
reference information, and aggregate this data into a cohesive summary. The aggregation 
includes calculating average confidence and area, determining the most common severity level,
summarizing locations, and providing a reference hint if available. This utility is essential 
for generating comprehensive reports that can be used for further analysis and decision-making 
in the context of printed board manufacturing defect assessment.
"""
from collections import Counter


def aggregate_detection_payload(detections: list[dict]) -> dict:
    """
    Agregate a list of defect detections into a summarized report format. Each detection in the 
    list should be a dictionary containing at least the following keys:
    - "defect_class": The class of the defect (e.g., "short_circuit", "spur", etc.).
    - "confidence": A numerical value representing the confidence level of the detection
    - "area_mm2": A numerical value representing the area of the detected defect in square 
    millimeters
    - "severity": A string representing the severity level of the defect
    - "location": A string describing the location of the defect on the printed board
    - "reference": (Optional) A string providing additional reference information about the defect
    """
    if not detections:
        raise ValueError("detections list cannot be empty")

    classes = [d["defect_class"] for d in detections]
    unique_classes = sorted(set(classes))

    if len(unique_classes) > 1:
        raise ValueError(
            "Mixed-class detections are not yet supported in a single report request."
        )

    defect_class = unique_classes[0]

    instances_count = len(detections)
    avg_confidence = sum(d["confidence"] for d in detections) / instances_count
    avg_area = sum(d["area_mm2"] for d in detections) / instances_count

    severities = [d["severity"] for d in detections]
    severity_counter = Counter(severities)
    dominant_severity = severity_counter.most_common(1)[0][0]

    locations = [d["location"] for d in detections]
    unique_locations = sorted(set(locations))
    location_summary = ", ".join(unique_locations)

    references = [d.get("reference") for d in detections if d.get("reference")]
    reference_hint = references[0] if references else None

    return {
        "defect_class": defect_class,
        "instances_count": instances_count,
        "confidence_avg": avg_confidence,
        "average_area_mm2": avg_area,
        "severity": dominant_severity,
        "location_summary": location_summary,
        "reference_hint": reference_hint,
    }
