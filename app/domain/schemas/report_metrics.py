"""
Report Metrics Schema
"""
from pydantic import BaseModel


class LatencyMetrics(BaseModel):
    """
    Latency metrics for report processing, including average, minimum, and maximum latency in 
    milliseconds.
    """
    avg_ms: float
    min_ms: float
    max_ms: float


class DefectClassCoverage(BaseModel):
    """
    Defect class coverage metrics, including the number of unique defect classes and a list of those
    classes.
    """
    unique_classes: int
    classes: list[str]


class ConsistencyMetrics(BaseModel):
    """
    Consistency metrics based on grounding strength and recommended action, including the number of
    consistent and inconsistent reports, as well as the overall consistency rate.
    """
    consistent_reports: int
    inconsistent_reports: int
    consistency_rate: float


class ReportMetricsResponse(BaseModel):
    """
    Report metrics response schema that encapsulates all aggregated metrics related to report 
    processing, including distributions of grounding strength, interpretation basis, acceptability 
    status, recommended actions, latency statistics, defect class coverage, and consistency analysis.
    """
    total_reports: int
    grounding_distribution: dict
    interpretation_distribution: dict
    acceptability_distribution: dict
    recommended_action_distribution: dict
    latency: LatencyMetrics
    defect_class_coverage: DefectClassCoverage
    consistency: ConsistencyMetrics
