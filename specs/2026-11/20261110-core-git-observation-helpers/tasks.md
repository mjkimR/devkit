---
id: TASKS-core-git-observation-helpers
spec: SPEC-core-git-observation-helpers
plan: PLAN-core-git-observation-helpers
---

# Task Breakdown: `SPEC-core-git-observation-helpers` Public Git observation helpers in devkit-core

## Phase 1: Core readers

- [x] **Task 1.1**: Worktree and status records, parsers and runners in `devkit_core.core`, with tests and reference
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/git.py`,
    `packages/devkit-core/src/devkit_core/core/__init__.py`,
    `packages/devkit-core/tests/integration/core/test_git_observation.py`,
    `packages/devkit-core/tests/unit/core/test_git_observation.py`, `docs/development/reference/core.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-10_
  - **Verification**: `just test devkit-core`

## Phase 2: Caller migration

- [x] **Task 2.1**: `devkit_agt` callers moved; `compact` porcelain removed
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/`, `packages/devkit/tests/`,
    `docs/capabilities/compact/CAP-CMP-bounded-execution.md`
  - _Requirements: AC-04, AC-10_
  - **Verification**: `just test-affected --base 1f8e0954cd2bd25cb93f0c0907e852440b2ba73f`
- [x] **Task 2.2**: `devkit_dist` callers moved, newline worktree path test
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/`, `packages/devkit-dist/tests/`
  - _Requirements: AC-04, AC-09_
  - **Verification**: `just test-dist`
- [x] **Task 2.3**: `devkit_spec` callers moved, quoted-path, rename and newline tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/`, `packages/devkit-spec/tests/`
  - _Requirements: AC-04, AC-05, AC-06, AC-09_
  - **Verification**: `just test devkit-spec`
- [x] **Task 2.4**: `devkit_adaptive` parsers as wrappers and the local revision fix, with the `^HEAD` test
  - **_Boundary**: `packages/devkit-adaptive/src/devkit_adaptive/features/`, `packages/devkit-adaptive/tests/`,
    `docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md`
  - _Requirements: AC-04, AC-08, AC-10_
  - **Verification**: `just test devkit-adaptive`
- [x] **Task 2.5**: `devkit_mcp` and `devkit_viewer` callers moved, non-UTF-8 and newline tests
  - **_Boundary**: `packages/devkit-mcp/src/devkit_mcp/features/`, `packages/devkit-mcp/tests/`,
    `packages/devkit-viewer/src/devkit_viewer/features/`, `packages/devkit-viewer/tests/`
  - _Requirements: AC-04, AC-07, AC-09_
  - **Verification**: `just test devkit-mcp`; `just test devkit-viewer`

## Phase 3: Checks

- [x] **Task 3.1**: Whole-change checks
  - **_Boundary**: `specs/2026-11/20261110-core-git-observation-helpers/`
  - _Requirements: AC-10_
  - **Verification**: `just lint-check`; `just check`; `just rules-check`;
    `just test-affected --base 1f8e0954cd2bd25cb93f0c0907e852440b2ba73f`; `just test-dist`
