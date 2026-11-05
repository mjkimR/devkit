---
id: TASKS-deep-research-practical-orchestration
spec: SPEC-deep-research-practical-orchestration
plan: PLAN-deep-research-practical-orchestration
---

# Task Breakdown: `SPEC-deep-research-practical-orchestration`

- [ ] **Task 1**: Refine the entry, references and role instructions while preserving deployed ownership.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/`, `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`, `packages/devkit-catalog/tests/e2e/bundles/deep_research/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: semantic walkthrough of the target blueprint, `just test-affected --base 94cd340e166d0714788c185f514923268e6d0b2a`, existing installed-consumer e2e, catalog lint/types, sync check and rules.
