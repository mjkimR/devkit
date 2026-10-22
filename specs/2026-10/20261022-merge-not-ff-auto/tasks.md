---
id: TASKS-merge-not-ff-auto
spec: SPEC-merge-not-ff-auto
plan: PLAN-merge-not-ff-auto
---

# Task Breakdown: `SPEC-merge-not-ff-auto` Auto advisory mode for WORKTREE_MERGE_NOT_FF

## Phase 1: Implementation

- [x] **Task 1.1**: Update `MergeNotFastForwardError` to `actor = Actor.TOOL` and add regression tests for `AUTO` mode
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/models/errors.py`, `packages/devkit/tests/e2e/features/integration/test_base_advance.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run pytest packages/devkit/tests/e2e/features/integration/test_base_advance.py`

## Phase 2: Living Spec & Verification

- [x] **Task 2.1**: Update Living Spec references and run verification
  - **_Boundary**: `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/development/reference/worktree.md`, `specs/2026-10/feedback/20261022-merge-not-ff-asks-the-user.md`
  - _Requirements: AC-04_
  - **Verification**: `just test-affected && just rules-check`
