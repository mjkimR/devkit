---
id: TASKS-reverify-carry-latest-state
spec: SPEC-reverify-carry-latest-state
plan: PLAN-reverify-carry-latest-state
---

# Task Breakdown: `SPEC-reverify-carry-latest-state` Reverify carries the latest closing state

## Phase 1: Implementation
- [ ] **Task 1.1**: Carry a named round's closing state
  - **_Boundary**: packages/devkit/src/devkit_agt/features/workflow/, packages/devkit/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_envelope_record_gaps.py`
- [ ] **Task 1.2**: Document the carry rule
  - **_Boundary**: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md
  - _Requirements: AC-01_
  - **Verification**: `just rules-check`
