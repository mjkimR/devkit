---
id: TASKS-bundle-source-snapshots
spec: SPEC-bundle-source-snapshots
plan: PLAN-bundle-source-snapshots
---

# Task Breakdown: `SPEC-bundle-source-snapshots`

## Implementation

- [ ] **Task 1**: Implement static complete-provider packaging, provenance, drift/diff and coherent refresh with filesystem tests.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/models/snapshots.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/services/snapshots/`, `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/snapshots.py`, `packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py`, `packages/devkit-dist/tests/support/distsupport/snapshots.py`
  - _Requirements: AC-01, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: filesystem integration tests including unsupported input and injected rollback failure.
- [ ] **Task 2**: Expose typed operations and JSON-only CLI, with real wrapper consumers and installation guidance.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/snapshots.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/cli/bundles.py`, `packages/devkit-dist/tests/e2e/cli/test_snapshots.py`, `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/in-repo-bundle.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: public CLI and installed-wrapper tests; just test-dist and affected selector.
