---
id: TASKS-git-operator-planning-completion-route
spec: SPEC-git-operator-planning-completion-route
plan: PLAN-git-operator-planning-completion-route
---

# Task Breakdown: `SPEC-git-operator-planning-completion-route` Planning completion and acceptance execution route for git-operator

## Phase 1: Implementation

- [x] **Task 1.1**: Host-run composed acceptance route in the operating references and acceptance skills, with wording tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/, packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py, .devkit/installation.json (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
- [x] **Task 1.2**: `direction-handoff` as the final Planning return stage in the worker records and Planning references, with a wording test and the GOP-03 behavior test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/, packages/devkit-spec/tests/integration/bundles/spec/, packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_planning_return_stage_guidance.py packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
- [x] **Task 1.3**: Reworded composed `--check` and `--direct` usage errors, with a CLI test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py, packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
