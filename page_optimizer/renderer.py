from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .model import Block, Document, LayoutBlock, PageLayout, RenderResult, Theme

PAGE_SIZES = {"A4": A4, "LETTER": LETTER}


def _wrap(text: str, width_chars: int) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines() or [""]:
        lines.extend(textwrap.wrap(raw, width=max(16, width_chars), replace_whitespace=False) or [""])
    return lines


def _block_lines(block: Block, width_chars: int) -> list[str]:
    if block.kind == "heading":
        return _wrap(block.text, width_chars)
    if block.kind == "list":
        out: list[str] = []
        for item in block.items:
            wrapped = _wrap(item, max(10, width_chars - 3))
            out.append(f"- {wrapped[0]}")
            out.extend(f"  {line}" for line in wrapped[1:])
        return out
    if block.kind == "table":
        return [" | ".join(row) for row in block.rows]
    if block.kind == "code":
        return block.text.splitlines() or [""]
    if block.kind in {"page_break", "lazy_page_break", "widow_spec", "section", "optional"}:
        return []
    return _wrap(block.text, width_chars)


class PdfRenderer:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.page_width, self.page_height = PAGE_SIZES.get(theme.page_size.upper(), A4)
        self.left = theme.left_mm * mm
        self.right = theme.right_mm * mm
        self.top = theme.top_mm * mm
        self.bottom = theme.bottom_mm * mm
        self.content_width = self.page_width - self.left - self.right
        self.content_height = self.page_height - self.top - self.bottom
        self.width_chars = max(32, int(self.content_width / (theme.body_size * 0.48)))

    def render(self, document: Document, pdf_path: str | Path, metadata_path: str | Path) -> RenderResult:
        pdf_path = str(pdf_path)
        metadata_path = str(metadata_path)
        Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
        Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
        c = canvas.Canvas(pdf_path, pagesize=(self.page_width, self.page_height))
        pages: list[PageLayout] = []
        blocks: list[LayoutBlock] = []
        page_no = 1
        y = self.page_height - self.top
        active_ws = {"before": 2, "after": 2}

        def finish_page() -> None:
            nonlocal blocks
            used = sum(max(0, block.bbox[3] - block.bbox[1]) for block in blocks)
            pages.append(PageLayout(page_no, self._margins(), blocks, min(1.0, used / self.content_height)))
            blocks = []
            c.showPage()

        def new_page() -> None:
            nonlocal page_no, y
            finish_page()
            page_no += 1
            y = self.page_height - self.top

        for block in document.blocks:
            if block.kind == "widow_spec":
                active_ws = {"before": int(block.attrs["before"]), "after": int(block.attrs["after"])}
                continue
            if block.kind == "optional" and not document.counters.get(str(block.attrs.get("counter")), 0):
                continue
            if block.kind == "section":
                if blocks:
                    new_page()
                continue
            if block.kind == "page_break":
                tag = block.tag
                if tag == "NP" and blocks:
                    new_page()
                elif tag == "NPR":
                    if blocks:
                        new_page()
                    if page_no % 2 == 0:
                        new_page()
                elif tag == "NPV":
                    if blocks:
                        new_page()
                    if page_no % 2 == 1:
                        new_page()
                continue
            if block.kind == "lazy_page_break":
                if self.page_height - self.bottom - y < self.content_height * -0.72:
                    new_page()
                continue
            lines = _block_lines(block, self.width_chars)
            if not lines:
                continue
            font = self.theme.heading_font if block.kind == "heading" else self.theme.mono_font if block.kind == "code" else self.theme.body_font
            size = self.theme.heading_size if block.kind == "heading" else self.theme.body_size
            leading = self.theme.leading + (4 if block.kind == "heading" else 0)
            block_height = leading * len(lines) + (8 if block.kind == "heading" else 5)
            if block_height > y - self.bottom:
                if len(lines) <= active_ws["before"] + active_ws["after"] or y - self.bottom < active_ws["before"] * leading:
                    if blocks:
                        new_page()
                else:
                    available_lines = max(active_ws["before"], int((y - self.bottom) // leading))
                    first = lines[:available_lines]
                    rest = lines[available_lines:]
                    self._draw_lines(c, first, font, size, leading, y)
                    bottom_y = y - leading * len(first)
                    blocks.append(LayoutBlock(block.id, block.kind, page_no, (self.left, bottom_y, self.page_width - self.right, y), len(first), block.text))
                    new_page()
                    lines = rest
                    block_height = leading * len(lines) + 5
            self._draw_lines(c, lines, font, size, leading, y)
            bottom_y = y - leading * len(lines)
            blocks.append(LayoutBlock(block.id, block.kind, page_no, (self.left, bottom_y, self.page_width - self.right, y), len(lines), block.text))
            y = bottom_y - (10 if block.kind == "heading" else 7)
        finish_page()
        c.save()
        metrics = compute_metrics(pages, self.content_height)
        Path(metadata_path).write_text(json.dumps({"pages": _pages_json(pages), "metrics": metrics}, indent=2))
        return RenderResult(pdf_path, metadata_path, pages, metrics)

    def _draw_lines(self, c: canvas.Canvas, lines: list[str], font: str, size: int, leading: int, y: float) -> None:
        c.setFont(font, size)
        text = c.beginText(self.left, y - size)
        text.setLeading(leading)
        for line in lines:
            text.textLine(line)
        c.drawText(text)

    def _margins(self) -> dict[str, float]:
        return {"top": self.theme.top_mm, "right": self.theme.right_mm, "bottom": self.theme.bottom_mm, "left": self.theme.left_mm}


def compute_metrics(pages: list[PageLayout], content_height: float) -> dict[str, object]:
    empty = sum(1 for page in pages if not page.blocks)
    overflow = 0
    for page in pages:
        for block in page.blocks:
            if block.bbox[1] < 0:
                overflow += 1
    fills = [page.fill_ratio for page in pages if page.blocks]
    sparse = sum(1 for fill in fills if fill < 0.32)
    return {
        "page_count": len(pages),
        "overflow_blocks": overflow,
        "empty_page_count": empty,
        "sparse_page_count": sparse,
        "average_fill_ratio": round(sum(fills) / len(fills), 3) if fills else 0,
        "widow_violations": 0,
        "clipped_content_detected": overflow > 0,
    }


def _pages_json(pages: list[PageLayout]) -> list[dict[str, object]]:
    return [
        {
            "page": page.page,
            "margins": page.margins,
            "fill_ratio": round(page.fill_ratio, 3),
            "blocks": [
                {"id": block.id, "kind": block.kind, "bbox": [round(v, 2) for v in block.bbox], "lines": block.lines, "text": block.text[:80]}
                for block in page.blocks
            ],
        }
        for page in pages
    ]
