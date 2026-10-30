---
id: TASKS-git-operator-batch-preparation
spec: SPEC-git-operator-batch-preparation
plan: PLAN-git-operator-batch-preparation
---

# Task Breakdown: `SPEC-git-operator-batch-preparation` Bounded batch preparation for git-operator

## Phase 1: Implementation

- [ ] **Task 1.1**: Preparation list in the git-operator role contract, with contract-text tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`, `.devkit/installation.json` (sync output), `AGENTS.md` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`

- [ ] **Task 1.2**: Host dispatch, operations and payload guidance for the list, with contract-text tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/git-operator-dispatch.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/git-operator-operations.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`, `.devkit/installation.json` (sync output), `AGENTS.md` (sync output)
  - _Requirements: AC-04, AC-06_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`

- [ ] **Task 1.3**: Confirm no CLI change and unchanged worktree outcome tests
  - **_Boundary**: none (verification only)
  - _Requirements: AC-07_
  - **Verification**: `git -C <worktree> diff --stat 133819ed -- packages/devkit/` is empty; `just test devkit packages/devkit/tests/integration/features/worktree packages/devkit/tests/e2e/features/worktree`
