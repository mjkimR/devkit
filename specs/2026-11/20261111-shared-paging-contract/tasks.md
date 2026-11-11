---
id: TASKS-shared-paging-contract
spec: SPEC-shared-paging-contract
plan: PLAN-shared-paging-contract
---

# Task Breakdown: `SPEC-shared-paging-contract` One paging contract for listing commands

- [x] **Task 1**: `exec list` text output through `echo_page`, with CLI unit tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/isolated_execution/cli.py`, `packages/devkit/tests/unit/features/isolated_execution/test_output.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just test devkit tests/unit/features/isolated_execution/test_output.py`
- [x] **Task 2**: Shared paging grammar in the agent output architecture and the capability and reference pointers
  - **_Boundary**: `docs/architecture/ARCH-08-1-agent-output.md`, `docs/capabilities/harness/CAP-HARN-command-mount.md`, `docs/capabilities/harness/CAP-HARN-isolated-execution.md`, `docs/development/reference/exec.md`
  - _Requirements: AC-07_
  - **Verification**: `rg -n EXECUTION_LIST docs/architecture docs/capabilities docs/development packages/devkit/src` and `uv run devkit rules check --ci --base main`
