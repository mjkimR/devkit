---
id: TASKS-scope-boundary-candidates
spec: SPEC-scope-boundary-candidates
plan: PLAN-scope-boundary-candidates
---

# Task Breakdown: `SPEC-scope-boundary-candidates` Drop entrypoint candidates once a spec declares its code boundary

## Phase 1: Implementation

- [ ] **Task 1.1**: Declared code replaces target entrypoint candidates in a spec's scope set, with Red then Green
  input and comparison tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/`,
    `packages/devkit-spec/tests/integration/features/scope/test_inputs.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-05_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/scope/test_inputs.py`
- [ ] **Task 1.2**: CLI comparison and registry update follow the rule, observed paths still compared
  - **_Boundary**: `packages/devkit-spec/tests/integration/features/scope/test_cli.py`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/scope/test_cli.py`

## Phase 2: Living Spec contract

- [ ] **Task 2.1**: State when candidates apply in the work scope registry contract
  - **_Boundary**: `docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`
