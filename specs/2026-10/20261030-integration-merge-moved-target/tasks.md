---
id: TASKS-integration-merge-moved-target
spec: SPEC-integration-merge-moved-target
plan: PLAN-integration-merge-moved-target
---

# Task Breakdown: `SPEC-integration-merge-moved-target` Integrate a conflict-free moved target without requiring the source to contain it

## Phase 1: Implementation

- [x] **Task 1**: Plan and build a prospective merge for a moved target at local prepare, with its result output and tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/`, `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/tests/`
  - _Requirements: AC-01, AC-03, AC-04, AC-05, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: `just test devkit features/integration features/worktree`, `just lint-check devkit`, `just check devkit`

- [x] **Task 2**: Delivery provider and composed acceptance on a prospective result, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/`, `packages/devkit-spec/tests/`
  - _Requirements: AC-02, AC-04, AC-05, AC-06, AC-09_
  - **Verification**: `just test devkit-spec features/delivery`, `just lint-check devkit-spec`, `just check devkit-spec`

- [ ] **Task 3**: Bundle guidance for the conditional base merge and the batch test run, with asset tests and sync outputs
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/`, `packages/devkit-spec/tests/integration/bundles/spec/`, `.devkit/installation.json` (sync output), `AGENTS.md` (sync output)
  - _Requirements: AC-11_
  - **Verification**: `just test devkit-spec bundles/spec`, `uv run devkit sync --check`

- [ ] **Task 4**: Repository verification policy and reference documents
  - **_Boundary**: `AGENTS.md`, `docs/development/`, `guides/INSTALL_GUIDE.md`
  - _Requirements: AC-09, AC-11_
  - **Verification**: `just rules-check`, `git diff --check`
