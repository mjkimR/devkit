---
id: TASKS-worker-inspection-fixes
spec: SPEC-worker-inspection-fixes
plan: PLAN-worker-inspection-fixes
---

# Worker inspection tasks

- [x] **Task 1**: Fix partial-turn scope inference and independent cumulative rules comparison, with permanent regression tests and CLI evidence.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/worker/`, `packages/devkit-spec/tests/integration/features/worker/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: worker inspector integration tests; just test-affected; just lint-check spec; just check spec.
- [x] **Task 2**: Reflect inspector behavior and verified source dispositions.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `packages/devkit-spec/README.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md`, `specs/2026-10/20261028-incubation-sdd-baseline/feedback/worker-inspect-partial-turn-scope.md`, `specs/2026-10/20261028-incubation-development-guidance/feedback/worker-inspect-scoped-reconcile-base.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: independent reconcile check, sync check and cumulative rules.
