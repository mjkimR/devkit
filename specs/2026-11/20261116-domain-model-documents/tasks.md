---
id: TASKS-domain-model-documents
spec: SPEC-domain-model-documents
plan: PLAN-domain-model-documents
---

# Task Breakdown: Domain-model documentation

- [x] **Task 1**: Maintain two conceptual entries and selected discovery links, with independent reader evidence
  - **_Boundary**: `docs/domain/delivery-relationships.md`, `docs/domain/bundle-selection-and-installation.md`, `docs/capabilities/documents/CAP-DOCS-documentation-ownership.md`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/steering/glossary.md`, `docs/decisions/2026-11/20261116-linked-domain-relationship-views.md`, `docs/materials/2026-11/20261116-domain-model-documents/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: D1–D4 owner audit, fresh global/package readers and actual namespace/identity/ordinary-link checks recorded in Development evidence.
- [x] **Task 2**: Deliver generic domain authoring guidance through the existing docs asset and verify source
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md`, `specs/2026-11/20261116-domain-model-documents/`, `docs/materials/2026-11/20261116-domain-model-documents/`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-05, AC-06_
  - **Verification**: D5 isolated consumer delivery and D6 scoped rules, sync/check, lint/types, affected checks and selected installed-consumer E2E.
