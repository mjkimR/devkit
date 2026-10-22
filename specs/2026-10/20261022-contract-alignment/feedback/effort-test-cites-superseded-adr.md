---
id: FB-effort-test-cites-superseded-adr
title: The effort procedure test docstring cites the superseded review loop ADR
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-effort-test-cites-superseded-adr] The effort procedure test docstring cites the superseded review loop ADR

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-contract-alignment` superseded `ADR-bounded-high-effort-review-loop` with
  `ADR-host-owned-review-loop-recovery`.
- **Expectation**: The test that confirms the loop names the in-effect decision.
- **Actual**: The module docstring of `test_effort_procedure.py` cites `ADR-bounded-high-effort-review-loop`;
  `ADR-host-owned-review-loop-recovery` names this test in its Confirmation.
- **Workaround (or Interpretation Chosen)**: Left unchanged: tests were outside the docs-only unit's write scope.
- **Suggestion**: Repoint the docstring citation to `ADR-host-owned-review-loop-recovery`.

## Evidence

```text
packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py:1
"""The ``high`` activity-effort procedure ships as one bounded review loop (``ADR-bounded-high-effort-review-loop``).
```
