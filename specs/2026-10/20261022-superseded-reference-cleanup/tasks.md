---
id: TASKS-superseded-reference-cleanup
spec: SPEC-superseded-reference-cleanup
plan: PLAN-superseded-reference-cleanup
---

# Task Breakdown: `SPEC-superseded-reference-cleanup` Align leftover references with the current ownership and integration recoveries

## Phase 1: Implementation

- [x] **Task 1.1**: Foundation ownership references: the devkit-agt dependency comment and the configuration ADR driver
  - **_Boundary**: `packages/devkit/pyproject.toml`, `docs/decisions/2026-10/20261022-configuration-language-and-rendering.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `rg -n 'devkit-dist==|shared foundation' packages/devkit/pyproject.toml`, `rg -n 'ADR-dist-foundation-ownership|foundation belongs' docs/decisions/2026-10/20261022-configuration-language-and-rendering.md`, `uv run devkit rules check`
- [x] **Task 1.2**: The effort procedure test docstring cites `ADR-host-owned-review-loop-recovery`
  - **_Boundary**: `packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py`
- [x] **Task 1.3**: Retained-runtime extensions and scenarios in the integration use case
  - **_Boundary**: `docs/usecases/delivery/UC-drive-development-to-integration.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/usecases/delivery/UC-drive-development-to-integration.md`
- [x] **Task 1.4**: Read-only shell access for the reconcile reviewer, its contract test and the regenerated projections
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/reconcile-reviewer.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`, `.claude/agents/reconcile-reviewer.md`, `.codex/agents/reconcile-reviewer.toml`, `.agents/agents/reconcile-reviewer.md`, `.devkit/`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit sync --check`, `just test-affected`
