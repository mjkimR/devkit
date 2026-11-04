---
id: TASKS-viewer-namespace-roadmap
spec: SPEC-viewer-namespace-roadmap
plan: PLAN-viewer-namespace-roadmap
---

# Task Breakdown: `SPEC-viewer-namespace-roadmap`

- [x] **Task 1**: Discover namespace milestone headers with integration regressions
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/repositories/`, `packages/devkit-viewer/tests/integration/features/browse/`
  - _Requirements: AC-01, AC-03, AC-04, AC-06_
  - **Verification**: backend discovery matrix and retained before/after fixture.
- [x] **Task 2**: Share frontend discovery with graph and cache regressions
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: parity, readiness/membership, namespace cache/page/error/abort tests.
- [x] **Task 3**: Rebuild and verify the committed distributable
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`, `docs/materials/2026-11/20261104-viewer-namespace-roadmap/`
  - _Requirements: AC-06_
  - **Verification**: frontend lint/check/test/build, generated asset check and outcome evidence.
