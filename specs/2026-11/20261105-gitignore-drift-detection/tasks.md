---
id: TASKS-gitignore-drift-detection
spec: SPEC-gitignore-drift-detection
plan: PLAN-gitignore-drift-detection
---

# Task Breakdown: SPEC-gitignore-drift-detection

- [x] **Task 1**: Add read-only projection Git diagnostics and real-Git regression coverage.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/`, `packages/devkit-dist/src/devkit_dist/features/distribution/models/errors.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py`, `packages/devkit-dist/tests/integration/features/distribution/`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/capabilities/distribution/CAP-DIST-workspace-ownership.md`, `docs/development/reference/distribution.md` (scope extension: document new distribution advisory codes)
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test-affected`, `just lint-check dist`, `just check dist`, `just test-dist`, `uv run devkit rules check`
