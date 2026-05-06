from pathlib import Path

from page_optimizer.agent_tools import render_document
from page_optimizer.generator import write_samples
from page_optimizer.hitl import rate_document
from page_optimizer.judge import score_metadata_file
from page_optimizer.rasterizer import rasterize_pdf


def test_golden_render_metadata_and_png(tmp_path):
    sample = tmp_path / "sample.md"
    sample.write_text("# Golden\n\nLorem ipsum " * 80)
    rendered = render_document(str(sample), output_dir=str(tmp_path / "renders"))
    assert rendered["ok"]
    assert Path(rendered["pdf"]).exists()
    assert Path(rendered["metadata"]).exists()
    assert rendered["pngs"]
    assert Path(rendered["pngs"][0]).exists()
    judged = score_metadata_file(rendered["metadata"])
    assert judged["score"] > 50


def test_human_rating_records_jsonl(tmp_path):
    record = rate_document("sample.md", "sample.pdf", ["page.png"], 4, "Readable", tmp_path / "ratings.jsonl")
    assert record["rating"] == 4
    assert (tmp_path / "ratings.jsonl").read_text().strip()


def test_sample_generator_writes_markdown(tmp_path):
    paths = write_samples(tmp_path)
    assert len(paths) == 3
    assert all(path.suffix == ".md" and "lorem" in path.read_text().lower() for path in paths)
