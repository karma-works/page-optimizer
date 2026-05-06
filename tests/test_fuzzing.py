from page_optimizer.generator import generate_document
from page_optimizer.parser import parse_markdown
from page_optimizer.renderer import PdfRenderer
from page_optimizer.theme import load_theme


def test_synthetic_fuzz_documents_render(tmp_path):
    renderer = PdfRenderer(load_theme())
    for seed in range(5):
        doc = parse_markdown(generate_document(seed=seed, sections=3, stress=seed % 2 == 0))
        result = renderer.render(doc, tmp_path / f"fuzz-{seed}.pdf", tmp_path / f"fuzz-{seed}.json")
        assert result.metrics["page_count"] >= 1
        assert result.metrics["overflow_blocks"] == 0
