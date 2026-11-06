---
id: TASKS-async-e2e-verification
spec: SPEC-async-e2e-verification
plan: PLAN-async-e2e-verification
---

# Task Breakdown: Isolated Command Execution

- [x] **Task 1**: Tier-aware affected selection with selected-tier full fallback and selector regressions
  - **_Boundary**: `scripts/affected_tests.py`, `justfile`, `packages/devkit/tests/e2e/package/test_affected_tests.py`
  - _Requirements: AC-01_
  - **Verification**: selector E2E and native CLI list/empty tier probes.
- [x] **Task 2**: Fixed-commit detached execution, persistent evidence, native argv and package registration with lifecycle tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/isolated_execution/`, `packages/devkit/src/devkit_agt/features/worktree/`, `packages/devkit/pyproject.toml`, `packages/devkit/README.md`, `packages/devkit/tests/unit/features/isolated_execution/`, `packages/devkit/tests/integration/features/isolated_execution/`, `packages/devkit/tests/e2e/features/isolated_execution/`, `packages/devkit/tests/unit/features/worktree/`, `packages/devkit/tests/integration/features/worktree/`, `packages/devkit-dist/src/devkit_dist/cli.py`, `packages/devkit-dist/tests/integration/cli/`, `.devkit/architecture.toml`, `uv.lock`
  - _Requirements: AC-03, AC-04, AC-07, AC-08, AC-09, AC-11, AC-12, AC-13, AC-14_
  - **Verification**: lifecycle subprocess probes, comparable blocking measurements, package registration tests, lint and types.
- [x] **Task 3**: Local-orchestrated consumption and final verification guidance with focused guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/`, `AGENTS.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-02, AC-05, AC-06, AC-10, AC-15_
  - **Verification**: focused guidance tests and accumulated interval/failed result walkthrough.

Living Spec reconciliation targets: `docs/capabilities/harness/`, `docs/capabilities/worktree/`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/development/reference/`, `docs/decisions/`, `docs/usecases/harness/UC-execute-an-isolated-command.md`, `docs/usecases/delivery/UC-drive-development-to-integration.md`.
