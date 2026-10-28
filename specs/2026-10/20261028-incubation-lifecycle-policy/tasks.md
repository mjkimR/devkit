---
id: TASKS-incubation-lifecycle-policy
spec: SPEC-incubation-lifecycle-policy
plan: PLAN-incubation-lifecycle-policy
---

# Task Breakdown

- [x] **Task 1**: Shared approach config, inspection and template with validation tests.
  - **_Boundary**: packages/devkit-dist/
  - _Requirements: AC-01, AC-02, AC-08_
  - **Verification**: config integration tests, just test-dist, lint and types.
- [x] **Task 2**: Lifecycle mutation gates, retained ownership and generic omission reporting.
  - **_Boundary**: packages/devkit/, packages/devkit-spec/, packages/devkit-docs/
  - _Requirements: AC-02, AC-03, AC-04, AC-05, AC-08_
  - **Verification**: direct/composed mutation, rule and retained artifact regression tests.
- [x] **Task 3**: Independent project readiness and retained snapshot authority.
  - **_Boundary**: packages/devkit/, packages/devkit-spec/, .devkit/architecture.toml
  - _Requirements: AC-02, AC-04, AC-06, AC-07_
  - **Verification**: real Git snapshot/provider integration and claims tests.
- [x] **Task 4**: Conditional SDD guidance and consumer installation contracts.
  - **_Boundary**: packages/devkit-spec/, docs/capabilities/, docs/usecases/, docs/architecture/, docs/decisions/, docs/steering/glossary.md, guides/, tests/e2e/smoke.sh, .devkit/config.toml, .devkit/installation.json, AGENTS.md
  - _Requirements: AC-02, AC-03, AC-08_
  - **Verification**: smoke, affected tests, sync --check and governance.
