---
id: TASKS-worker-audit-known-host-advance
spec: SPEC-worker-audit-known-host-advance
plan: PLAN-worker-audit-known-host-advance
---

# Task Breakdown: `SPEC-worker-audit-known-host-advance` Stop requiring an unchanged base checkout in worker validation

## Phase 1: Implementation

- [x] **Task 1.1**: Drop the base equality from the worker and payload references, add the own-envelope condition, with
  the contract test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`, `.devkit/installation.json`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_role_contracts.py`, `uv run devkit sync --check`
- [x] **Task 1.2**: Characterization test: a base advance never enters or blocks the audited range
  - **_Boundary**: `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec tests/integration/features/worker/test_worker_inspect.py`
- [x] **Task 1.3**: Living Spec: the capability's acceptance and base-checkout wording, the ADR pointer line
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/decisions/2026-10/20261022-orchestration-workers.md`, `docs/decisions/2026-10/20261030-drop-the-base-checkout-equality-from-worker-validation.md`
  - _Requirements: AC-02_
  - **Verification**: `just rules-check`
