from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Block:
    id: str
    kind: str
    text: str = ""
    source_line: int = 0
    level: int = 0
    items: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    tag: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    blocks: list[Block]
    counters: dict[str, int] = field(default_factory=dict)


@dataclass
class Theme:
    page_size: str = "A4"
    top_mm: float = 24
    right_mm: float = 20
    bottom_mm: float = 24
    left_mm: float = 20
    body_font: str = "Helvetica"
    heading_font: str = "Helvetica-Bold"
    mono_font: str = "Courier"
    body_size: int = 10
    heading_size: int = 16
    leading: int = 13


@dataclass
class LayoutBlock:
    id: str
    kind: str
    page: int
    bbox: tuple[float, float, float, float]
    lines: int
    text: str = ""


@dataclass
class PageLayout:
    page: int
    margins: dict[str, float]
    blocks: list[LayoutBlock]
    fill_ratio: float


@dataclass
class RenderResult:
    pdf_path: str
    metadata_path: str
    pages: list[PageLayout]
    metrics: dict[str, Any]
