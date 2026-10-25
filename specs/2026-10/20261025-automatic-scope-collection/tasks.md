---
id: TASKS-automatic-scope-collection
spec: SPEC-automatic-scope-collection
plan: PLAN-automatic-scope-collection
---

# Implementation tasks

- [x] **Task 1**: Source readers, bounded Git and shared declaration parsing with source tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/`, `packages/devkit-spec/tests/`
  - _Requirements: AC-04, AC-05, AC-06, AC-08_
  - **Verification**: focused source and collector tests
- [x] **Task 2**: Explicit collection use case, inventory, comparison, output limits and CLI with integration tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/`
  - _Requirements: AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: collector/CLI regression and failure tests
- [x] **Task 3**: Silent creation registration and remove worker obligations, preserving maintenance behavior
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, `packages/devkit-spec/tests/`
  - _Requirements: AC-01, AC-02, AC-03, AC-08_
  - **Verification**: automatic registration, help, guidance and workflow regression tests
