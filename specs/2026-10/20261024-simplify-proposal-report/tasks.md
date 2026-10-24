---
id: TASKS-simplify-proposal-report
spec: SPEC-simplify-proposal-report
plan: PLAN-simplify-proposal-report
---

# Task Breakdown: `SPEC-simplify-proposal-report` Simplify proposal review report template

## Phase 1: Implementation
- [ ] **Task 1.1**: Streamline `report.py` sections, fields, checks and template
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/report.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_report.py`
- [ ] **Task 1.2**: Update integration tests and verify language parity
  - **_Boundary**: `packages/devkit-spec/tests/integration/features/proposals/test_proposal_report.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_report.py`
- [ ] **Task 1.3**: Verification, type checks and linting
  - **_Boundary**: `packages/devkit-spec/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`
