---
id: TASKS-review-refactor-lessons
spec: SPEC-review-refactor-lessons
plan: PLAN-review-refactor-lessons
---

# Task Breakdown: `SPEC-review-refactor-lessons` Review-refactor playbook: parallel application and preservation lessons

Tasks 1.1 to 1.3 have disjoint boundaries and run in parallel.

## Phase 1: Implementation

- [ ] **Task 1.1**: Playbook procedure
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `uv run devkit rules check packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor`; `just test devkit-catalog`
- [ ] **Task 1.2**: Decision record
  - **_Boundary**: `docs/decisions/2026-10/`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit rules check docs/decisions/2026-10`
- [ ] **Task 1.3**: Capability and use case
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-review-refactor.md`, `docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `uv run devkit rules check docs/capabilities/delivery docs/usecases/governance`

## Phase 2: Integration

- [ ] **Task 2.1**: Cross-check, full verification and review
  - **_Boundary**: the files of Phase 1
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just rules-check`; `just test devkit-catalog`; fresh review
