---
id: TASKS-generated-conflicts-follow-ups
spec: SPEC-generated-conflicts-follow-ups
plan: PLAN-generated-conflicts-follow-ups
---

# Task Breakdown: `SPEC-generated-conflicts-follow-ups` Follow-ups of the generated conflict settling

## Phase 1: Implementation

- [x] **Task 1**: Accepted exit statuses on the shared Git runner, with tests and the core reference
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/git.py`, `packages/devkit-core/tests/integration/core/test_git.py`, `docs/development/reference/core.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-core core`, `just check devkit-core`

- [x] **Task 2**: merge-tree on the shared runner, with a structural test
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/services/merging.py`, `packages/devkit/tests/integration/features/worktree/test_merging.py`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit features/worktree`, `just test devkit features/integration`, `just check devkit`

- [x] **Task 3**: The generated check before the batch test run in the guides
  - **_Boundary**: `docs/development/workflow.md`, `docs/development/ci-cd.md`, `AGENTS.md`
  - _Requirements: AC-04_
  - **Verification**: `git diff --check`, `uv run devkit rules check`

- [x] **Task 4**: The architecture declaration in a delegated cross-feature choice, with a guidance test and sync outputs
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_architecture_scope_guidance.py`, `AGENTS.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-05_
  - **Verification**: `just test devkit-spec bundles/spec`, `uv run devkit sync --check`

- [x] **Task 5**: Document changes select the bundle citation test, with tests
  - **_Boundary**: `scripts/affected_tests.py`, `packages/devkit/tests/e2e/package/test_affected_tests.py`, `docs/development/ci-cd.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run pytest packages/devkit/tests/e2e/package/test_affected_tests.py`

- [x] **Task 6**: The agent-asset-writing instruction in the repository guide
  - **_Boundary**: `AGENTS.md`
  - _Requirements: AC-07_
  - **Verification**: `git diff --check`, `uv run devkit sync --check`
