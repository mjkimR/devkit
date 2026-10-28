---
id: TASKS-performance-pass
spec: SPEC-performance-pass
plan: PLAN-performance-pass
---

# Task Breakdown: `SPEC-performance-pass` Performance pass maintenance playbook

## Phase 1: Implementation

- [x] **Task 1.1**: Author the router-structured `performance-pass` playbook
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass/`
  - _Requirements: AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: `uv run devkit rules check --phase hygiene packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass`
- [x] **Task 1.2**: Declare the asset and the `performance` preset, with bundle tests and catalog documentation
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/bundle.toml`, `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`, `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-11_
  - **Verification**: `just test devkit-catalog`
