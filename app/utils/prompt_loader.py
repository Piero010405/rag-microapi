"""
Prompt loader module
"""
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "infrastructure" / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")
