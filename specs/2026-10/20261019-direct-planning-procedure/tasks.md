---
id: TASKS-direct-planning-procedure
spec: SPEC-direct-planning-procedure
plan: PLAN-direct-planning-procedure
---

# Task Breakdown: `SPEC-direct-planning-procedure` Planning procedure reachable from the spec skill for any executor

## Phase 1: Implementation
- [x] **Task 1.1**: Move the contract's Planning steps 2 to 6 into `spec/references/planning.md`, link it from the
  routing table's `proposal` row and leave the `planning-worker` contract with step 1, a step citing the reference and
  the nested-role rule
  - **_Boundary**: harness/
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/test_bundle_budgets.py`
- [x] **Task 1.2**: Move the pinned phrases in `test_role_contracts.py` to the reference, assert their absence from the
  contract and replace the contract with the reference in `test_effort_procedure.py` `CITING`
  - **_Boundary**: harness/
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/test_role_contracts.py packages/devkit-spec/tests/test_effort_procedure.py`

## Phase 2: Living Spec
- [x] **Task 2.1**: Update `CAP-DLV-delivery-workflows` §4.6 (the `planning-worker` row and the sentence on where a
  role's procedure lives) and record it in `reconcile.md`
  - **_Boundary**: delivery/
  - _Requirements: AC-05_
  - **Verification**: `just rules-check`
