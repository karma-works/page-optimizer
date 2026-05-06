from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def score_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    metrics = metadata["metrics"]
    score = 100
    score -= int(metrics["overflow_blocks"]) * 30
    score -= int(metrics["empty_page_count"]) * 15
    score -= int(metrics["sparse_page_count"]) * 4
    score -= int(metrics.get("dangling_heading_count", 0)) * 18
    score -= int(metrics["widow_violations"]) * 8
    score = max(0, min(100, score))
    labels = []
    if metrics["overflow_blocks"]:
        labels.append("MARGIN_VIOLATION")
    if metrics["sparse_page_count"]:
        labels.append("SPARSE")
    if metrics.get("dangling_heading_count", 0):
        labels.append("AWKWARD_BREAK")
    if not labels:
        labels.append("GOOD")
    return {"score": score, "labels": labels, "metrics": metrics}


def score_metadata_file(path: str | Path) -> dict[str, Any]:
    return score_metadata(json.loads(Path(path).read_text()))
