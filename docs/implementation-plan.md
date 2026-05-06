# Document Creation Engine + ReAct Visual Layout Optimizer — Architecture Plan

## 1. Overview

The system consists of two major applications:

1. **Document Creation Engine**

   * Input: Markdown + custom layout tags
   * Output: PDF
   * Responsible for deterministic layouting, pagination, widow/orphan handling, and rendering

2. **ReAct Visual Layout Optimizer**

   * Uses rendered PDF screenshots + layout metadata
   * Optimizes page breaks, margins, widow specifications, optional content, and whitespace distribution
   * Produces a non-destructive optimization patch layer

---

# 2. High-Level Architecture

```text
Markdown Source
    +
Theme Config
    +
Optimization Patch
        ↓
Parser
        ↓
Internal Document Model
        ↓
Paginator / Layout Engine
        ↓
PDF Renderer
        ↓
PDF Output
        ↓
PDF Rasterizer
        ↓
PNG Screenshots
        ↓
Visual Judge
        ↓
ReAct Optimizer
        ↓
Updated Patch Layer
        ↓
Re-render
```

---

# 3. Input Format

## Supported Markdown

Only basic Markdown:

* headings
* paragraphs
* bold/italic
* lists
* tables
* code blocks
* images
* links

---

# 4. Special Layout Tags

## Page Break Tags

| Tag       | Meaning            |
| --------- | ------------------ |
| `<NP>`    | Immediate new page |
| `<NPR>`   | New recto page     |
| `<NPV>`   | New verso page     |
| `<FCP>`   | Lazy page seal     |
| `<NS,p1>` | New section        |

---

## Widow Specification

```text
<WS,p1,p2,p3,p4>
```

| Param | Meaning                    |
| ----- | -------------------------- |
| p1    | minimum lines before break |
| p2    | minimum lines after break  |
| p3    | priority                   |
| p4    | conflict behavior          |

---

## Conditional Content

Uses:

* counters
* reserved strings
* IF commands

Example:

```text
<#R12=Optional text here<NL>>
<IFEQ,^10,1,12>
```

---

# 5. Core Technical Decisions

| Area                  | Decision                         |
| --------------------- | -------------------------------- |
| Language              | Python                           |
| Markdown parsing      | markdown-it-py or mistune        |
| PDF generation        | ReportLab                        |
| PDF rasterization     | pypdfium2                        |
| Image processing      | Pillow                           |
| Architecture          | Internal document model          |
| Optimization strategy | ReAct + deterministic validators |
| Patch strategy        | Non-destructive patch layer      |

---

# 6. Internal Document Model

## Block Types

```text
Document
 ├── Section
 ├── Heading
 ├── Paragraph
 ├── List
 ├── Table
 ├── Image
 ├── CodeBlock
 ├── PageBreak
 ├── LazyPageBreak
 ├── WidowSpec
 ├── ConditionalBlock
```

---

# 7. Rendering Pipeline

## Pipeline

```text
Markdown
    ↓
Tag Preprocessor
    ↓
Markdown Parser
    ↓
AST Conversion
    ↓
Internal Block Model
    ↓
Paginator
    ↓
PDF Renderer
```

---

# 8. Pagination Strategy

## Chosen Strategy

Hybrid heuristic pagination.

Reason:

* flexible
* efficient
* supports dynamic content
* handles NPR/NPV
* supports conditional blocks

---

## Pagination Responsibilities

### Must Handle

* margins
* widow/orphan rules
* recto/verso pages
* lazy page breaks
* keep-together blocks
* optional content
* section boundaries

---

# 9. Theme System

## Example

```yaml
page:
  size: A4

margins:
  top: 24mm
  right: 20mm
  bottom: 24mm
  left: 20mm

fonts:
  body: Helvetica
  heading: Helvetica-Bold
  mono: Courier
```

---

# 10. Patch Layer

## Goal

Never modify original markdown.

Optimizer outputs patch instructions.

---

## Example

```json
{
  "version": 1,
  "margin_profile": {
    "top_mm": 22,
    "right_mm": 18,
    "bottom_mm": 22,
    "left_mm": 18
  },
  "tag_edits": [
    {
      "op": "replace",
      "anchor": "block:heading_12:after",
      "from": "<NP>",
      "to": "<FCP>"
    }
  ]
}
```

---

# 11. Anchor Resolution

## Hybrid Anchors

```json
{
  "block_id": "b0042",
  "kind": "paragraph",
  "position": "before",
  "source_line": 118,
  "text_fingerprint": "sha1hash"
}
```

## Resolution Order

```text
1. block_id
2. fingerprint
3. source line proximity
4. fallback text match
```

---

# 12. Layout Metadata

## Per Page

```json
{
  "page": 12,
  "margins": {
    "top": 22,
    "right": 18,
    "bottom": 22,
    "left": 18
  },
  "blocks": [
    {
      "id": "b0042",
      "bbox": [72,144,510,220],
      "lines": 8
    }
  ]
}
```

---

# 13. PDF Screenshot Pipeline

## Chosen Strategy

Rasterize every page to PNG.

## Recommended Settings

```text
resolution: 150–200 DPI
format: PNG
```

---

# 14. Visual Judge

## Inputs

```text
- page PNGs
- layout metadata
- AST
- patch layer
```

---

## Responsibilities

### Hard Violations

* text outside margins
* clipped content
* unintended empty pages
* invalid recto/verso

### Soft Optimization

* sparse pages
* whitespace balancing
* widow/orphan quality
* heading grouping

---

# 15. ReAct Optimization Architecture

## Hierarchical Agent Design

```text
Document Planner
    ↓
Regional Optimizer
    ↓
Local Repair Agent
```

---

# 16. Agent Responsibilities

## Document Planner

* global page balance
* optional content strategy
* detect problematic regions

---

## Regional Optimizer

Optimizes:

* 3–8 page windows
* whitespace distribution
* page fullness
* WS tuning

---

## Local Repair Agent

Fixes:

* margin overflow
* clipping
* widows/orphans
* bad page transitions

---

# 17. Allowed Optimizer Actions

```json
[
  "set_margin_profile",
  "insert_tag",
  "remove_tag",
  "replace_tag",
  "insert_spacing",
  "remove_spacing",
  "set_ws",
  "reset_ws",
  "set_counter",
  "unset_counter"
]
```

---

# 18. Validation Layer

## Deterministic Validators

Must validate:

* patch schema
* anchor resolution
* tag correctness
* no infinite loops
* margin compliance
* no clipped content
* valid recto/verso behavior

---

# 19. Optimization Phases

## Phase 1 — Local Repair

```text
- fix margin violations
- remove clipping
- remove empty pages
- repair widows/orphans
```

---

## Phase 2 — Regional Optimization

```text
- rebalance neighboring pages
- improve spacing
- optimize WS rules
```

---

## Phase 3 — Global Optimization

```text
- optional content activation
- improve fill ratios
- reduce sparse pages
```

---

# 20. Optional Content Optimization

Optional content acts as a constrained filler system.

## Metadata Example

```json
{
  "id": "opt_42",
  "priority": 0.7,
  "min_lines": 3,
  "max_lines": 8
}
```

---

# 21. Acceptance Rules

## Hard Reject Conditions

```text
IF:
    overflow_ratio > threshold
OR:
    clipped_content_detected
OR:
    unintended_empty_pages > 0

THEN:
    acceptable = false
```

---

# 22. Scoring Model

```text
document_score =
    + 40% margin compliance
    + 20% widow/orphan quality
    + 20% page fullness
    + 10% spacing consistency
    + 10% page count efficiency
```

---

# 23. Lorem Ipsum Generator

## Purpose

Generate synthetic stress-test documents.

## Features

* configurable paragraph lengths
* random headings
* optional tables/images
* configurable WS tags
* random conditional content
* stress pagination edges

---

# 24. Suggested Repository Structure

```text
project/
├── engine/
│   ├── parser/
│   ├── ast/
│   ├── paginator/
│   ├── renderer/
│   ├── optimizer/
│   └── visual_judge/
├── tests/
├── examples/
├── themes/
├── patches/
├── renders/
│   ├── pdf/
│   └── png/
└── prompts/
```

---

# 25. Recommended Development Order

## Phase 1

Build deterministic engine:

* parser
* AST
* paginator
* ReportLab renderer

---

## Phase 2

Add:

* WS handling
* NPR/NPV
* FCP behavior
* conditional content

---

## Phase 3

Add:

* PNG rasterization
* layout metadata
* visual judge

---

## Phase 4

Implement ReAct optimizer:

* patch generation
* validation
* iterative rerendering

---

# 26. Final System Characteristics

The final system will provide:

* deterministic document generation
* intelligent layout repair
* explainable optimization patches
* visual quality validation
* adaptive page utilization
* professional pagination behavior
* robust widow/orphan handling
* conditional content optimization

