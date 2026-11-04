---
id: TASKS-maintenance-history
spec: SPEC-maintenance-history
plan: PLAN-maintenance-history
---

# Task Breakdown: `SPEC-maintenance-history`

- [x] **Task 1**: Local run identity, canonical storage, evidence freezing and validation with unit tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/maintenance_history/models/`, `packages/devkit/src/devkit_agt/features/maintenance_history/repositories/`, `packages/devkit/src/devkit_agt/features/maintenance_history/services/`, `packages/devkit/tests/unit/features/maintenance_history/`, `.devkit/architecture.toml`
  - _Requirements: AC-02, AC-03, AC-08_
  - **Verification**: `just test devkit tests/unit/features/maintenance_history`
- [x] **Task 2**: GitHub atomic publication, initialization, retrieval and amendments with integration tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/maintenance_history/`, `packages/devkit/tests/integration/features/maintenance_history/`, `packages/devkit/tests/support/`
  - _Requirements: AC-01, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test devkit tests/integration/features/maintenance_history`
- [x] **Task 3**: Agent-first command family, config defaults and discovery with CLI tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/maintenance_history/`, `packages/devkit/pyproject.toml`, `packages/devkit/README.md`, `uv.lock`, `packages/devkit/tests/integration/features/maintenance_history/`
  - _Requirements: AC-09_
  - **Verification**: `uv run devkit maintenance history --help`
- [x] **Task 4**: Four playbooks and durable contracts with catalog content checks
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/maintenance/`, `packages/devkit-catalog/tests/`, `docs/capabilities/delivery/`, `docs/usecases/governance/`, `docs/development/reference/`, `docs/steering/glossary.md`, `docs/decisions/2026-11/20261104-history-branch-publication.md`, `docs/decisions/2026-11/20261104-inspected-state-identity.md`
  - _Requirements: AC-09_
  - **Verification**: `just test devkit-catalog`
- [ ] **Task 5**: Labelled live GitHub exercise and sanitized evidence
  - **_Boundary**: `docs/materials/2026-11/20261104-maintenance-history/`, `specs/2026-11/20261104-maintenance-history/`
  - _Requirements: AC-10_
  - **Verification**: Run the documented exercise only with a user-selected destination and external mutation authority.
