---
id: TASKS-cli-tool-layout-rules
spec: SPEC-cli-tool-layout-rules
plan: PLAN-cli-tool-layout-rules
---

# Task Breakdown: `SPEC-cli-tool-layout-rules` Feature layout and layer rules for cli-tool

## Phase 1: Rules

- [x] **Task 1.1**: Add `RULE-cli-tool-layout` and `RULE-cli-tool-layers` with guides and tests, and register them
  - **_Boundary**: `packages/devkit-catalog/`, `tests/e2e/smoke.sh`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test catalog`, `just smoke`

## Phase 2: Contract

- [x] **Task 2.1**: Update the instruction, `CAP-CLI-agent-cli-toolkit`, the catalog README and the recommendation
  - **_Boundary**: `packages/devkit-catalog/`, `docs/capabilities/cli/`, `guides/install/bundle-recommendations.md`
  - _Requirements: AC-08_
  - **Verification**: `just rules-check`
