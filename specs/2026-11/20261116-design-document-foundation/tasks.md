---
id: TASKS-design-document-foundation
spec: SPEC-design-document-foundation
plan: PLAN-design-document-foundation
---

# Task Breakdown: `SPEC-design-document-foundation`

## Phase 1: Implementation

- [ ] **Task 1**: Establish shared ownership and architecture boundary
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-documentation-ownership.md`, `docs/architecture/README.md`, `docs/decisions/2026-11/20261116-documentation-ownership-and-linked-design-entries.md`
  - _Requirements: AC-01_
  - **Verification**: Ownership case audit and document rules.

- [ ] **Task 2**: Maintain transaction entry/detail and selected owner route
  - **_Boundary**: `docs/designs/distribution-transactions.md`, `docs/designs/distribution-transactions/file-directory-replacement.md`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`
  - _Requirements: AC-02, AC-03_
  - **Verification**: Independent global reader and source/link audit.

- [ ] **Task 3**: Deliver generic instructions and optional template
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/architecture-writing.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design-template.md`
  - _Requirements: AC-05_
  - **Verification**: Consumer fixture sync and source asset rules.

- [ ] **Task 4**: Validate package/global navigation and retain F1–F6 evidence
  - **_Boundary**: `docs/materials/2026-11/20261116-design-document-foundation/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: Package fixture, independent reader, rules and affected tests.
