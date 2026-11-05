---
id: TASKS-ux-design-exploration
spec: SPEC-ux-design-exploration
plan: PLAN-ux-design-exploration
---

# Task Breakdown: `SPEC-ux-design-exploration`

- [x] **Task 1**: Add the explicitly invoked skill, optional local roles and conditional design/orchestration guidance with sync and instruction-contract tests.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/uiux_improve/`, `packages/devkit-catalog/pyproject.toml`, `.devkit/architecture.toml`, `packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py`, `uv.lock`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: focused integration tests, catalog lint/type and agent-asset hygiene checks.
- [x] **Task 2**: Verify built-wheel selection/removal/reselection without delivery/document packages and retain user artifacts.
  - **_Boundary**: `packages/devkit-catalog/tests/e2e/bundles/uiux_improve/`
  - _Requirements: AC-01, AC-05, AC-06_
  - **Verification**: installed-consumer e2e test and `just test-affected`.
