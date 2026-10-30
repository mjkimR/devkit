---
id: TASKS-local-orch-resource-manager
spec: SPEC-local-orch-resource-manager
plan: PLAN-local-orch-resource-manager
---

# Task Breakdown: `SPEC-local-orch-resource-manager`

- [x] **Task 1**: Register git-operator, its operating procedure and Host dispatch, with contract/projection checks
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/`, `packages/devkit-spec/tests/integration/bundles/spec/`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: focused bundle tests, lint/type checks, `just test-affected --base main`, `devkit sync --check`
- [ ] **Task 2**: Exercise repeated jobs and record matched same-head role-disabled evidence and limits
  - **_Boundary**: `docs/materials/2026-10/20261030-local-orch-resource-manager/`, `specs/2026-10/20261030-local-orch-resource-manager/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: selected Terra medium native continuation, recorded fixture/replay distinctions and host limits
