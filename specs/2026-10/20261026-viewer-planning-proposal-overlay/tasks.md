---
id: TASKS-viewer-planning-proposal-overlay
spec: SPEC-viewer-planning-proposal-overlay
plan: PLAN-viewer-planning-proposal-overlay
---

# Task Breakdown: `SPEC-viewer-planning-proposal-overlay` Viewer overlay of Planning proposals

## Phase 1: Server

- [x] **Task 1.1**: Planning source enumeration, batched proposal scan, source-scoped `tree` and `blob`, the
  `planning-proposals` endpoint and their integration tests
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/`, `packages/devkit-viewer/tests/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit-viewer`, `just lint devkit-viewer`, `just check devkit-viewer`

## Phase 2: Page and library

- [x] **Task 2.1**: Optional data-source methods, overlay loading, cache and seed, with unit tests
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/api/`, `packages/devkit-viewer/frontend/src/lib/index.ts`
  - _Requirements: AC-08, AC-10_
  - **Verification**: `just viewer test`
- [x] **Task 2.2**: Dashboard in-place overlay, badge, note and seeded list build, with component tests
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/dashboard/`
  - _Requirements: AC-06, AC-07, AC-08, AC-10_
  - **Verification**: `just viewer test`
- [x] **Task 2.3**: Proposals tab overlay, source-scoped bundle, badge and Dashboard card selection, with component tests
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/knowledge/`,
    `packages/devkit-viewer/frontend/src/lib/SddViewer.svelte`, `packages/devkit-viewer/frontend/src/lib/*.test.ts`
  - _Requirements: AC-09, AC-10_
  - **Verification**: `just viewer test`
- [x] **Task 2.4**: Rebuild the committed page
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`
  - _Requirements: AC-06, AC-09_
  - **Verification**: `just viewer lint`, `just viewer check`, `just viewer build`,
    `uv run devkit generated check viewer-assets`
