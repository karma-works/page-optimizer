Testing ReAct agents properly requires testing **three separate layers**:

1. reasoning quality
2. tool/action correctness
3. end-task outcome quality

For your document optimizer, you additionally need:

* layout correctness
* convergence stability
* regression protection
* visual quality evaluation

---

# 1. Core Principle

Do **not** test only final outputs.

A ReAct agent can:

* reach correct outputs for wrong reasons
* loop unnecessarily
* take destructive actions
* overfit to examples
* become unstable after small prompt/model changes

You must therefore test:

```text id="n5y94k"
THOUGHTS
ACTIONS
OBSERVATIONS
FINAL RESULT
```

---

# 2. Recommended Testing Pyramid

```text id="a5m4zv"
                E2E visual tests
             integration / trajectory
          action-policy / planner tests
         deterministic renderer tests
              unit tests
```

---

# 3. Deterministic Engine Tests (Most Important)

Your renderer/paginator must be heavily deterministic-tested.

## Test Categories

### Pagination

```text id="8f9p87"
- NP behavior
- NPR recto logic
- NPV verso logic
- FCP lazy behavior
- section boundaries
```

---

### Widow/Orphan Tests

```text id="6ovg5o"
- p1/p2 enforcement
- nested WS priorities
- overwrite semantics
- keep-together behavior
```

---

### Margin Tests

```text id="kll1v8"
- exact bounding box validation
- overflow detection
- clipping detection
- edge tolerance thresholds
```

---

### Conditional Content

```text id="2u9f3l"
- counter evaluation
- IF command correctness
- reserved string expansion
- optional-content activation
```

---

# 4. Golden Rendering Tests

This is one of the most important best practices.

## Concept

Render:

* markdown
* theme
* patch

Then compare against:

* known-good metadata
* known-good screenshots

---

## Recommended Structure

```text id="efptce"
tests/golden/
    basic_page_breaks/
    widow_cases/
    recto_verso/
    optional_content/
    sparse_page_cases/
```

---

## Validate

### Metadata Equality

Compare:

```json id="lr8dyc"
{
  "page_count": 12,
  "overflow_blocks": 0,
  "widow_violations": 0
}
```

---

### Screenshot Similarity

Use:

* SSIM
* perceptual hashing
* pixel diff thresholds

Avoid exact pixel equality.

---

# 5. Trajectory Testing (Critical for ReAct)

Most teams forget this.

Test the entire reasoning trajectory.

---

## Example

```text id="aqe2jh"
THOUGHT:
Page 7 has overflow.

ACTION:
Insert <NP> before block b42.

OBSERVATION:
Overflow fixed, but page 8 sparse.

THOUGHT:
Activate optional block opt_12.

ACTION:
set_counter(12=1)
```

Validate:

* reasoning coherence
* action validity
* convergence
* no oscillation

---

# 6. Convergence Testing

Your optimizer is iterative.

You must test:

```text id="6x6d7h"
Does the system stabilize?
```

---

## Detect

### Infinite Oscillation

Example:

```text id="ktst4v"
iteration 1:
insert page break

iteration 2:
remove page break

iteration 3:
insert again
```

---

## Best Practices

Track:

```text id="3izqbo"
- patch delta size
- score improvement
- repeated actions
- repeated states
```

Terminate if:

* no score improvement
* repeated layout state
* repeated patch sequence

---

# 7. Action Safety Testing

Every action should have validators.

---

## Example

```text id="jlwm3f"
replace_tag(<NP> -> <FCP>)
```

Validate:

* anchor exists
* no invalid state introduced
* recto/verso constraints preserved

---

# 8. Adversarial Testing

Very important for layout systems.

Generate pathological documents.

---

## Examples

### Extremely Long Paragraphs

```text id="1bd92i"
single paragraph spanning 8 pages
```

---

### Aggressive WS Rules

```text id="r6hbgh"
<WS,60,60,7,2>
```

---

### Near-Overflow Cases

```text id="5kg9ev"
text exceeds page by 1 line
```

---

### Cascading Page Shift Cases

```text id="6rk7zy"
small change on page 2 breaks page 20
```

---

# 9. Synthetic Document Fuzzing

Your lorem ipsum generator should become a fuzzing engine.

Generate random:

```text id="vt0t4y"
- headings
- page breaks
- WS rules
- optional content
- paragraph lengths
- tables
- nested conditions
```

Then run thousands of documents automatically.

This is extremely valuable.

---

# 10. Metrics-Based Evaluation

Do not rely only on LLM judgments.

Compute deterministic metrics.

---

## Recommended Metrics

```text id="ysnsvb"
overflow_ratio
widow_count
orphan_count
page_fill_ratio
empty_page_count
average_whitespace
layout_stability
patch_size
iterations_to_convergence
```

---

# 11. Judge Calibration

Your visual judge itself must be tested.

---

## Build a Labeled Dataset

Humans label pages:

```text id="qf4ff0"
GOOD
BAD
MARGIN_VIOLATION
SPARSE
AWKWARD_BREAK
```

Then compare:

* judge decisions
* human labels

Measure:

* precision
* recall
* agreement

---

# 12. Regional vs Global Regression Tests

Critical for hierarchical systems.

A local fix may globally worsen layout.

Always compare:

```text id="fwgqg7"
before optimization
vs
after optimization
```

Across:

* entire document
* not only modified pages

---

# 13. Replayability

All runs must be reproducible.

Store:

```text id="x1t9qj"
- prompts
- screenshots
- metadata
- model version
- seeds
- patches
- scores
```

This is essential for debugging.

---

# 14. Human-in-the-Loop Review

For production rollout:

Sample optimized documents and review:

```text id="nly1df"
- readability
- aesthetics
- correctness
- consistency
```

Especially for:

* legal documents
* books
* invoices
* contracts

---

# 15. Recommended Testing Strategy for Your System

## Stage 1

Deterministic renderer tests.

Goal:

```text id="jlwm4t"
renderer correctness = near 100%
```

---

## Stage 2

Golden screenshot tests.

Goal:

```text id="8ycqz7"
stable rendering behavior
```

---

## Stage 3

Synthetic fuzzing.

Goal:

```text id="g0gd1o"
robustness under pathological layouts
```

---

## Stage 4

ReAct trajectory testing.

Goal:

```text id="9dfj3d"
stable optimization behavior
```

---

## Stage 5

Human quality evaluation.

Goal:

```text id="h8gl5u"
production-grade visual quality
```

---

# 16. Biggest Mistake to Avoid

The most common failure mode:

```text id="0cdjlwm"
LLM optimizer compensates for renderer bugs.
```

Never allow that.

The renderer must be:

* deterministic
* trusted
* independently validated

The agent should optimize layout quality,
not repair broken rendering semantics.

