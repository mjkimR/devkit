---
id: TASKS-retire-finish-merge
spec: SPEC-retire-finish-merge
plan: PLAN-retire-finish-merge
---

# Task Breakdown: `SPEC-retire-finish-merge` Retire worktree finish --merge

## Phase 1: Decision

- [x] **Task 1.1**: Record `ADR-single-local-landing-route`, superseding in part the `finish --merge` clauses of
  `ADR-local-and-pull-request-integration`, `ADR-orchestration-workers`, `ADR-worktrees-and-scope` and the
  `devkit.finish_guard` entry point clause of `ADR-package-ownership-and-release-version`
  - **_Boundary**: `docs/decisions/2026-11/20261111-single-local-landing-route.md`, `docs/decisions/2026-11/20261102-local-and-pull-request-integration.md`, `docs/decisions/2026-11/20261102-orchestration-workers.md`, `docs/decisions/2026-11/20261102-worktrees-and-scope.md`, `docs/decisions/2026-11/20261102-package-ownership-and-release-version.md`
  - _Requirements: AC-07_
  - **Verification**: `uv run devkit rules check docs/decisions/2026-11/20261111-single-local-landing-route.md`

## Phase 2: Implementation

- [x] **Task 2.1**: Retire the landing path of `finish` and refuse `--merge`, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/`, `packages/devkit/tests/integration/features/worktree/`, `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py`, `packages/devkit/tests/integration/package/test_config_tables.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit tests/integration/features/worktree tests/e2e/features/worktree tests/integration/package/test_config_tables.py`
- [x] **Task 2.2**: Integration service cleanup call and the landing coverage moved from `finish --merge`, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/usecases/service.py`, `packages/devkit/src/devkit_agt/features/integration/usecases/pull_request.py`, `packages/devkit/tests/integration/features/integration/`, `packages/devkit/tests/e2e/features/integration/`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit tests/integration/features/integration`
- [x] **Task 2.3**: Retire the `devkit.finish_guard` group and the workflow guard, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/services/extensions.py`, `packages/devkit/src/devkit_agt/features/workflow/usecases/integration.py`, `packages/devkit/pyproject.toml`, `packages/devkit/tests/integration/features/workflow/test_envelope_hold.py`, `packages/devkit/tests/integration/features/worktree/test_branches.py`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_envelope_hold.py tests/integration/features/worktree/test_branches.py`
- [x] **Task 2.4**: Spec bundle guidance names the integration route, with the bundle text test and sync outputs
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/branches.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_role_contracts.py` and `uv run devkit sync --check`
- [x] **Task 2.5**: Living Spec and references name one landing route
  - **_Boundary**: `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`, `docs/capabilities/delivery/CAP-DLV-project-policy.md`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/architecture/ARCH-04-2-delivery-policy.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/architecture/ARCH-06-runtime-view.md`, `docs/usecases/delivery/UC-drive-development-to-integration.md`, `docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md`, `docs/development/reference/worktree.md`, `docs/development/reference/integration.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check` and the AC-06 `rg -n "finish[^|]*--merge" packages docs guides`
