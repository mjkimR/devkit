---
id: TASKS-consolidate-spec-scope-commands
spec: SPEC-consolidate-spec-scope-commands
plan: PLAN-consolidate-spec-scope-commands
---

# Task Breakdown: `SPEC-consolidate-spec-scope-commands` Consolidate the spec scope commands around collect

## Phase 1: Implementation

- [ ] **Task 1.1**: Retire `register`, `query`, `compare` and hidden `update` with the registry update path, the journal and their codes; the post-finish cleanup and `release`/`sweep` keep their contracts, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py`, `packages/devkit-spec/tests/integration/features/scope/`, `packages/devkit-spec/tests/support/spec_support/`, `packages/devkit-spec/tests/integration/features/delivery/test_cleanup.py`, `packages/devkit-spec/tests/integration/package/test_help_and_notices.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, `.devkit/architecture.toml`
  - _Requirements: AC-01, AC-05_
  - **Verification**: `just test devkit-spec tests/integration/features/scope tests/integration/features/delivery/test_cleanup.py tests/integration/package`
- [ ] **Task 1.2**: Creation registration records declarations and dirty paths through collect's observation service; `observe_git` goes, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/usecases/flow.py`, `packages/devkit-spec/src/devkit_spec/features/scope/usecases/inputs.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/handoff.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/specs.py`, `packages/devkit-spec/tests/integration/features/scope/`, `packages/devkit-spec/tests/integration/features/delivery/test_handoff.py`, `packages/devkit-spec/tests/integration/features/delivery/test_spec_initialization.py`
  - _Requirements: AC-02_
  - **Verification**: `just test devkit-spec tests/integration/features/scope/test_flow.py tests/integration/features/delivery`
- [ ] **Task 1.3**: `collect` without `--mode`: options, collector, JSON and fix strings, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/cli/commands.py`, `packages/devkit-spec/src/devkit_spec/features/scope/models/observation.py`, `packages/devkit-spec/src/devkit_spec/features/scope/services/collection.py`, `packages/devkit-spec/src/devkit_spec/features/scope/usecases/collection.py`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/scope/test_collection.py`, `packages/devkit-spec/tests/integration/features/scope/test_collection_horizon.py`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/integration/features/scope/test_collection.py tests/integration/features/scope/test_collection_horizon.py`
- [ ] **Task 1.4**: Codes table and fix strings checked in both directions
  - **_Boundary**: `packages/devkit-spec/tests/integration/package/test_documented_codes.py`, `packages/devkit-spec/src/devkit_spec/base/errors.py`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-spec tests/integration/package/test_documented_codes.py`
- [ ] **Task 1.5**: Guidance, scaffold comment and Living Spec name only the remaining commands and options
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/SKILL.md.jinja`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`, `docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`, `docs/capabilities/harness/CAP-HARN-command-mount.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`, `docs/usecases/collaboration/UC-run-parallel-work-safely.md`, `docs/decisions/2026-11/20261102-worktrees-and-scope.md`
  - _Requirements: AC-01, AC-04, AC-06_
  - **Verification**: `uv run devkit sync --check`, `uv run devkit rules check --ci --base main` and `git grep -nE "scope (register|query|compare|update)|collect --mode"` limited to `docs/capabilities`, `docs/usecases` and `packages/devkit-spec/src`
