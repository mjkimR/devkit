---
id: TASKS-incubation-discovery-teams
spec: SPEC-incubation-discovery-teams
plan: PLAN-incubation-discovery-teams
---

# Implementation Tasks for SPEC-incubation-discovery-teams

- [ ] **Task 1**: Add the explicit research entry and optional role contracts, with native projection and preservation checks.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/incubation/bundle/`, `packages/devkit-catalog/tests/integration/bundles/test_incubation.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: actual bundle loading, three-host sync, role contract parsing, skill validation and guidance inspection.

- [ ] **Task 2**: Extend consumer documentation and installed docs/catalog-only verification.
  - **_Boundary**: `packages/devkit-catalog/README.md`, `packages/devkit-catalog/tests/e2e/bundles/incubation/test_installed_consumer.py`
  - _Requirements: AC-01, AC-08_
  - **Verification**: installed wheels expose both skills and six roles without devkit-spec; remove/reselect preserves context and research notes.

- [ ] **Task 3**: Exercise bounded discovery, actual delegated roles and fresh-context resume; retain observed evidence.
  - **_Boundary**: `specs/2026-10/20261029-incubation-discovery-teams/`, isolated ignored consumer/probe paths assigned per run
  - _Requirements: AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-09_
  - **Verification**: matched fixture runs, actual role outputs, source inspection, artifact review, scope checks and independent resume; report limited coverage honestly.
