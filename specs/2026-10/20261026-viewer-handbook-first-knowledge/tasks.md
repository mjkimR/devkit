---
id: TASKS-viewer-handbook-first-knowledge
spec: SPEC-viewer-handbook-first-knowledge
plan: PLAN-viewer-handbook-first-knowledge
---

# Task Breakdown: `SPEC-viewer-handbook-first-knowledge` Handbook-first knowledge view with on-demand book

## Phase 1: Implementation

- [x] **Task 1.1**: Handbook reads, staleness, language choice and page rendering, with unit tests
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/api/handbook.ts, packages/devkit-viewer/frontend/src/lib/api/handbook.test.ts
  - _Requirements: AC-08, AC-09, AC-10_
  - **Verification**: `just viewer test`
- [x] **Task 1.2**: Handbook mode, index latch, book gate and bindable request in the knowledge views, with component tests
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/features/knowledge/, packages/devkit-viewer/frontend/src/lib/KnowledgeViews.svelte
  - _Requirements: AC-02, AC-03, AC-04, AC-05, AC-06, AC-08, AC-09, AC-10_
  - **Verification**: `just viewer test`
- [x] **Task 1.3**: Rail label, request state and deep links in `SddViewer`, with tests; rebuild the committed page
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/SddViewer.svelte, packages/devkit-viewer/frontend/src/lib/SddViewer.test.ts, packages/devkit-viewer/frontend/src/lib/components/shared/NavigationRail.svelte, packages/devkit-viewer/src/devkit_viewer/static/
  - _Requirements: AC-01, AC-06, AC-07_
  - **Verification**: `just viewer lint && just viewer check && just viewer test && just viewer build`
- [x] **Task 1.4**: Integration test of handbook serving through `tree` and `blob`
  - **_Boundary**: packages/devkit-viewer/tests/integration/features/browse/test_handbook.py
  - _Requirements: AC-11_
  - **Verification**: `just test devkit-viewer tests/integration/features/browse/test_handbook.py`
- [ ] **Task 1.5**: Cold-load measurement after the change
  - **_Boundary**: docs/materials/2026-10/20261026-viewer-handbook-first-knowledge/
  - _Requirements: AC-12_
  - **Verification**: `node coldload-probe.mjs <url> <repo-id> 3 cold-load-after.json Read .handbook-page`
