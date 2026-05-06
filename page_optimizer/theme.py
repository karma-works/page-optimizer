from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import Theme


def _mm_value(value: Any, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text.endswith("mm"):
        text = text[:-2]
    return float(text)


def load_theme(path: str | Path | None = None) -> Theme:
    if path is None:
        return Theme()
    data = yaml.safe_load(Path(path).read_text()) or {}
    margins = data.get("margins", {})
    fonts = data.get("fonts", {})
    page = data.get("page", {})
    sizes = data.get("sizes", {})
    return Theme(
        page_size=str(page.get("size", "A4")),
        top_mm=_mm_value(margins.get("top"), 24),
        right_mm=_mm_value(margins.get("right"), 20),
        bottom_mm=_mm_value(margins.get("bottom"), 24),
        left_mm=_mm_value(margins.get("left"), 20),
        body_font=str(fonts.get("body", "Helvetica")),
        heading_font=str(fonts.get("heading", "Helvetica-Bold")),
        mono_font=str(fonts.get("mono", "Courier")),
        body_size=int(sizes.get("body", 10)),
        heading_size=int(sizes.get("heading", 16)),
        leading=int(sizes.get("leading", 13)),
    )
