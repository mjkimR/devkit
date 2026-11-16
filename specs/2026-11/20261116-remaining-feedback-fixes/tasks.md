---
id: TASKS-remaining-feedback-fixes
spec: SPEC-remaining-feedback-fixes
plan: PLAN-remaining-feedback-fixes
---

# Tasks: `SPEC-remaining-feedback-fixes`

- [x] **Task 1**: State the search model error scope and the module layers.
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-document-search.md`, `docs/capabilities/search/CAP-SRCH-document-search.md`
  - _Requirements: AC-01, AC-02_
- [x] **Task 2**: Complete the host reference MCP services table.
  - **_Boundary**: `docs/development/reference/host.md`
  - _Requirements: AC-03_
- [x] **Task 3**: State override results for a removed-upstream record and pin them in the regression test.
  - **_Boundary**: `docs/capabilities/distribution/CAP-DIST-workspace-ownership.md`, `packages/devkit-dist/tests/integration/features/distribution/test_override_tracking.py`
  - _Requirements: AC-04, AC-07_
  - **Verification**: `uv run pytest packages/devkit-dist/tests/integration/features/distribution/test_override_tracking.py`
- [x] **Task 4**: State the observe-only scope of the observation record.
  - **_Boundary**: `docs/capabilities/host/CAP-HOST-lifecycle-observation.md`
  - _Requirements: AC-05_
- [x] **Task 5**: Complete the capabilities README area tree.
  - **_Boundary**: `docs/capabilities/README.md`
  - _Requirements: AC-06_
- [x] **Task 6**: Record the dispositions of the six source feedback items.
  - **_Boundary**: `specs/2026-11/20261116-formal-document-coverage/feedback/search-model-invalid-scope-disagrees.md`, `specs/2026-11/20261116-formal-document-coverage/feedback/search-module-layout-omits-layers.md`, `specs/2026-11/20261116-formal-document-coverage/feedback/host-reference-mcp-table-gaps.md`, `specs/2026-11/20261116-formal-document-coverage/feedback/override-removed-upstream-command-results-unstated.md`, `specs/2026-11/20261116-formal-document-coverage/feedback/host-observation-only-observe-handler.md`, `specs/2026-11/20261116-formal-document-coverage/feedback/capabilities-readme-area-tree-incomplete.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
