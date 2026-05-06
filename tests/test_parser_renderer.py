from pathlib import Path

from page_optimizer.generator import generate_document
from page_optimizer.parser import parse_markdown
from page_optimizer.renderer import PdfRenderer
from page_optimizer.theme import load_theme


def test_parser_recognizes_layout_tags():
    doc = parse_markdown("# A\n\n<NP>\n\n<WS,2,3,5,1>\n\nText")
    assert [block.kind for block in doc.blocks] == ["heading", "page_break", "widow_spec", "paragraph"]


def test_renderer_produces_metadata_without_overflow(tmp_path):
    doc = parse_markdown(generate_document(seed=3, sections=2))
    result = PdfRenderer(load_theme()).render(doc, tmp_path / "out.pdf", tmp_path / "out.json")
    assert Path(result.pdf_path).exists()
    assert result.metrics["page_count"] >= 1
    assert result.metrics["overflow_blocks"] == 0


def test_npr_starts_recto_page_after_content(tmp_path):
    doc = parse_markdown("# A\n\nText\n\n<NPR>\n\n# B")
    result = PdfRenderer(load_theme()).render(doc, tmp_path / "recto.pdf", tmp_path / "recto.json")
    heading_b = [b for p in result.pages for b in p.blocks if b.text == "B"][0]
    assert heading_b.page % 2 == 1
