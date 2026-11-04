---
id: TASKS-entrypoint-generated-filter
spec: SPEC-entrypoint-generated-filter
plan: PLAN-entrypoint-generated-filter
---

# Task Breakdown: `SPEC-entrypoint-generated-filter`

- [ ] **Task 1**: Filter generated ownership during derivation, preserving scope classification, with regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/repositories/managed.py`,
    `packages/devkit-spec/src/devkit_spec/features/entrypoints/services/derive.py`,
    `packages/devkit-spec/src/devkit_spec/features/entrypoints/models/derive.py`,
    `packages/devkit-spec/tests/integration/features/entrypoints/test_managed_outputs.py`
  - _Requirements: AC-01, AC-02, AC-04, AC-05_
  - **Verification**: typed receipt and path-policy integration tests; recorded real-bundle comparison.
- [ ] **Task 2**: Guard explicit selector synthesis and apply with CLI regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/usecases/derive.py`,
    `packages/devkit-spec/tests/integration/features/entrypoints/test_cli.py`
  - _Requirements: AC-03_
  - **Verification**: generated exact and directory selectors fail before writing; authored selectors pass.
