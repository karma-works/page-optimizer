Here is an ADR (Architecture Decision Record) document capturing the implementation decisions made during the architecture discussion.

# ADR-001 — Document Creation Engine & ReAct Layout Optimizer

## Status

Accepted

---

# Context

We are building a deterministic document creation engine with an intelligent layout optimization system.

The system must:

* render Markdown documents to PDF
* support custom pagination and widow/orphan tags
* enforce page margin constraints
* support conditional/optional content
* optimize layout quality automatically
* use a ReAct-style agent with visual judgment
* generate explainable optimization patches
* support theming
* provide reproducible rendering behavior

The layout optimizer must operate safely and deterministically while still enabling intelligent document composition improvements.

---

# Decision Summary

| Area                    | Decision                                    |
| ----------------------- | ------------------------------------------- |
| Implementation language | Python                                      |
| Markdown support        | Basic Markdown only                         |
| Rendering architecture  | Internal document model                     |
| Markdown parsing        | Existing Markdown parser                    |
| PDF rendering           | ReportLab                                   |
| PDF rasterization       | Rasterize every page to PNG                 |
| Layout optimization     | ReAct agent                                 |
| Optimization safety     | Deterministic validators                    |
| Patch strategy          | Non-destructive patch layer                 |
| Visual judge inputs     | Screenshots + layout metadata               |
| Optimization hierarchy  | Hierarchical agent system                   |
| Pagination strategy     | Hybrid heuristic pagination                 |
| Theme support           | Configurable theming                        |
| Margin enforcement      | Hard acceptance criteria                    |
| Optional content        | Counter-driven conditional blocks           |
| Testing strategy        | Deterministic + visual + trajectory testing |

---

# ADR-002 — Use Python as Primary Implementation Language

## Status

Accepted

## Decision

Python will be used as the implementation language.

## Rationale

Python provides:

* strong PDF ecosystem
* mature image-processing libraries
* excellent LLM integration
* rapid experimentation capability
* strong testing/fuzzing support

## Consequences

### Positive

* fast development velocity
* easy AI integration
* large ecosystem

### Negative

* lower rendering performance than native implementations
* memory overhead for large documents

---

# ADR-003 — Use Internal Document Model

## Status

Accepted

## Decision

The system will use a custom internal document model between Markdown parsing and PDF rendering.

## Rationale

Custom layout semantics require full pagination control:

* `<NP>`
* `<NPR>`
* `<NPV>`
* `<FCP>`
* `<WS>`
* conditional blocks

Direct Markdown-to-PDF rendering libraries do not expose sufficient pagination control.

## Consequences

### Positive

* deterministic pagination
* flexible layout optimization
* robust widow/orphan handling

### Negative

* additional implementation complexity
* custom pagination engine required

---

# ADR-004 — Use Existing Markdown Parser

## Status

Accepted

## Decision

Use an existing Markdown parser rather than implementing Markdown parsing manually.

Recommended libraries:

* markdown-it-py
* mistune

## Rationale

Markdown parsing itself is not the core problem.

The core challenge is pagination and layout optimization.

## Consequences

### Positive

* reduced implementation effort
* standards-compliant Markdown parsing

### Negative

* requires AST transformation layer

---

# ADR-005 — Use ReportLab for PDF Rendering

## Status

Accepted

## Decision

Use ReportLab for final PDF generation.

## Rationale

ReportLab provides:

* low-level layout control
* deterministic rendering
* custom pagination support
* explicit coordinate control

## Consequences

### Positive

* precise rendering control
* deterministic output

### Negative

* more manual layout implementation
* less automatic styling

---

# ADR-006 — Use Non-Destructive Patch Layer

## Status

Accepted

## Decision

The optimizer must never directly modify source Markdown.

Instead, it produces optimization patches.

## Example

```json
{
  "tag_edits": [
    {
      "op": "replace",
      "from": "<NP>",
      "to": "<FCP>"
    }
  ]
}
```

## Rationale

This enables:

* reproducibility
* rollback
* explainability
* safe optimization

## Consequences

### Positive

* auditable optimization process
* easier debugging

### Negative

* additional patch resolution layer required

---

# ADR-007 — Use Hybrid Anchor Resolution

## Status

Accepted

## Decision

Patch anchors will use:

* generated block IDs
* text fingerprints
* source line fallback

## Rationale

Line-number-only systems are fragile.

Manual IDs are too intrusive.

Hybrid anchors provide robustness without burdening authors.

## Consequences

### Positive

* stable optimization patches
* robust against source edits

### Negative

* more complex patch resolution logic

---

# ADR-008 — Use ReAct-Based Optimization

## Status

Accepted

## Decision

The layout optimizer will use the ReAct pattern.

## ReAct Cycle

```text
THOUGHT
→ ACTION
→ OBSERVATION
→ REPEAT
```

## Rationale

Layout optimization is iterative and stateful.

ReAct enables:

* explainable reasoning
* iterative refinement
* controlled action generation

## Consequences

### Positive

* transparent optimization
* iterative improvement

### Negative

* convergence management required

---

# ADR-009 — Use Deterministic Validators

## Status

Accepted

## Decision

All optimizer actions must pass deterministic validation.

## Validator Responsibilities

* patch schema validation
* anchor validation
* layout constraint enforcement
* recto/verso validation
* margin validation
* clipping detection

## Rationale

LLM decisions must not directly mutate layout state without safety guarantees.

## Consequences

### Positive

* stable optimization
* safer rendering pipeline

### Negative

* more validation infrastructure required

---

# ADR-010 — Use Hierarchical Optimization Agents

## Status

Accepted

## Decision

The optimizer will use three hierarchical layers:

1. Document Planner
2. Regional Optimizer
3. Local Repair Agent

## Rationale

Layout changes propagate across pages.

A hierarchical structure separates:

* global planning
* regional balancing
* local repairs

## Consequences

### Positive

* scalable optimization
* better global coherence

### Negative

* coordination complexity

---

# ADR-011 — Use Screenshots + Layout Metadata

## Status

Accepted

## Decision

The visual judge will receive:

* rasterized PDF screenshots
* structured layout metadata

## Rationale

Screenshots alone lack structural understanding.

Metadata alone misses visual quality issues.

Combined input provides robust evaluation.

## Consequences

### Positive

* improved optimization reliability
* explainable layout reasoning

### Negative

* more rendering artifacts must be generated

---

# ADR-012 — Rasterize Every Page to PNG

## Status

Accepted

## Decision

Every PDF page will be rasterized into PNG images.

## Recommended Settings

* 150–200 DPI
* PNG format

## Rationale

Simple, deterministic, and easy to integrate.

## Consequences

### Positive

* simplified visual pipeline
* deterministic screenshots

### Negative

* increased storage requirements

---

# ADR-013 — Use Hybrid Heuristic Pagination

## Status

Accepted

## Decision

Pagination will use a hybrid heuristic approach.

## Rationale

Full constraint solving is unnecessarily expensive and complex for:

* conditional content
* widow handling
* recto/verso rules

Heuristics provide better engineering tradeoffs.

## Consequences

### Positive

* practical performance
* flexible pagination

### Negative

* pagination not globally optimal in all cases

---

# ADR-014 — Layout Quality Over Minimal Page Count

## Status

Accepted

## Decision

The optimizer prioritizes layout quality over minimizing total page count.

## Priority Order

1. hard constraint compliance
2. visual quality
3. whitespace balance
4. page count minimization

## Rationale

Professional typography prioritizes readability and visual balance.

## Consequences

### Positive

* higher-quality layouts
* fewer awkward pages

### Negative

* potentially longer documents

---

# ADR-015 — Use Optional Content as Layout Optimization Mechanism

## Status

Accepted

## Decision

Conditional content may be activated/deactivated during optimization.

## Rationale

Optional content can improve:

* page fullness
* whitespace balance
* section rhythm

## Consequences

### Positive

* adaptive layout balancing

### Negative

* optimization search space increases

---

# ADR-016 — Introduce Lorem Ipsum Fuzz Generator

## Status

Accepted

## Decision

The system will include a synthetic document generator.

## Purpose

Generate randomized stress-test documents containing:

* random WS rules
* random page breaks
* optional content
* varying paragraph lengths

## Rationale

Layout systems require large-scale fuzz testing.

## Consequences

### Positive

* robustness testing
* regression detection

### Negative

* additional tooling required

---

# ADR-017 — Comprehensive ReAct Testing Strategy

## Status

Accepted

## Decision

Testing must include:

* deterministic renderer tests
* visual regression tests
* trajectory tests
* convergence tests
* fuzz testing
* human evaluation

## Rationale

ReAct systems fail in ways traditional systems do not.

Final-output-only testing is insufficient.

## Consequences

### Positive

* safer optimization system
* better regression protection

### Negative

* significant testing infrastructure required

---

# Final Architecture Summary

```text
Markdown + Tags
    +
Theme Config
    +
Patch Layer
        ↓
Parser
        ↓
Internal Document Model
        ↓
Paginator
        ↓
ReportLab Renderer
        ↓
PDF
        ↓
PNG Rasterization
        ↓
Visual Judge
        ↓
ReAct Optimizer
        ↓
Validated Patch Updates
```
