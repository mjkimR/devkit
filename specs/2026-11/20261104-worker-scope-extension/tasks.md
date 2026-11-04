---
id: TASKS-worker-scope-extension
spec: SPEC-worker-scope-extension
plan: PLAN-worker-scope-extension
---

# Task Breakdown: `SPEC-worker-scope-extension`

## Phase 1: Implementation

- [ ] **Task 1**: Add worker-only typed extension records, authoring flag and validation with regression tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/models/envelope.py`, `packages/devkit/src/devkit_agt/features/workflow/services/envelope/`, `packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py`, `packages/devkit/src/devkit_agt/features/workflow/usecases/envelopes.py`, `packages/devkit/tests/integration/features/workflow/`, `packages/devkit/tests/unit/features/workflow/`
  - _Requirements: AC-01_
  - **Verification**: workflow typed evidence parser and CLI tests

- [ ] **Task 2**: Expose annotations and validate cumulative extension evidence without widening explicit scope
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/repositories/bundle.py`, `packages/devkit-spec/src/devkit_spec/features/worker/`, `packages/devkit-spec/tests/unit/features/entrypoints/`, `packages/devkit-spec/tests/unit/features/worker/`, `packages/devkit-spec/tests/integration/features/worker/`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: boundary parser and worker inspection tests

- [ ] **Task 3**: Ship matching worker/reviewer/Host guidance and reconcile retained delivery contracts
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-tasks/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md`, `packages/devkit-spec/tests/integration/bundles/spec/`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`, `docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md`, `docs/materials/2026-11/20261104-worker-scope-extension/`
  - _Requirements: AC-05_
  - **Verification**: local/cloud content tests, sync check, independent review and reconcile verification
