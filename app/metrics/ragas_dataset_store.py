"""
Ragas Dataset Store
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAGAS_DIR = BASE_DIR / "data" / "ragas"
RAGAS_DIR.mkdir(parents=True, exist_ok=True)

RAGAS_DATASET_FILE = RAGAS_DIR / "ragas_dataset.json"


def load_ragas_dataset() -> list[dict[str, Any]]:
    """
    Load the Ragas dataset from the JSON file. If the file does not exist or is invalid, return an 
    empty list.
    """
    if not RAGAS_DATASET_FILE.exists():
        return []

    try:
        with RAGAS_DATASET_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []
    except json.JSONDecodeError:
        return []


def append_ragas_sample(
    question: str,
    contexts: list[str],
    answer: str,
    ground_truth: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Append a new sample to the Ragas dataset. Each sample includes the question, contexts, answer, 
    ground truth (if available), and optional metadata. The dataset is stored as a JSON file, and 
    this function ensures that the new sample is added without overwriting existing data. If the 
    dataset file does not exist, it will be created. If the file is invalid, it will be reset to 
    an empty list before appending the new sample.
    """
    dataset = load_ragas_dataset()

    sample = {
        "question": question,
        "contexts": contexts,
        "answer": answer,
        "ground_truth": ground_truth,
        "metadata": {
            **(metadata or {}),
            "created_at": datetime.utcnow().isoformat(),
        },
    }

    dataset.append(sample)

    with RAGAS_DATASET_FILE.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)


def clear_ragas_dataset() -> None:
    """
    Clear the Ragas dataset by overwriting the JSON file with an empty list. This will remove all 
    existing samples from the dataset. If the file does not exist, it will be created with an 
    empty list. If the file is invalid, it will be reset to an empty list as well.
    """
    with RAGAS_DATASET_FILE.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def export_ragas_dataset() -> list[dict[str, Any]]:
    """
    Export the Ragas dataset by loading it from the JSON file and returning it as a list of 
    dictionaries.
    """
    return load_ragas_dataset()
