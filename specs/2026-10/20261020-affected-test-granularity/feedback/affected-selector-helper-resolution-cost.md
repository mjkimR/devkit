---
id: FB-affected-selector-helper-resolution-cost
title: Profile the remaining per-run helper resolution cost
scope: repo
kind: suggestion
category: other
target: scripts/affected_tests.py
skill: spec-review
agent: codex
origin: agent
severity: noise
recurring: true
status: dismissed
created_at: 2026-10-20
---

# [FB-affected-selector-helper-resolution-cost] Profile the remaining per-run helper resolution cost

## Suggestion

Performance observation: finer static coverage adds measurable selector overhead even while reducing test execution.

- **Current Procedure**: Rebuild the source graph and test-helper closures on every selection, caching ASTs and helper
  path resolutions within the run.
- **Proposed Procedure**: Profile remaining filesystem candidate checks before considering an in-memory helper
  inventory. Preserve conservative ambiguity handling and all current regression fixtures.
- **Expected Benefit**: Reduce repeated selection latency without a persistent cache or altered coverage.
- **Cost & Risk**: More inventory code can introduce dependency omissions; unchanged selected-file sets and independent
  fixtures are required before accepting an optimization.
- **Attempted**: Per-run helper-path caching reduced the initial implementation from roughly two seconds to about
  1.2–1.4 seconds. A fully indexed helper inventory is untested, and is not required by this delivery.

## Diagnostic Details

- **Reproduction**: Run the dated `measure.py` in the affected-test-granularity materials on the same source checkout.
- **Expected / Actual**: No hardware-independent latency bound was promised. Nine cases show about twice the baseline
  selector time while retaining coverage and reducing several test sets.
- **Versions**: Baseline algorithm from 29e7dd36845455d92d42e858e3372e3dd812a22e; reviewed implementation d94c914.
- **Conditions**: Warm local filesystem, three selection samples per algorithm and source case, existing workspace
  interpreter; no production code imported by the selector.
- **Workarounds Attempted**: AST and helper-path caches are in place; no helper import was removed or relocated.
- **Related Assets**: `scripts/affected_tests.py`, dated development-selection.json and development-evidence.md.

## Evidence

```text
Baseline selector medians: approximately 0.6–0.7 seconds.
New selector medians: approximately 1.2–1.4 seconds.
Gate selection: 1,073 to 301 tests; scope: 1,118 to 1,048; proposals: 1,118 to 1,065.
```

## Disposition

Dismissed: additional measurement on source revision `6b21869d9029e22886fc6d5511b82c67bc9297cc` found
approximately 1.15–1.55 seconds of extra selector time across the nine cases. A helper inventory does not have
enough demonstrated benefit to justify additional dependency-resolution complexity. Separate single pytest runs
with eight workers, plus selector medians from three samples, retained net improvements for gate
(14.58 to 10.78 seconds) and rules (61.34 to 54.80 seconds). Scope, documents and proposals retain the costly
integration consumers; removed scope/proposal tests account for only 0.08/0.06 summed worker-seconds in the full
run. Scope's single selected execution was slower, so no universal runtime improvement is claimed. Whole-workspace
verification passed 3,993 tests with 12 skipped, and all six selected executions passed. Keep the existing selector
and investigate repeated integration-test preparation separately; no selector optimization is required.
