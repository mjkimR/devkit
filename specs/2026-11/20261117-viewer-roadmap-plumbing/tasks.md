---
id: TASKS-viewer-roadmap-plumbing
spec: SPEC-viewer-roadmap-plumbing
plan: PLAN-viewer-roadmap-plumbing
---

# Task Breakdown: `SPEC-viewer-roadmap-plumbing` Remove dead other-branch plumbing from the viewer roadmap

## Phase 1: Implementation

- [ ] **Task 1.1**: Drop the other-branch parameter, member branch and helpers from the roadmap builder and views,
  with their tests
  - **_Boundary**: `packages/devkit-viewer/frontend/src/api/roadmap.ts`,
    `packages/devkit-viewer/frontend/src/api/roadmap.test.ts`,
    `packages/devkit-viewer/frontend/src/api/milestones.test.ts`,
    `packages/devkit-viewer/frontend/src/features/roadmap/`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just viewer check && just viewer test`
- [ ] **Task 1.2**: Keep the server's tree item types in `normalizeTree`, with a test
  - **_Boundary**: `packages/devkit-viewer/frontend/src/api/repository.ts`,
    `packages/devkit-viewer/frontend/src/api/repository.test.ts`
  - _Requirements: AC-03_
  - **Verification**: `just viewer test`
- [ ] **Task 1.3**: Remove the stale library-build ignore entries
  - **_Boundary**: `.gitignore`
  - _Requirements: AC-04_
  - **Verification**: `rg -n "frontend/dist" .gitignore` prints nothing

## Phase 2: Generated build and records

- [ ] **Task 2.1**: Rebuild the committed page and resolve the source feedback
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`,
    `specs/2026-11/20261116-viewer-internal-simplification/feedback/viewer-roadmap-branch-plumbing.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just viewer build` and `git status --short` clean after commit
