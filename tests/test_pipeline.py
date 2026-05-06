from pathlib import Path

from page_optimizer.agent_tools import render_document
from page_optimizer.agent_tools import propose_patch
from page_optimizer.generator import write_samples
from page_optimizer.hitl import rate_document
from page_optimizer.judge import score_metadata, score_metadata_file
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


def test_judge_labels_dangling_heading_as_awkward_break():
    judged = score_metadata(
        {
            "metrics": {
                "page_count": 2,
                "overflow_blocks": 0,
                "empty_page_count": 0,
                "sparse_page_count": 1,
                "dangling_heading_count": 1,
                "dangling_headings": [{"heading_text": "Section 2", "heading_page": 1, "next_content_page": 2}],
                "average_fill_ratio": 0.5,
                "widow_violations": 0,
                "clipped_content_detected": False,
            }
        }
    )
    assert "AWKWARD_BREAK" in judged["labels"]
    assert judged["score"] == 78


def test_agent_proposes_break_repair_for_dangling_heading(tmp_path):
    metadata = tmp_path / "metadata.json"
    metadata.write_text(
        """
        {
          "metrics": {
            "page_count": 2,
            "overflow_blocks": 0,
            "empty_page_count": 0,
            "sparse_page_count": 1,
            "dangling_heading_count": 1,
            "dangling_headings": [{"heading_text": "Section 2", "heading_page": 1, "next_content_page": 2}],
            "average_fill_ratio": 0.5,
            "widow_violations": 0,
            "clipped_content_detected": false
          }
        }
        """
    )
    patch = propose_patch(str(metadata))
    assert patch["actions"] == [{"op": "remove_tag", "anchor": "first_dangling_heading_after", "tag": "<NP>"}]


def test_sample_generator_writes_markdown(tmp_path):
    paths = write_samples(tmp_path)
    assert len(paths) == 3
    assert all(path.suffix == ".md" and "lorem" in path.read_text().lower() for path in paths)
