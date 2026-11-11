---
id: TASKS-remove-test-only-public-apis
spec: SPEC-remove-test-only-public-apis
plan: PLAN-remove-test-only-public-apis
---

# Task Breakdown: `SPEC-remove-test-only-public-apis` Remove test-only public APIs

## Phase 1: Implementation

- [ ] **Task 1.1**: Remove `before_remove` from the worktree `finish` and `discard`, with migrated tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py`, `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py`, `packages/devkit/tests/integration/features/worktree/test_branches.py`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit packages/devkit/tests/e2e/features/worktree packages/devkit/tests/integration/features/worktree`
- [ ] **Task 1.2**: Remove `renames` and `ignore_submodules` from `status_records`, with core tests
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/git.py`, `packages/devkit-core/tests/integration/core/test_git_observation.py`
  - _Requirements: AC-02_
  - **Verification**: `just test devkit-core packages/devkit-core/tests/integration/core/test_git_observation.py`
- [ ] **Task 1.3**: Remove `bm25_scores`, `SearchIndex.search(limit=)` and `SearchHit.to_dict`, with search tests
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/search/`, `packages/devkit-dist/tests/unit/features/search/test_lexical.py`, `packages/devkit-dist/tests/integration/features/search/test_index.py`
  - _Requirements: AC-03_
  - **Verification**: `just test-dist`
- [ ] **Task 1.4**: Update the Living Spec for the removed members
  - **_Boundary**: `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/capabilities/search/CAP-SRCH-document-search.md`, `docs/development/reference/worktree.md`, `docs/development/reference/search.md`, `docs/development/reference/core.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check`
