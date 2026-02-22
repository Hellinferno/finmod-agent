"""
JSON export engine — structured JSON output with all valuation data.
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from fmva.core.schemas import ValuationResult


def export_to_json(result: ValuationResult, filepath: str) -> str:
    """Export full valuation result to structured JSON."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = result.model_dump(mode="json")
    data["_exported_at"] = datetime.utcnow().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"JSON exported to {filepath}")
    return str(path)
