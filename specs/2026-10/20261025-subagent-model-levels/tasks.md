---
id: TASKS-subagent-model-levels
spec: SPEC-subagent-model-levels
plan: PLAN-subagent-model-levels
---

# Task Breakdown: `SPEC-subagent-model-levels`

- [ ] **Task 1**: Typed policy, validation and native resolution with resolver tests.
  - **_Boundary**: packages/devkit-dist/src/devkit_dist/features/distribution/, packages/devkit-dist/tests/
  - _Requirements: AC-02, AC-03, AC-04, AC-05_
  - **Verification**: just test dist distribution
- [ ] **Task 2**: Shared config, inventory and sync policy plumbing with integration tests.
  - **_Boundary**: packages/devkit-dist/src/devkit_dist/features/distribution/, packages/devkit-dist/src/devkit_dist/features/project/, packages/devkit-dist/tests/
  - _Requirements: AC-01, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: just test dist distribution
- [ ] **Task 3**: Shipped role inheritance and matching bundle checks.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/, packages/devkit-spec/tests/
  - _Requirements: AC-01, AC-07_
  - **Verification**: just test spec bundles
