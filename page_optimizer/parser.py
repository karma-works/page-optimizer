from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .model import Block, Document

TAG_RE = re.compile(r"^<(NP|NPR|NPV|FCP|NS,[^>]+|WS,[^>]+)>$")
IF_RE = re.compile(r"^<IFEQ,\^?([^,>]+),([^,>]+),([^>]+)>$")
COUNTER_RE = re.compile(r"^<#R([^=]+)=(.*)>$")


def fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def parse_markdown_file(path: str | Path) -> Document:
    return parse_markdown(Path(path).read_text())


def parse_markdown(markdown: str, counters: dict[str, int] | None = None) -> Document:
    counters = dict(counters or {})
    blocks: list[Block] = []
    paragraph: list[str] = []
    paragraph_start = 1
    lines = markdown.splitlines()
    i = 0

    def add(kind: str, text: str = "", source_line: int = 0, **kwargs: object) -> None:
        block_id = f"b{len(blocks) + 1:04d}_{fingerprint(kind + text)}"
        blocks.append(Block(id=block_id, kind=kind, text=text, source_line=source_line, **kwargs))

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            add("paragraph", " ".join(part.strip() for part in paragraph), paragraph_start)
            paragraph = []

    while i < len(lines):
        raw = lines[i]
        line_no = i + 1
        stripped = raw.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            add("code", "\n".join(code_lines), line_no)
            i += 1
            continue
        if TAG_RE.match(stripped):
            flush_paragraph()
            tag = stripped[1:-1]
            kind = "page_break"
            attrs: dict[str, object] = {}
            if tag == "FCP":
                kind = "lazy_page_break"
            elif tag.startswith("WS,"):
                kind = "widow_spec"
                parts = tag.split(",")
                attrs = {"before": int(parts[1]), "after": int(parts[2]), "priority": int(parts[3]), "conflict": int(parts[4])}
            elif tag.startswith("NS,"):
                kind = "section"
                attrs = {"name": tag.split(",", 1)[1]}
            add(kind, tag, line_no, tag=tag, attrs=attrs)
            i += 1
            continue
        counter = COUNTER_RE.match(stripped)
        if counter:
            counters[counter.group(1)] = 0
            add("optional", counter.group(2).replace("<NL>", "\n"), line_no, attrs={"counter": counter.group(1)})
            i += 1
            continue
        condition = IF_RE.match(stripped)
        if condition:
            name, expected, target = condition.groups()
            counters[target] = 1 if str(counters.get(name, 0)) == expected else 0
            i += 1
            continue
        if stripped.startswith("#"):
            flush_paragraph()
            level = len(stripped) - len(stripped.lstrip("#"))
            add("heading", stripped[level:].strip(), line_no, level=level)
            i += 1
            continue
        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            add("list", "\n".join(items), line_no, items=tuple(items))
            continue
        if stripped.startswith("|") and "|" in stripped[1:]:
            flush_paragraph()
            rows: list[tuple[str, ...]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = tuple(cell.strip() for cell in lines[i].strip().strip("|").split("|"))
                if not all(set(cell) <= {"-", ":"} for cell in cells):
                    rows.append(cells)
                i += 1
            add("table", "", line_no, rows=tuple(rows))
            continue
        if not paragraph:
            paragraph_start = line_no
        paragraph.append(raw)
        i += 1
    flush_paragraph()
    return Document(blocks=blocks, counters=counters)
