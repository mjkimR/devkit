---
id: TASKS-viewer-dashboard-loading
spec: SPEC-viewer-dashboard-loading
plan: PLAN-viewer-dashboard-loading
---

# Task Breakdown: `SPEC-viewer-dashboard-loading`

- [x] **Task 1**: Add bounded caching, continuous workers, selective dashboard loaders and regression tests.
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/`, `packages/devkit-viewer/tests/integration/features/browse/`, `packages/devkit-viewer/frontend/src/lib/api/`, `packages/devkit-viewer/frontend/src/lib/features/dashboard/loading.ts`
  - _Requirements: AC-01, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just viewer test`, `just viewer check`
- [x] **Task 2**: Render independent sections with refresh and cancellation, verify components and rebuild assets.
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/dashboard/`, `packages/devkit-viewer/src/devkit_viewer/static/`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`, `just viewer pack`
