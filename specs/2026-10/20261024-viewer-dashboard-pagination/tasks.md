---
id: TASKS-viewer-dashboard-pagination
spec: SPEC-viewer-dashboard-pagination
plan: PLAN-viewer-dashboard-pagination
---
# Tasks for `SPEC-viewer-dashboard-pagination`

- [x] **Task 1**: Metadata reader and endpoint, optional source API and regression tests.
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/`, `packages/devkit-viewer/tests/`, `packages/devkit-viewer/frontend/src/lib/api/repository.ts`
  - _Requirements: AC-01, AC-05_
  - **Verification**: `just test viewer`
- [x] **Task 2**: Cached snapshots, page body loading, controls and regression checks.
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/dashboard/`, `packages/devkit-viewer/frontend/src/lib/api/cache.ts`, `packages/devkit-viewer/frontend/src/app/App.test.ts`, `packages/devkit-viewer/src/devkit_viewer/static/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`, `just test-affected`
