---
id: TASKS-affected-test-granularity
spec: SPEC-affected-test-granularity
plan: PLAN-affected-test-granularity
---

# Task Breakdown: `SPEC-affected-test-granularity`

- [ ] **Task 1**: Implement file groups, fine source inventory and conservative dependency traversal with independent regression fixtures.
  - **_Boundary**: scripts/affected_tests.py, packages/devkit/tests/test_affected_tests.py
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: Focused selector pytest, lint and type checks.
- [ ] **Task 2**: Measure same-revision selection and document actual granularity and limitations.
  - **_Boundary**: docs/materials/2026-10/20261020-affected-test-granularity/, docs/development/ci-cd.md, docs/development/workflow.md
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: Baseline/new file and collection matrices, just test-affected and governance checks.
