---
id: TASKS-delivery-document-hygiene
spec: SPEC-delivery-document-hygiene
plan: PLAN-delivery-document-hygiene
---

# Task Breakdown: `SPEC-delivery-document-hygiene`

- [ ] **Task 1**: Partition the delivery capabilities and retain a section relocation map.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-delivery-roles.md`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `specs/2026-11/20261110-delivery-document-hygiene/`
  - _Requirements: AC-01, AC-02_
  - **Verification**: line counts, mechanical section comparison, document rules and independent review.
- [ ] **Task 2**: Repair exact current references and backlinks admitted by the Host.
  - **_Boundary**: `docs/usecases/delivery/`, `docs/decisions/`, `docs/capabilities/`, `docs/architecture/`
  - _Requirements: AC-02_
  - **Verification**: edits limited to the Host's exact link/trace list; no decision or behavior change.
- [ ] **Task 3**: Trim duplicate reference configuration and correct the repeated scenario number.
  - **_Boundary**: `docs/development/reference/distribution.md`, `docs/usecases/delivery/UC-drive-development-to-integration.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: unique diagnostics/examples and scenario preservation, affected tests and hygiene report.
