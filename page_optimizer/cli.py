from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_tools import render_document
from .generator import write_samples
from .hitl import rate_document
from .judge import score_metadata_file
from .react_agent import ReActAgent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="page-optimizer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sample", help="create synthetic sample markdown documents")
    render = sub.add_parser("render", help="render markdown to PDF, PNG screenshots, and metadata")
    render.add_argument("markdown")
    render.add_argument("--theme", default="themes/default.yml")
    render.add_argument("--patch")
    judge = sub.add_parser("judge", help="score layout metadata")
    judge.add_argument("metadata")
    rate = sub.add_parser("rate", help="record a human rating for a rendered sample")
    rate.add_argument("sample")
    rate.add_argument("pdf")
    rate.add_argument("--screenshot", action="append", default=[])
    rate.add_argument("--rating", type=int, required=True)
    rate.add_argument("--notes", default="")
    agent = sub.add_parser("agent", help="run the deterministic ReAct optimizer loop")
    agent.add_argument("markdown")
    agent.add_argument("--theme", default="themes/default.yml")
    agent.add_argument("--iterations", type=int, default=3)
    agent.add_argument("--output-dir", default="renders")
    args = parser.parse_args(argv)

    if args.command == "sample":
        print(json.dumps([str(path) for path in write_samples()], indent=2))
    elif args.command == "render":
        print(json.dumps(render_document(args.markdown, args.theme, args.patch), indent=2))
    elif args.command == "judge":
        print(json.dumps(score_metadata_file(args.metadata), indent=2))
    elif args.command == "rate":
        print(json.dumps(rate_document(args.sample, args.pdf, args.screenshot, args.rating, args.notes), indent=2))
    elif args.command == "agent":
        print(json.dumps(ReActAgent().optimize(args.markdown, args.theme, args.iterations, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
