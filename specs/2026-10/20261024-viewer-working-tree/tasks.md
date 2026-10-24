---
id: TASKS-viewer-working-tree
spec: SPEC-viewer-working-tree
plan: PLAN-viewer-working-tree
---

# Task Breakdown: `SPEC-viewer-working-tree` Show the working tree for the current branch

## Phase 1: Contract and reader

- [ ] **Task 1**: Read current filesystem entries and files safely; report the checked-out branch and update server contracts
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/`, `packages/devkit-viewer/tests/integration/features/browse/`, `docs/capabilities/viewer/CAP-VIEW-repository-viewer.md`, `docs/decisions/2026-10/20261024-viewer-working-tree.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06_
  - **Verification**: `just test packages/devkit-viewer tests/integration/features/browse`

## Phase 2: Current-tree interface

- [ ] **Task 2**: Remove branch selection and make all app views use the current working tree
  - **_Boundary**: `packages/devkit-viewer/frontend/src/`, `packages/devkit-viewer/src/devkit_viewer/static/`, `packages/devkit-viewer/tests/integration/features/browse/`, `docs/capabilities/viewer/CAP-VIEW-repository-viewer.md`, `docs/decisions/2026-10/20261024-viewer-working-tree.md`
  - _Requirements: AC-04, AC-05, AC-06_
  - **Verification**: `just viewer lint && just viewer check && just viewer test && just viewer build`
