---
id: TASKS-worker-source-completion
spec: SPEC-worker-source-completion
plan: PLAN-worker-source-completion
---

# Tasks: `SPEC-worker-source-completion`

- [ ] **Task 1**: Retain same-path open-to-resolved source scope with Git-backed regression and preservation tests.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inputs.py`, `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py`, `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `specs/2026-11/feedback/20261104-worker-inspect-resolved-source-scope.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: Worker integration tests, lint, types, CI rules and affected tests.
