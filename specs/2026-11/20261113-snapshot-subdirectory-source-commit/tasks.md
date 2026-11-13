---
id: TASKS-snapshot-subdirectory-source-commit
spec: SPEC-snapshot-subdirectory-source-commit
plan: PLAN-snapshot-subdirectory-source-commit
---

# Implementation tasks

- [x] **Task 1**: Restore subdirectory verified identity with retained identity, dirty-input and metadata-refresh regressions.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/snapshots.py`, `packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: complete snapshot integration module, independent dist tests and required repository checks.
