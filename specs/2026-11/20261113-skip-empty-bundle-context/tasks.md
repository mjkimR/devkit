---
id: TASKS-skip-empty-bundle-context
spec: SPEC-skip-empty-bundle-context
plan: PLAN-skip-empty-bundle-context
---

# Task Breakdown: `SPEC-skip-empty-bundle-context`

- [ ] **Task 1**: Align generated entry paths with source presence and verify integration cases.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/`, `packages/devkit-dist/tests/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: Focused integration tests, lint, type check and affected tests.
- [ ] **Task 2**: Update consumption instructions and package reference; sync derived outputs.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/consumption.md`, `packages/devkit-dist/README.md`, `AGENTS.md` (sync output), `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-05, AC-07_
  - **Verification**: Rules and `uv run devkit sync --check`.
