---
id: TASKS-envelope-answer-decider
spec: SPEC-envelope-answer-decider
plan: PLAN-envelope-answer-decider
---

# Task Breakdown: `SPEC-envelope-answer-decider` Record the decider of each answer and guard reverify closures

## Phase 1: Implementation
- [ ] **Task 1.1**: Record and validate a per-answer decider
  - **_Boundary**: packages/devkit/src/devkit_agt/features/workflow/, packages/devkit/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_envelope_answer_decider.py`
- [ ] **Task 1.2**: Refuse a reverify that closes a closed finding
  - **_Boundary**: packages/devkit/src/devkit_agt/features/workflow/, packages/devkit/tests/
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_envelope_answer_decider.py`

## Phase 2: Contracts and guidance
- [ ] **Task 2.1**: Document the decider and the closed-finding refusal
  - **_Boundary**: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md, docs/capabilities/delivery/CAP-DLV-cli-and-output.md, docs/development/reference/workflow.md
  - _Requirements: AC-01, AC-03, AC-05, AC-06_
  - **Verification**: `just rules-check`
- [ ] **Task 2.2**: Name the decider in worker records and payload guidance
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/, packages/devkit-spec/tests/, AGENTS.md, .devkit/installation.json
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_answer_decider_guidance.py`
