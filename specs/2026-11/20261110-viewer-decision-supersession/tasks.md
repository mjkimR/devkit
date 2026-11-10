---
id: TASKS-viewer-decision-supersession
spec: SPEC-viewer-decision-supersession
plan: PLAN-viewer-decision-supersession
---

# Task Breakdown: `SPEC-viewer-decision-supersession`

- [x] **Task 1**: Derive canonical supersession relations and source-aware replacement text with parity fixtures.
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/document/supersession.ts`, `packages/devkit-viewer/frontend/src/lib/features/document/supersession.test.ts`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just viewer test`
- [x] **Task 2**: Integrate the shared summary in Read, Files and PADR chapters with loading, navigation and source guards.
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/features/document/`, `packages/devkit-viewer/frontend/src/lib/features/knowledge/ChapterSection.svelte`, `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte`, `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.test.ts`, `packages/devkit-viewer/frontend/src/lib/SddViewer.svelte`, `packages/devkit-viewer/frontend/src/lib/SddViewer.test.ts`
  - _Requirements: AC-01, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: `just viewer lint`, `just viewer check`, `just viewer test`
- [x] **Task 3**: Build the committed viewer assets and verify package compatibility.
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`
  - _Requirements: AC-08_
  - **Verification**: `just viewer pack`, `just viewer build`, `uv run devkit generated check viewer-assets`

- [x] **Task 4**: Verify exact viewer UC screen citations while retaining nonscreen repository UC coverage.
  - **_Boundary**: `packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`
  - _Requirements: AC-08_
  - **Verification**: targeted native pytest and affected checks.

The Host explicitly admitted Task 4's exact cross-package test path after its no-screens repository assumption
failed on the first approved viewer UX use case. All other devkit-docs production and test paths remain excluded.
