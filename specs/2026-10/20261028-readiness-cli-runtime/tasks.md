---
id: TASKS-readiness-cli-runtime
spec: SPEC-readiness-cli-runtime
plan: PLAN-readiness-cli-runtime
summary: "Implement and verify running CLI diagnostic guidance without changing rule validation."
---

# [TASKS-readiness-cli-runtime] CLI citation diagnostic guidance

- [x] **Task 1**: Clarify shared remediation and the existing guide, retaining a missing-command/option regression.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/rule.py`, `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/guide.md`, `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/tests/test_rule.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: Red then Green on the parameterized regression; all rule-local tests and repository checks in `PLAN-readiness-cli-runtime`.
