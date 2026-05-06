from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def rate_document(sample: str, pdf: str, screenshots: list[str], rating: int, notes: str = "", output: str | Path = "renders/ratings.jsonl") -> dict[str, object]:
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")
    record = {
        "sample": sample,
        "pdf": pdf,
        "screenshots": screenshots,
        "rating": rating,
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return record
