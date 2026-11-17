---
id: TASKS-formal-doc-padding-trim
spec: SPEC-formal-doc-padding-trim
plan: PLAN-formal-doc-padding-trim
---

# Task Breakdown: `SPEC-formal-doc-padding-trim` Trim padding from formal document guidance and documents

## Phase 1: Docs bundle

- [x] **Task 1.1**: Narrow the formal templates and writing instructions, move shared steps to living-spec-writing and document-writing, and drop inactive elements from the other templates and instructions
  - **_Boundary**: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/domain.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/operations.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/capability.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/usecase.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/ux.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/milestone.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/design-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/domain-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/operations-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/document-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md, .devkit/installation.json (sync output)
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/bundles/spec packages/devkit-docs/tests/integration/bundles/docs`; the `rg` commands of AC-01, AC-02 and AC-04
- [x] **Task 1.2**: Merge the two routing tables into one fact-type table in the capability and living-spec-writing, and update the capability's section contracts and the table test
  - **_Boundary**: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md, packages/devkit-spec/tests/integration/bundles/spec/test_formal_doc_checkpoints_guidance.py
  - _Requirements: AC-03, AC-05_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/bundles/spec/test_formal_doc_checkpoints_guidance.py`

## Phase 2: Living Spec documents

- [x] **Task 2.1**: Apply the audit to the formal documents and fold DESIGN-distribution-transactions into its detail, with the reference repairs and the viewer test
  - **_Boundary**: docs/designs/, docs/domain/, docs/operations/, docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md, specs/2026-11/20261116-design-bundle-layout/feedback/viewer-adopts-bundle-grammar.md, packages/devkit-viewer/frontend/src/features/knowledge/FormalReading.test.ts
  - _Requirements: AC-06, AC-07_
  - **Verification**: the `rg` commands of AC-06; `uv run devkit docs resolve DESIGN-distribution-transactions`; `uv run devkit rules check docs/designs docs/domain docs/operations`; the viewer frontend check
- [x] **Task 2.2**: Move the handoff mechanism clauses from CAP-DLV-proposal-lifecycle into DESIGN-proposal-handoff and resolve the source feedback
  - **_Boundary**: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md, docs/designs/delivery/DESIGN-proposal-handoff/design.md, specs/2026-11/20261116-formal-docs-feedback-handoff/feedback/proposal-lifecycle-capability-holds-mechanism-detail.md
  - _Requirements: AC-08_
  - **Verification**: the `rg` command of AC-08 exits `1`
- [x] **Task 2.3**: Run the full verification set
  - **_Boundary**: .devkit/installation.json (sync output)
  - _Requirements: AC-09_
  - **Verification**: `just lint-check`; `uv run devkit generated check`; `uv run devkit rules check --ci --base main`; `just test-affected --base main`
