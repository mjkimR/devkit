---
id: FB-integration-readiness-loads-new-rule-with-base-code
title: Integration readiness loads a branch's new rule with the base checkout's code
scope: repo
kind: friction
category: tool-error
target: devkit integration prepare/integrate (unit readiness, CI rules snapshot)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-integration-readiness-loads-new-rule-with-base-code] Integration readiness loads a branch's new rule with the base checkout's code

## 1. Friction / Question (friction, question)

- **Context**: Integrating `dev-foundation-documents`, which adds `RULE-steering-documents`, whose bundled rule
  package imports its implementation from `devkit_spec.features.governance.usecases.steering_documents`.
- **Expectation**: Readiness evaluates the branch with the code that the integration lands.
- **Actual**: `devkit integration prepare|integrate`, run from the retained base checkout, loads the branch's
  receipt-listed rule packages with the base checkout's installed `devkit_spec`, which lacks the new module, and refuses
  with `INTEGRATION_NOT_READY` (BLOCKED) carrying `RULES_RUN_FAILED` / `RULES_LOAD_FAILED`. Every change that adds a
  bundled rule whose implementation lives in package code meets this.
- **Workaround (or Interpretation Chosen)**: With the user's explicit approval, ran the same integration command from
  the base checkout with the task worktree's `.venv/bin/devkit`, so readiness used the branch's code; the branch's own
  checks had already passed.
- **Suggestion**: Evaluate readiness and the CI rules snapshot with the source branch's code (for example in the task
  worktree's environment), or report the mismatch with its own code and a directive instead of a BLOCKED refusal.

## Diagnostic Details

- **Reproduction**: Add a bundled rule whose package imports a new module of `devkit_spec`, then run
  `devkit integration prepare <branch> --task-kind unit ... --route local` from the base checkout.
- **Expected / Actual**: Expected readiness to pass as the branch's checks did; actual `No module named
  'devkit_spec.features.governance.usecases.steering_documents'`.
- **Versions**: base `893d3892`; branch head `6e5bb3ec`.
- **Related Assets**: `CAP-GOV-evaluation-lifecycle` section on snapshot gates, `CAP-GOV-rule-authoring` rule loading.

- **Disposition**: `SPEC-integration-readiness-branch-code`: integration names a synchronized rule of the source (or the result) that imports code the running runtime lacks with `INTEGRATION_RULE_RUNTIME_MISMATCH` before readiness, directing a run from a runtime built from the source after separately granted authority; automatic evaluation with the source's environment is a Non-Goal. Verified by `packages/devkit/tests/integration/features/integration/test_rule_runtime.py`, the Red/Green regression `packages/devkit-spec/tests/e2e/features/delivery/test_integration_rule_runtime.py`, and the guard on branch head `6e5bb3ec` naming `devkit_spec.features.governance.usecases.steering_documents` when that module is absent.
