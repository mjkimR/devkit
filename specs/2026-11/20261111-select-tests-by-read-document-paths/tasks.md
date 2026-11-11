---
id: TASKS-select-tests-by-read-document-paths
spec: SPEC-select-tests-by-read-document-paths
plan: PLAN-select-tests-by-read-document-paths
---

# Task Breakdown: `SPEC-select-tests-by-read-document-paths` Select tests by the repository paths they read

## Phase 1: Implementation

- [x] **Task 1.1**: Read discovery in the selector, with its tests
  - **_Boundary**: `scripts/affected_tests.py`, `packages/devkit/tests/e2e/package/test_affected_tests.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06, AC-07, AC-08_
  - **Verification**: `just test-e2e devkit packages/devkit/tests/e2e/package/test_affected_tests.py`; the AC-06
    timing probe under `tmp/probe/`
- [ ] **Task 1.2**: Describe read discovery in the CI/CD reference and the deployment view
  - **_Boundary**: `docs/development/ci-cd.md`, `docs/architecture/ARCH-07-deployment.md`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit rules check --ci --base main`; `git diff --check`
