# page-optimizer

Markdown document creation engine plus a ReAct visual layout optimizer. It renders
synthetic Markdown documents to PDF, rasterizes PDF pages to PNG screenshots,
computes deterministic layout metrics, and records human-in-the-loop ratings.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
```

If `python3-venv` is unavailable, install into a local dependency directory:

```bash
pip3 install --target .deps -e ".[test]"
PYTHONPATH=.deps:. python3 -m page_optimizer.cli sample
```

## OpenRouter Setup

The ReAct agent is wired for OpenRouter.

```bash
export OPENROUTER_API_KEY="..."
export OPENROUTER_MODEL="openai/gpt-4o-mini"
```

The deterministic optimizer loop works without an API key. Live LLM calls require
`OPENROUTER_API_KEY`.

## Usage

Create synthetic lorem ipsum samples:

```bash
page-optimizer sample
```

Render a sample to PDF, PNG screenshots, and metadata:

```bash
page-optimizer render examples/basic.md --theme themes/default.yml
```

Judge the layout:

```bash
page-optimizer judge renders/metadata/basic.json
```

Record a human rating:

```bash
page-optimizer rate examples/basic.md renders/pdf/basic.pdf \
  --screenshot renders/png/basic_page_001.png \
  --rating 4 \
  --notes "Readable, balanced first page"
```

Run the ReAct optimizer loop:

```bash
page-optimizer agent examples/basic.md --iterations 3
```

## Agent Tools

The ReAct agent exposes all required layout actions through tool functions:

- `render_document`: applies a non-destructive patch, renders PDF, writes metadata, and rasterizes PNGs.
- `evaluate_layout`: scores deterministic metrics and labels.
- `propose_patch`: produces allowed patch actions for sparse or problematic layouts.

Patch validation supports the planned action set:
`set_margin_profile`, `insert_tag`, `remove_tag`, `replace_tag`,
`insert_spacing`, `remove_spacing`, `set_ws`, `reset_ws`, `set_counter`, and
`unset_counter`.

## Test Strategy Coverage

At least five recommended strategies are implemented:

- deterministic renderer tests
- pagination and recto behavior tests
- golden render metadata plus PNG screenshot tests
- synthetic fuzzing tests
- ReAct trajectory and convergence tests
- action safety tests
- human-in-the-loop rating persistence tests

Run:

```bash
PYTHONPATH=.deps:. python3 -m pytest
```

## Outputs

- PDF files: `renders/pdf/`
- PNG screenshots: `renders/png/`
- layout metadata: `renders/metadata/`
- human ratings: `renders/ratings.jsonl`

## License

MIT. See `LICENSE`.
