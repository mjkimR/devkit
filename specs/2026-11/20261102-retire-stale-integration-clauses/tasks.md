---
id: TASKS-retire-stale-integration-clauses
spec: SPEC-retire-stale-integration-clauses
plan: PLAN-retire-stale-integration-clauses
---

# Task Breakdown: `SPEC-retire-stale-integration-clauses` Retire stale integration ADR clauses

## Phase 1: Implementation

- [x] **Task 1.1**: New ADR and partial-supersession lines
  - **_Boundary**: `docs/decisions/2026-11/20261102-retire-stale-integration-approval-clauses.md`,
    `docs/decisions/2026-10/20261022-local-and-pull-request-integration.md`,
    `docs/decisions/2026-10/20261022-configuration-language-and-rendering.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run devkit rules check docs/decisions`
- [x] **Task 1.2**: Source feedback dispositions and checks
  - **_Boundary**: `specs/2026-11/20261102-adr-normative-outcomes/feedback/pr-auto-admin-refusal-point.md`,
    `specs/2026-11/20261102-adr-normative-outcomes/feedback/stale-approval-form-clause.md`,
    `specs/2026-11/20261102-adr-normative-outcomes/feedback/bundle-text-bare-devkit-commands.md`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check`; `just test-affected`
