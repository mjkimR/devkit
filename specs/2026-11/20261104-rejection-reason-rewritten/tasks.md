---
id: TASKS-rejection-reason-rewritten
spec: SPEC-rejection-reason-rewritten
plan: PLAN-rejection-reason-rewritten
---

# Task Breakdown: `SPEC-rejection-reason-rewritten` Rejection records carry a rewritten decision, not a quote

## Phase 1: Bundle wording and tests

- [x] **Task 1.1**: Reword the rejection sentence of the `sdd-proposal` workflow and Step 4 of the `feedback-hygiene`
  playbook, and pin both in a guidance test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/SKILL.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_workflows.py`
  - _Requirements: AC-01, AC-02, AC-07_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_workflows.py`; the `rg` command of AC-07
- [x] **Task 1.2**: Reword the proposal scaffold's Lifecycle comment
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals`

## Phase 2: Records that follow the rule

- [x] **Task 2.1**: Restate the rejection ADR's reason as a decision sentence and resolve the source feedback
  - **_Boundary**: `docs/decisions/2026-11/20261104-reject-ux-rules-path-exclusion.md`,
    `specs/2026-11/feedback/20261104-rejection-reason-quoted-verbatim.md`
  - _Requirements: AC-05, AC-06_
  - **Verification**: `uv run devkit rules check docs/decisions/2026-11/20261104-reject-ux-rules-path-exclusion.md specs/2026-11/feedback/20261104-rejection-reason-quoted-verbatim.md`
- [x] **Task 2.2**: Name the decision-sentence form in `CAP-DLV-proposal-planning` rule 9
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
