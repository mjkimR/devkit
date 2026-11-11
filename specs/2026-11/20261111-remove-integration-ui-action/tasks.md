---
id: TASKS-remove-integration-ui-action
spec: SPEC-remove-integration-ui-action
plan: PLAN-remove-integration-ui-action
---

# Task Breakdown: `SPEC-remove-integration-ui-action` Remove the integration ui_action field

## Phase 1: Implementation

- [x] **Task 1.1**: Remove `ui_action` from the integration result and composed execution
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/tests/integration/features/integration/`, `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit tests/integration/features/integration` and `just test-affected --base main --tier all`

## Phase 2: Living Spec

- [x] **Task 2.1**: State that integration JSON carries `authority`
  - **_Boundary**: `docs/capabilities/integration/CAP-INT-mcp-services.md`
  - _Requirements: AC-03_
  - **Verification**: `rg -n ui_action docs/capabilities docs/development/reference packages/*/src` returns nothing
