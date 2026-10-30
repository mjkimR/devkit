---
id: TASKS-git-operator-result-readiness
spec: SPEC-git-operator-result-readiness
plan: PLAN-git-operator-result-readiness
---

# Task Breakdown: `SPEC-git-operator-result-readiness` Separate effect, readiness, permission and next actor in git-operator results

## Phase 1: Composed handoff commit

- [x] **Task 1.1**: Commit step, refusal error and result fields of the composed handoff, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/delivery/test_handoff_commit.py`, `packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py`, `packages/devkit-spec/tests/support/spec_support/delivery.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/delivery/test_handoff_commit.py packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py`
- [x] **Task 1.2**: Composed acceptance and CLI output carry the commit, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`, `packages/devkit-spec/tests/integration/features/delivery/test_composed_output.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
  - _Requirements: AC-02, AC-03_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/delivery/test_composed_output.py packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`

## Phase 2: Operator result and handoff guidance

- [x] **Task 2.1**: git-operator worker-input readiness, evidence separation and operator scope, with contract tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/git-operator-dispatch.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/git-operator-operations.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`
  - _Requirements: AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`
- [x] **Task 2.2**: Post-handoff link commit and sibling conflict resolution guidance, with text tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/test_post_handoff_guidance.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_post_handoff_guidance.py` and `uv run devkit sync --check`
