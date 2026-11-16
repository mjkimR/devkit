---
id: TASKS-formal-document-kinds
spec: SPEC-formal-document-kinds
plan: PLAN-formal-document-kinds
---

# Task Breakdown: `SPEC-formal-document-kinds`

- [x] **Task 1**: Formal Kind/model/discovery contracts with real new-kind regression tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/`, `packages/devkit-docs/tests/unit/features/documents/`, `packages/devkit-docs/tests/integration/features/documents/`
  - _Requirements: AC-01, AC-02, AC-07_
  - **Verification**: Owned document unit/integration suites.

- [x] **Task 2**: Canonical role schema, artifact and applicable entrypoint governance with tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/`, `packages/devkit-docs/tests/unit/features/governance/`, `packages/devkit-docs/tests/integration/features/governance/`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-07_
  - **Verification**: Rule unit/integration/wrapper suites and maintenance fixtures.

- [x] **Task 3**: Shipped formal authoring assets and neutral installed-consumer coverage
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`, `packages/devkit-docs/tests/integration/bundles/docs/`, `packages/devkit-docs/tests/e2e/bundles/docs/`, `packages/devkit-docs/README.md`, `.devkit/installation.json` (sync output), `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`
  - _Requirements: AC-05, AC-07_
  - **Verification**: Distribution inventories, sync/get-context and built-wheel consumer E2E.

- [x] **Task 4**: Five formal node migrations and current owner/navigation reflection
  - **_Boundary**: `docs/designs/`, `docs/domain/`, `docs/operations/`, `docs/capabilities/documents/`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md`, `docs/usecases/documents/UC-find-the-right-documents.md`, `docs/usecases/governance/UC-keep-the-living-spec-consistent.md`, `docs/architecture/`, `docs/decisions/`, `docs/development/reference/`, `docs/steering/glossary.md`, `docs/README.md`, `docs/materials/2026-11/20261116-formal-document-kinds/`
  - _Requirements: AC-03, AC-04, AC-06, AC-07_
  - **Verification**: Migration ingress/source-link audit, F1–F6 matrix, rules and affected checks. CAP-TRACE edits restricted to §§1,3.1–3.3; other docs restricted to agreed contract/ingress reflection; pinned core-contract unchanged.
