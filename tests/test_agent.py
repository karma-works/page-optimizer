from page_optimizer.patches import validate_patch
from page_optimizer.react_agent import ReActAgent


def test_action_safety_rejects_unknown_ops():
    assert validate_patch({"version": 1, "actions": [{"op": "delete_file"}]})


def test_react_trajectory_converges_on_small_document(tmp_path):
    sample = tmp_path / "small.md"
    sample.write_text("# Small\n\nLorem ipsum dolor sit amet.\n")
    result = ReActAgent().optimize(str(sample), iterations=2, output_dir=str(tmp_path / "renders"))
    actions = [step["action"] for step in result["trajectory"]]
    assert "render_document" in actions
    assert "evaluate_layout" in actions
    assert len(result["trajectory"]) <= 6
