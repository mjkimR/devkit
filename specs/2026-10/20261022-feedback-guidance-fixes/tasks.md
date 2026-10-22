---
id: TASKS-feedback-guidance-fixes
spec: SPEC-feedback-guidance-fixes
plan: PLAN-feedback-guidance-fixes
---

# Task Breakdown: `SPEC-feedback-guidance-fixes` Feedback Guidance Fixes

## Phase 1: Report template route

- [x] **Task 1.1**: Template use case, field-class refusals, CLI `--template`, read-only MCP tool and tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/report.py`,
    `packages/devkit-spec/src/devkit_spec/features/proposals/mcp/report.py`,
    `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_report.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_report.py`
- [x] **Task 1.2**: `spec-review-proposal` names the template route
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_cloud_guidance.py`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_cloud_guidance.py`

## Phase 2: Workflow records and guides

- [x] **Task 2.1**: Reverify `[FIX]` for a reconcile-check source, answer-correction acceptance test
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`,
    `packages/devkit/tests/integration/features/workflow/test_envelope_record_gaps.py`
  - _Requirements: AC-06, AC-08_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_envelope_record_gaps.py`
- [x] **Task 2.2**: PADR withdrawal and answer-correction guidance
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md`
  - _Requirements: AC-07, AC-08_
  - **Verification**: `uv run devkit sync` and reading the synced references

## Phase 3: Handoff placement

- [x] **Task 3.1**: Carried contract section for validation scenarios
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/services/body.py`,
    `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/specs.py`,
    `packages/devkit-spec/tests/unit/features/proposals/test_proposal_body.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py`
  - _Requirements: AC-09_
  - **Verification**: `just test devkit-spec tests/unit/features/proposals tests/integration/features/proposals`

## Phase 4: Living Spec and checks

- [x] **Task 4.1**: Living Spec reflection, sync, source-feedback resolution and checks
  - **_Boundary**: `docs/capabilities/delivery/`, `docs/capabilities/harness/`, `.devkit/installation.json`,
    the five source feedback files named in spec section 6
  - _Requirements: AC-10_
  - **Verification**: `just test-affected`, `uv run devkit rules check`, `uv run devkit status`
