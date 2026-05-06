from __future__ import annotations

import random
from pathlib import Path

WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua "
    "ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"
).split()


def lorem_words(count: int, rng: random.Random) -> str:
    return " ".join(rng.choice(WORDS) for _ in range(count)).capitalize() + "."


def generate_document(seed: int = 1, sections: int = 4, stress: bool = False) -> str:
    rng = random.Random(seed)
    parts = [f"# Synthetic Layout Sample {seed}", "", "<WS,2,2,5,1>", ""]
    for section in range(1, sections + 1):
        parts.extend([f"## Section {section}", ""])
        if section == 2:
            parts.extend(["<NP>", ""])
        if section == 3:
            parts.extend(["<#R12=Optional editorial sidebar: " + lorem_words(38, rng) + "<NL>>", "<IFEQ,^10,1,12>", ""])
        for _ in range(rng.randint(3, 6)):
            size = rng.randint(45, 130 if not stress else 260)
            parts.extend([lorem_words(size, rng), ""])
        parts.extend(["- " + lorem_words(12, rng), "- " + lorem_words(18, rng), ""])
        if stress and section == sections:
            parts.extend(["<NPR>", "", lorem_words(480, rng), ""])
    return "\n".join(parts)


def write_samples(directory: str | Path = "examples") -> list[Path]:
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    specs = [("basic.md", 11, False), ("stress.md", 29, True), ("rating-sample.md", 41, False)]
    paths: list[Path] = []
    for name, seed, stress in specs:
        path = out / name
        path.write_text(generate_document(seed=seed, sections=5, stress=stress))
        paths.append(path)
    return paths
