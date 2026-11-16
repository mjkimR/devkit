---
id: TASKS-open-feedback-fixes
spec: SPEC-open-feedback-fixes
plan: PLAN-open-feedback-fixes
---

# Task Breakdown: Fixes for four open feedback items

- [x] **Task 1**: Order the journal before the file writes in the runtime view
  - **_Boundary**: `docs/architecture/ARCH-06-runtime-view.md`, `specs/2026-11/20261116-design-document-pilot/feedback/runtime-journal-ordering.md`
  - _Requirements: AC-01_
- [x] **Task 2**: Grant the scout web search
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/scout.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`, `specs/2026-11/20261116-formal-document-templates/feedback/scout-lacks-web-search.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-02_
- [x] **Task 3**: Drop the handed-off proposal's own path from the carried boundaries
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py`, `specs/2026-11/20261116-formal-document-templates/feedback/handoff-skeleton-keeps-proposal-boundary.md`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md` (scope extension: CAP-DLV-proposal-lifecycle handoff step 1 states the carried boundaries, which now omit the removed proposal path)
  - _Requirements: AC-03, AC-04_
- [x] **Task 4**: State the workspace-relative anchor in the resolve help
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/cli/commands.py`, `packages/devkit-docs/tests/integration/features/documents/test_cli_documents.py`, `specs/2026-11/20261116-domain-model-documents/feedback/resolve-package-path-anchor.md`
  - _Requirements: AC-05_
