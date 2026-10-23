---
id: TASKS-cli-host-lifecycle
spec: SPEC-cli-host-lifecycle
plan: PLAN-cli-host-lifecycle
---

# Task Breakdown: `SPEC-cli-host-lifecycle` CLI execution for Host lifecycle operations

## Phase 1: Lifecycle CLI operations

- [x] **Task 1**: Compose proposal acceptance and handoff through CLI use cases
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/cli/`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/`, `packages/devkit-spec/src/devkit_spec/features/proposals/cli/`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/delivery/`, `packages/devkit-spec/tests/integration/features/proposals/`, `packages/devkit-spec/tests/e2e/features/delivery/`
  - _Requirements: AC-01, AC-02, AC-03, AC-05, AC-09_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/ tests/integration/features/delivery/ tests/e2e/features/delivery/`

- [x] **Task 2**: Expose stateless local and pull-request integration execution through CLI
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/cli.py`, `packages/devkit/src/devkit_agt/features/integration/usecases/`, `packages/devkit/src/devkit_agt/features/integration/models/`, `packages/devkit/tests/integration/features/integration/test_cli.py`, `packages/devkit/tests/integration/features/integration/test_service.py`, `packages/devkit/tests/integration/features/integration/test_policy.py`, `packages/devkit/tests/integration/features/integration/test_pull_request.py`, `packages/devkit/tests/integration/features/integration/test_composition.py`, `packages/devkit/tests/integration/features/integration/test_receipt_reader.py`, `packages/devkit/tests/e2e/features/integration/`
  - _Requirements: AC-03, AC-04, AC-05, AC-06, AC-07, AC-09_
  - **Verification**: `just test devkit tests/integration/features/integration/ tests/e2e/features/integration/`

## Phase 2: Transport removal and contract reflection

- [x] **Task 3**: Remove lifecycle MCP registrations and preserve shared MCP services
  - **_Boundary**: `packages/devkit/pyproject.toml`, `packages/devkit/src/devkit_agt/features/integration/mcp.py`, `packages/devkit/tests/integration/features/integration/test_mcp.py`, `packages/devkit-spec/pyproject.toml`, `packages/devkit-spec/src/devkit_spec/features/delivery/mcp/`, `packages/devkit-spec/src/devkit_spec/features/proposals/mcp/report.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_report.py`, `packages/devkit-mcp/tests/integration/features/runtime/test_shared_transport.py`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/`, `.devkit/installation.json`
  - _Requirements: AC-03, AC-08_
  - **Verification**: `just test devkit tests/integration/features/integration/test_mcp.py`; `just test devkit-spec tests/e2e/features/delivery/test_integration.py tests/integration/features/proposals/test_proposal_report.py tests/integration/bundles/spec/`; `just test devkit-mcp tests/integration/features/runtime/test_shared_transport.py`

- [x] **Task 4**: Reconcile Living Spec, superseding decisions and consumer guidance
  - **_Boundary**: `docs/capabilities/delivery/`, `docs/capabilities/harness/`, `docs/capabilities/integration/`, `docs/capabilities/mcp/`, `docs/capabilities/worktree/`, `docs/capabilities/collaboration/`, `docs/usecases/delivery/`, `docs/architecture/ARCH-04-2-delivery-policy.md`, `docs/architecture/ARCH-06-runtime-view.md`, `docs/decisions/2026-10/`, `docs/development/reference/`, `guides/`, `specs/2026-10/20261023-cli-host-lifecycle/reconcile.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09_
  - **Verification**: `just rules-check`; `uv run devkit rules check --ci --base <base-ref>`; compare each reconcile target against the implementation diff
