---
id: TASKS-rule-shared-python-ast
spec: SPEC-rule-shared-python-ast
plan: PLAN-rule-shared-python-ast
---

# Task Breakdown: `SPEC-rule-shared-python-ast` Parse each Python file once per rules run

## Phase 1: Engine

- [x] **Task 1.1**: `WorkspaceCache.get_python_ast` with its tree and error memo, and the per-run resolution memo,
  with cache tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`,
    `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit packages/devkit/tests/integration/features/rules/workspace/test_cache.py`
- [x] **Task 1.2**: Lazy resolution in `RuleContext._relative`, with context tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/models/contracts.py`,
    `packages/devkit/tests/integration/features/rules/engine/test_context.py`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit packages/devkit/tests/integration/features/rules/engine/test_context.py`

## Phase 2: Rules

- [x] **Task 2.1**: Migrate `RULE-architecture` and `RULE-usecase-boundaries` to the accessor, with shared-tree and
  unparsable-file tests
  - **_Boundary**: `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/`,
    `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `uv run devkit rules test`
- [x] **Task 2.2**: Migrate `RULE-advisory-unique-code`, with shared-tree and unparsable-file tests
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `uv run devkit rules test`
- [x] **Task 2.3**: Migrate the catalog `layers`, `heavy_imports`, `command_boundary` and `library_output` rules,
  with shared-tree and unparsable-file tests
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit-catalog`
- [x] **Task 2.4**: Refresh the deployed copies and record parse count, byte identity and timing
  - **_Boundary**: `.devkit/installation.json`, `specs/2026-10/20261022-rule-shared-python-ast/evidence.md`
  - _Requirements: AC-08, AC-09, AC-10, AC-11_
  - **Verification**: `uv run devkit sync --check`; `uv run devkit rules check --format json`
