from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import requests

from .agent_tools import TOOLS


SYSTEM_PROMPT = """You are a ReAct visual layout optimizer.
Use thoughts, actions, observations, and a final answer. Valid actions are:
render_document(markdown_path, theme_path, patch_path, output_dir)
evaluate_layout(metadata_path)
propose_patch(metadata_path)
Never edit source markdown directly. Return JSON action calls when acting."""


@dataclass
class Step:
    thought: str
    action: str | None = None
    observation: dict[str, Any] | None = None


@dataclass
class ReActAgent:
    model: str = field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"))
    api_key: str | None = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"

    def optimize(self, markdown_path: str, theme_path: str = "themes/default.yml", iterations: int = 3, output_dir: str = "renders") -> dict[str, Any]:
        patch_path = None
        trajectory: list[Step] = []
        last_state = None
        for _ in range(iterations):
            thought = "Render, score, and use deterministic tools before proposing a non-destructive patch."
            rendered = TOOLS["render_document"](markdown_path=markdown_path, theme_path=theme_path, patch_path=patch_path, output_dir=output_dir)
            trajectory.append(Step(thought, "render_document", rendered))
            if not rendered["ok"]:
                break
            judged = TOOLS["evaluate_layout"](metadata_path=rendered["metadata"])
            trajectory.append(Step("Evaluate layout metrics and decide whether further action is useful.", "evaluate_layout", judged))
            state = json.dumps(judged["metrics"], sort_keys=True)
            if state == last_state or judged["score"] >= 92:
                break
            last_state = state
            proposed = TOOLS["propose_patch"](metadata_path=rendered["metadata"])
            trajectory.append(Step("Propose a small patch using allowed agent actions.", "propose_patch", proposed))
            if not proposed.get("actions"):
                break
            patch_path = "patches/agent-latest.json"
            with open(patch_path, "w", encoding="utf-8") as handle:
                json.dump(proposed, handle, indent=2)
        return {"trajectory": [step.__dict__ for step in trajectory], "patch_path": patch_path}

    def ask_openrouter(self, messages: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required for live LLM calls")
        response = requests.post(
            self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "HTTP-Referer": "https://github.com/page-optimizer/page-optimizer", "X-Title": "page-optimizer"},
            json={"model": self.model, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages]},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
