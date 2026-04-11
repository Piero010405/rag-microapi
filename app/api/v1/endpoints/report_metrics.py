"""
Report Metrics API Endpoint
"""
from fastapi import APIRouter

from app.domain.schemas.report_metrics import ReportMetricsResponse
from app.metrics.report_metrics_store import compute_report_metrics, load_report_metrics

router = APIRouter(prefix="/report", tags=["report-metrics"])


@router.get("/metrics", response_model=ReportMetricsResponse)
async def get_report_metrics() -> ReportMetricsResponse:
    """
    Get aggregated metrics for all processed reports, including:
        - Total number of reports processed
        - Distribution of grounding strength
        - Distribution of interpretation basis
        - Distribution of acceptability status
        - Distribution of recommended actions
        - Latency statistics
        - Defect class coverage
        - Consistency analysis
    """
    records = load_report_metrics()
    metrics = compute_report_metrics(records)
    return ReportMetricsResponse(**metrics)
