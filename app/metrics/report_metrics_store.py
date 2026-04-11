"""
Report Metrics Store
"""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
METRICS_DIR = BASE_DIR / "data" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

REPORT_METRICS_FILE = METRICS_DIR / "report_metrics.jsonl"


def append_report_metric(record: dict) -> None:
    """
    Append a single report metric record to the metrics file. Each record is stored as a JSON line
    with a timestamp.
    """
    record = {
        **record,
        "timestamp": datetime.utcnow().isoformat(),
    }

    with REPORT_METRICS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_report_metrics() -> list[dict]:
    """
    Load all report metric records from the metrics file. Each line is parsed as a JSON object and
    returned as a list of dictionaries.
    """
    if not REPORT_METRICS_FILE.exists():
        return []

    rows: list[dict] = []
    with REPORT_METRICS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def compute_report_metrics(records: list[dict]) -> dict:
    """
    Compute aggregated metrics from a list of report metric records. This includes distributions of 
    various fields, latency statistics, defect class coverage, and consistency analysis based on
    grounding strength and recommended action.
    """
    if not records:
        return {
            "total_reports": 0,
            "grounding_distribution": {},
            "interpretation_distribution": {},
            "acceptability_distribution": {},
            "recommended_action_distribution": {},
            "latency": {
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
            },
            "defect_class_coverage": {
                "unique_classes": 0,
                "classes": [],
            },
            "consistency": {
                "consistent_reports": 0,
                "inconsistent_reports": 0,
                "consistency_rate": 0.0,
            },
        }

    total = len(records)

    grounding_counter = Counter(r.get("grounding_strength", "unknown") for r in records)
    interpretation_counter = Counter(r.get("interpretation_basis", "unknown") for r in records)
    acceptability_counter = Counter(r.get("acceptability_status", "unknown") for r in records)
    action_counter = Counter(r.get("recommended_action", "unknown") for r in records)

    latencies = [r.get("latency_ms", 0) for r in records if isinstance(r.get("latency_ms", 0), (int, float))]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    classes = sorted(set(r.get("defect_class", "unknown") for r in records))

    inconsistent_reports = 0
    for r in records:
        grounding = r.get("grounding_strength")
        action = r.get("recommended_action")
        if grounding == "weak" and action in ["reject", "rework", "repair"]:
            inconsistent_reports += 1

    consistent_reports = total - inconsistent_reports
    consistency_rate = consistent_reports / total if total else 0.0

    return {
        "total_reports": total,
        "grounding_distribution": dict(grounding_counter),
        "interpretation_distribution": dict(interpretation_counter),
        "acceptability_distribution": dict(acceptability_counter),
        "recommended_action_distribution": dict(action_counter),
        "latency": {
            "avg_ms": round(avg_latency, 2),
            "min_ms": min_latency,
            "max_ms": max_latency,
        },
        "defect_class_coverage": {
            "unique_classes": len(classes),
            "classes": classes,
        },
        "consistency": {
            "consistent_reports": consistent_reports,
            "inconsistent_reports": inconsistent_reports,
            "consistency_rate": round(consistency_rate, 4),
        },
    }
