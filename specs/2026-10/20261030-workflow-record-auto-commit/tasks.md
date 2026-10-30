---
id: TASKS-workflow-record-auto-commit
spec: SPEC-workflow-record-auto-commit
plan: PLAN-workflow-record-auto-commit
---

# Task Breakdown: `SPEC-workflow-record-auto-commit`

## Implementation

- [ ] **Task 1**: Implement explicit envelope commit with real Git safety and regression tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/`, `packages/devkit/tests/unit/features/workflow/`, `packages/devkit/tests/integration/features/workflow/`, `specs/2026-10/20261030-workflow-record-auto-commit/`, `docs/materials/2026-10/20261030-workflow-record-auto-commit/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit workflow`, `just lint-check devkit`, `just check devkit`, `just test-affected`

- [ ] **Task 2**: Document record-only invocation and combined commit boundaries with bundle checks
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/`, `packages/devkit-spec/tests/integration/bundles/spec/`, `docs/capabilities/delivery/`, `docs/usecases/delivery/`, `docs/decisions/2026-10/20261030-explicit-envelope-commits.md`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test devkit-spec bundles/spec`, `just lint-check devkit-spec`, `just check devkit-spec`, `uv run devkit sync --check`, `just rules-check`
