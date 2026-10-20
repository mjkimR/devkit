---
id: TASKS-handoff-fixture-initialization
spec: SPEC-handoff-fixture-initialization
plan: PLAN-handoff-fixture-initialization
---

# Tasks: `SPEC-handoff-fixture-initialization`

- [x] **Task 1**: Reuse standalone initialization while preserving real per-test Planning state, with an isolation regression.
  - **_Boundary**: `packages/devkit-spec/tests/test_integration.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: integration file, isolation regression and affected tests.
- [x] **Task 2**: Retain paired baseline/current performance evidence and its reproducible driver.
  - **_Boundary**: `docs/materials/2026-10/20261020-handoff-fixture-initialization/`
  - _Requirements: AC-04_
  - **Verification**: one serial comparison and two reversed-order eight-worker comparisons over the same original cases.
