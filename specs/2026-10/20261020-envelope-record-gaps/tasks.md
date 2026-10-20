---
id: TASKS-envelope-record-gaps
spec: SPEC-envelope-record-gaps
plan: PLAN-envelope-record-gaps
---

# Task Breakdown: `SPEC-envelope-record-gaps` Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries

- [x] **Task 1**: Reverify closes challenger rounds: reference pattern, deciding state, `--from`, challenger findings
  refusal and the `review=` check output, with tests
  - **_Boundary**: `packages/devkit/src/devkit/workflow/unit/envelope/`, `packages/devkit/src/devkit/workflow/cli/envelope.py`,
    `packages/devkit/tests/workflow/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit workflow`
- [x] **Task 2**: Answer envelopes carry `settles`, authored with `--settle`, with tests
  - **_Boundary**: `packages/devkit/src/devkit/workflow/unit/envelope/`, `packages/devkit/src/devkit/workflow/cli/envelope.py`,
    `packages/devkit/tests/workflow/`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit workflow`
- [x] **Task 3**: `RULE-proposal-boundaries` with its guide, tests and bundle registration
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/rules/`, `packages/devkit-spec/src/devkit_spec/entrypoints/paths.py`,
    `packages/devkit-spec/src/devkit_spec/bundle/rules/proposal_boundaries/`, `packages/devkit-spec/src/devkit_spec/bundle/bundle.toml`,
    `packages/devkit-spec/tests/`
  - _Requirements: AC-08, AC-09, AC-10_
  - **Verification**: `just test devkit-spec`
- [ ] **Task 4**: Bundle procedure text (review loop, Planning, worker records, envelope reference, `sdd-proposal`,
  proposal template) with wording tests, and the linked source feedback's disposition
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/`,
    `packages/devkit-spec/src/devkit_spec/bundle/workflows/sdd-proposal.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/templates/proposal.md`, `packages/devkit-spec/tests/`,
    `specs/2026-10/feedback/20261019-review-loop-round-count-across-procedure-change.md`
  - _Requirements: AC-11_
  - **Verification**: `just test devkit-spec tests/test_effort_procedure.py`
