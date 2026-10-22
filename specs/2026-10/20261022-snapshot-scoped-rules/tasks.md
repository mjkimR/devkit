---
id: TASKS-snapshot-scoped-rules
spec: SPEC-snapshot-scoped-rules
plan: PLAN-snapshot-scoped-rules
---

# Task Breakdown: `SPEC-snapshot-scoped-rules` Scope snapshot rules runs to their changed paths

## Phase 1: Engine Implementation

- [ ] **Task 1.1**: Snapshot scoping in `scope_rules` and diff path capture in `snapshot.py`
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/evaluator.py`, `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/snapshot.py`, `packages/devkit/tests/unit/features/rules/engine/test_scoping.py`
  - _Requirements: AC-01, AC-02, AC-05, AC-06_
  - **Verification**: `uv run pytest packages/devkit/tests/unit/features/rules/engine/test_scoping.py`
- [ ] **Task 1.2**: Lifecycle short-circuit fix for deletion-only commits and `RuleContext` target decoupling
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/usecases/project.py`, `packages/devkit/src/devkit_agt/features/rules/models/contracts.py`, `packages/devkit/tests/integration/features/rules/engine/test_project.py`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/rules/engine/test_project.py`

## Phase 2: Verification and End-to-End Checks

- [ ] **Task 2.1**: Verification of snapshot gates, pre-commit speedup, and affected tests
  - **_Boundary**: `specs/2026-10/20261022-snapshot-scoped-rules/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just test-affected && just rules-check`
