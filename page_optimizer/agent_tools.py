from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .judge import score_metadata_file
from .parser import parse_markdown
from .patches import apply_patch_to_markdown, validate_patch
from .rasterizer import rasterize_pdf
from .renderer import PdfRenderer
from .theme import load_theme


def render_document(markdown_path: str, theme_path: str = "themes/default.yml", patch_path: str | None = None, output_dir: str = "renders") -> dict[str, Any]:
    markdown = Path(markdown_path).read_text()
    patch = json.loads(Path(patch_path).read_text()) if patch_path else {"version": 1, "actions": []}
    errors = validate_patch(patch)
    if errors:
        return {"ok": False, "errors": errors}
    patched, counters = apply_patch_to_markdown(markdown, patch)
    doc = parse_markdown(patched, counters=counters)
    stem = Path(markdown_path).stem
    renderer = PdfRenderer(load_theme(theme_path))
    result = renderer.render(doc, Path(output_dir) / "pdf" / f"{stem}.pdf", Path(output_dir) / "metadata" / f"{stem}.json")
    pngs = rasterize_pdf(result.pdf_path, Path(output_dir) / "png")
    return {"ok": True, "pdf": result.pdf_path, "metadata": result.metadata_path, "pngs": pngs, "metrics": result.metrics}


def evaluate_layout(metadata_path: str) -> dict[str, Any]:
    return score_metadata_file(metadata_path)


def propose_patch(metadata_path: str) -> dict[str, Any]:
    judged = evaluate_layout(metadata_path)
    actions: list[dict[str, Any]] = []
    if judged["metrics"]["sparse_page_count"] > 0:
        actions.append({"op": "set_counter", "name": "12", "value": 1})
    return {"version": 1, "actions": actions, "reason": "Enable optional content when deterministic metrics report sparse pages."}


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "render_document": render_document,
    "evaluate_layout": evaluate_layout,
    "propose_patch": propose_patch,
}
