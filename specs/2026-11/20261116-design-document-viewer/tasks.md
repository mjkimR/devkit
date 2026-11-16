---
id: TASKS-design-document-viewer
spec: SPEC-design-document-viewer
plan: PLAN-design-document-viewer
---

# Task Breakdown: `SPEC-design-document-viewer`

- [ ] **Task 1**: Formal identity, navigation, retirement and shared reference context with browser tests
  - **_Boundary**: `packages/devkit-viewer/frontend/`
  - _Requirements: AC-01, AC-02, AC-03, AC-05_
  - **Verification**: Document, supersession, Read and cold Files regression tests.

- [ ] **Task 2**: Source-safe artifact reader, raw and Back flow with byte/source/disposal tests
  - **_Boundary**: `packages/devkit-viewer/frontend/`
  - _Requirements: AC-04, AC-05, AC-06_
  - **Verification**: Artifact API/component and composed maintenance tests.

- [ ] **Task 3**: Generic backend/public/package evidence and handbook source recognition
  - **_Boundary**: `packages/devkit-viewer/`, `scripts/handbook.py`, `tools/devkit-dev/tests/integration/test_handbook_script.py`
  - _Requirements: AC-01, AC-06, AC-07_
  - **Verification**: Backend/handbook tests, frontend commands, public tarball/wheel inspection and generated static consistency.

- [ ] **Task 4**: Current viewer reading/UX/reference contracts and source-identified evidence
  - **_Boundary**: `docs/capabilities/viewer/CAP-VIEW-repository-viewer.md`, `docs/capabilities/delivery/CAP-DLV-release-handbook.md`, `docs/usecases/viewer/UC-read-formal-document.md`, `docs/usecases/viewer/UC-read-decision-supersession.md`, `docs/ux/`, `docs/steering/ux-objects.md`, `docs/development/reference/viewer.md`, `docs/materials/2026-11/20261116-design-document-viewer/`, `packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: Full V1–V4 matrix, implemented UX findings, current contract comparison and rules. UX writes restricted to the three planned new IDs and affected UX-view-decision/UX-decision-supersession; immutable core-contract bytes unchanged.
