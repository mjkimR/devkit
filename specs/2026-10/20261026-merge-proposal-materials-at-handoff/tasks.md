---
id: TASKS-merge-proposal-materials-at-handoff
spec: SPEC-merge-proposal-materials-at-handoff
plan: PLAN-merge-proposal-materials-at-handoff
---

# Task Breakdown: `SPEC-merge-proposal-materials-at-handoff` Merge existing proposal materials during handoff

## Phase 1: Implementation

- [x] **Task 1.1**: Per-leaf merge plan, guarded moves, link origins and result fields in the handoff use case, the
  conflict fix, and their tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/proposals/, packages/devkit-spec/src/devkit_spec/base/,
    packages/devkit-spec/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals`
- [x] **Task 1.2**: Render the merge fields in the handoff CLI text output, with tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/delivery/, packages/devkit-spec/tests/
  - _Requirements: AC-07_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_cli.py`

## Phase 2: Living Spec

- [x] **Task 2.1**: State the merge rules, the residual window and the result fields in the proposal incubation
  contract.
  - **_Boundary**: docs/capabilities/delivery/, docs/capabilities/governance/
  - _Requirements: AC-08_
  - **Verification**: `just rules-check`
