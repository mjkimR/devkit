---
id: TASKS-gate-health-status
spec: SPEC-gate-health-status
plan: PLAN-gate-health-status
---

# Task Breakdown: `SPEC-gate-health-status`

- [x] **Task 1**: Optional distribution status checks and isolated failure reporting, with regression tests.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/`, `packages/devkit-dist/tests/integration/features/distribution/`, `packages/devkit-dist/tests/unit/features/distribution/`, `packages/devkit-dist/tests/integration/package/`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/development/reference/distribution.md`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: distribution regression tests, lint/type checks and `just test-dist`.
- [x] **Task 2**: Gate-owned provider registered by harness metadata, with hook regression and baseline checks.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/gate/`, `packages/devkit/tests/integration/features/gate/`, `packages/devkit/pyproject.toml`, `docs/capabilities/gate/CAP-GATE-commit-gates.md`, `specs/2026-10/feedback/20261027-gate-hook-problems-invisible-to-status.md`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: gate regression tests, lint/type checks and `just test-affected`.
