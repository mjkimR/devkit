---
id: TASKS-shared-python-node-index
spec: SPEC-shared-python-node-index
plan: PLAN-shared-python-node-index
---

# Task Breakdown: `SPEC-shared-python-node-index` Walk each Python tree once per rules run

## Phase 1: Cache Accessor

- [x] **Task 1.1**: Implement `WorkspaceCache.get_python_nodes` and write cache integration tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`, `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit packages/devkit/tests/integration/features/rules/workspace/test_cache.py`

## Phase 2: Rules Migration

- [x] **Task 2.1**: Migrate `RULE-architecture` and `RULE-usecase-boundaries` to `get_python_nodes`
  - **_Boundary**: `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/`, `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-dev`
- [x] **Task 2.2**: Migrate `RULE-cli-tool-command-boundary` and `RULE-cli-tool-library-output` to `get_python_nodes`
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/command_boundary/`, `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/library_output/`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-catalog`
- [ ] **Task 2.3**: Reconcile Living Spec contracts, refresh installation receipt, and verify workspace findings
  - **_Boundary**: `docs/capabilities/governance/`, `.devkit/installation.json`
  - _Requirements: AC-07, AC-08, AC-09_
  - **Verification**: `uv run devkit sync --check`; `uv run devkit rules check --format json`
