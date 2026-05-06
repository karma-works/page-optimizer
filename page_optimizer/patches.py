from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_ACTIONS = {
    "set_margin_profile",
    "insert_tag",
    "remove_tag",
    "replace_tag",
    "insert_spacing",
    "remove_spacing",
    "set_ws",
    "reset_ws",
    "set_counter",
    "unset_counter",
}


def load_patch(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {"version": 1, "actions": []}
    return json.loads(Path(path).read_text())


def validate_patch(patch: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if patch.get("version") != 1:
        errors.append("patch version must be 1")
    for idx, action in enumerate(patch.get("actions", [])):
        op = action.get("op")
        if op not in ALLOWED_ACTIONS:
            errors.append(f"actions[{idx}] has unsupported op {op!r}")
        if op in {"insert_tag", "remove_tag", "replace_tag", "set_ws", "reset_ws"} and not action.get("anchor"):
            errors.append(f"actions[{idx}] requires anchor")
    return errors


def apply_patch_to_markdown(markdown: str, patch: dict[str, Any]) -> tuple[str, dict[str, int]]:
    counters: dict[str, int] = {}
    lines = markdown.splitlines()
    for action in patch.get("actions", []):
        op = action.get("op")
        if op == "set_counter":
            counters[str(action["name"])] = int(action.get("value", 1))
        elif op == "unset_counter":
            counters[str(action["name"])] = 0
        elif op == "insert_tag":
            anchor = int(action.get("anchor_line", len(lines) + 1))
            lines.insert(max(0, min(anchor - 1, len(lines))), str(action["tag"]))
        elif op == "replace_tag":
            old = str(action.get("from", ""))
            new = str(action.get("to", ""))
            lines = [new if line.strip() == old else line for line in lines]
        elif op == "remove_tag":
            tag = str(action.get("tag", ""))
            lines = [line for line in lines if line.strip() != tag]
    return "\n".join(lines) + "\n", counters
