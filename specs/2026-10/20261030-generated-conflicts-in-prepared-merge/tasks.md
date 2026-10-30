---
id: TASKS-generated-conflicts-in-prepared-merge
spec: SPEC-generated-conflicts-in-prepared-merge
plan: PLAN-generated-conflicts-in-prepared-merge
---

# Task Breakdown: `SPEC-generated-conflicts-in-prepared-merge` Settle generated-file conflicts in prepared merges

## Phase 1: Implementation

- [ ] **Task 1**: Conflicted-entry reading, the conflict settler seam and the seeded tree in the worktree merge, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/`, `packages/devkit/tests/integration/features/worktree/test_merging.py`
  - _Requirements: AC-03, AC-08_
  - **Verification**: `just test devkit features/worktree`, `just lint-check devkit`, `just check devkit`

- [ ] **Task 2**: Registry at a commit and the shared conflict classification in the generated feature, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/generated/`, `packages/devkit/tests/unit/features/generated/`, `packages/devkit/tests/integration/features/generated/`
  - _Requirements: AC-05, AC-07_
  - **Verification**: `just test devkit features/generated`

- [ ] **Task 3**: Generated seeding in local prepare and integrate, the disclosure and its CLI output, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/tests/e2e/features/integration/`, `packages/devkit/tests/integration/features/integration/`
  - _Requirements: AC-01, AC-02, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test devkit features/integration`, `just lint-check devkit`, `just check devkit`

- [ ] **Task 4**: Integration and batch completion guidance, with asset tests and sync outputs
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `packages/devkit-spec/tests/integration/bundles/spec/test_moved_target_guidance.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-09_
  - **Verification**: `just test devkit-spec bundles/spec`, `uv run devkit sync --check`
