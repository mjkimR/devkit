---
id: TASKS-adr-admission-and-trace-format
spec: SPEC-adr-admission-and-trace-format
plan: PLAN-adr-admission-and-trace-format
---

# Task Breakdown: `SPEC-adr-admission-and-trace-format` ADR admission criteria and restatement trace format

## Phase 1: Guidance

- [ ] **Task 1.1**: Admission criteria and trace format in decision-writing, the template and Planning, with tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`,
    `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_writing_guidance.py`

## Phase 2: Existing ADRs

- [ ] **Task 2.1**: Rewrite the markers of the 13 ADRs into the trace format
  - **_Boundary**: `docs/decisions/2026-10/`, `docs/decisions/2026-11/`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/decisions`

## Phase 3: Checks

- [ ] **Task 3.1**: Whole-change checks
  - **_Boundary**: `specs/2026-11/20261102-adr-admission-and-trace-format/`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit rules check`; `just test-affected`
