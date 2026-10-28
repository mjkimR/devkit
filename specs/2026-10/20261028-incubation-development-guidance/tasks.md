---
id: TASKS-incubation-development-guidance
spec: SPEC-incubation-development-guidance
plan: PLAN-incubation-development-guidance
---

# Task Breakdown: Incubation development guidance

- [ ] **Task 1**: Add opt-in incubation catalog assets and real selection/projection/context-preservation tests.
  - **_Boundary**: packages/devkit-catalog/
  - _Requirements: AC-01, AC-04, AC-05, AC-06_
  - **Verification**: catalog bundle tests; catalog lint/types; sync check and affected tests.
- [ ] **Task 2**: Verify actual policy consumers and adaptive, research, usage, delegation and resume scenarios with observed artifacts.
  - **_Boundary**: packages/devkit-catalog/, specs/2026-10/20261028-incubation-development-guidance/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: built-wheel docs+catalog/no-spec consumer after policy base merge; labelled semantic exercises with actual run/check evidence.
- [ ] **Task 3**: Reflect delivered ownership, interaction and adoption doorway in current contracts and guides after shared-doc write release.
  - **_Boundary**: docs/capabilities/delivery/, docs/capabilities/harness/, docs/usecases/delivery/, docs/usecases/harness/, docs/architecture/, docs/decisions/, docs/steering/, guides/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: independent reconcile comparison, rule checks and final cumulative governance.
