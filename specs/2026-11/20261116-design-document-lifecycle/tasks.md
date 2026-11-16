---
id: TASKS-design-document-lifecycle
spec: SPEC-design-document-lifecycle
plan: PLAN-design-document-lifecycle
---

# Task Breakdown: `SPEC-design-document-lifecycle`

- [x] **Task 1**: Formal role impact/scaffold and SDD maintenance guidance with integration and composed tests
  - **_Boundary**: `packages/devkit-spec/`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: Scaffold, entrypoint, bundle guidance, adoption and composed SDD E2E tests.

- [x] **Task 2**: Adaptive source-bound formal maintenance, retained map and installed/composed proof
  - **_Boundary**: `packages/devkit-adaptive/`
  - _Requirements: AC-01, AC-04, AC-05_
  - **Verification**: Adaptive bundle guidance, installed consumer and composed no-implicit-SDD E2E.

- [x] **Task 3**: Current delivery contracts and source-identified comparison evidence
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`, `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`, `docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md`, `docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md`, `docs/usecases/governance/UC-keep-the-living-spec-consistent.md`, `docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md`, `docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md`, `docs/usecases/harness/UC-adopt-in-an-existing-repository.md`, `docs/decisions/2026-11/20261116-formal-document-delivery-integration.md`, `docs/materials/2026-11/20261116-design-document-lifecycle/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: Rules, actual source comparison and full L1–L4 matrix. CAP-TRACE core §§1,3.1–3.3 and immutable pins remain unchanged.
