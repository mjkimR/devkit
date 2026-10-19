---
id: TASKS-affected-frontend
spec: SPEC-affected-frontend
plan: PLAN-affected-frontend
---

# Task Breakdown: `SPEC-affected-frontend` Frontend changes in affected test selection

- [x] **Task 1**: Frontend rule and `[FRONTEND_CHECK: ...]` line in `just test-affected`, with unit tests
  - **_Boundary**: `scripts/affected_tests.py`, `packages/devkit/tests/test_affected_tests.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just test-affected`
- [x] **Task 2**: Describe the frontend rule and line in the development docs and agent guide
  - **_Boundary**: `docs/development/ci-cd.md`, `AGENTS.md`
  - _Requirements: AC-07_
  - **Verification**: `just rules-check`
