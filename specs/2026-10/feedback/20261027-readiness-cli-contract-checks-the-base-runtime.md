---
id: FB-readiness-cli-contract-checks-the-base-runtime
title: Integration readiness checks CLI citations against the base runtime, not the branch
scope: repo
kind: friction
category: tool-error
target: devkit integration prepare (devkit-spec readiness provider) with RULE-cli-contract
origin: agent
severity: blocked
recurring: false
status: promoted
created_at: 2026-10-27
---

# [FB-readiness-cli-contract-checks-the-base-runtime] Integration readiness checks CLI citations against the base runtime, not the branch

## 1. Friction / Question (friction, question)

- **Context**: Integrating `dev-bug-polish` on the local route. The branch adds `--given` to
  `devkit workflow answer|return|handoff` and documents it in `CAP-DLV-cli-and-output`, as the contract requires.
- **Expectation**: Readiness evaluates the branch as CI does at the branch head: `just rules-check` in the branch
  worktree passes, so readiness passes.
- **Actual**: `devkit integration prepare` must run from the retained base checkout (`WORKTREE_RUN_FROM_BASE`), and
  `RULE-cli-contract` verifies citations against the click tree of the running `devkit` invocation, which is the
  base checkout's code. The new options are unknown there, so readiness refuses with `INTEGRATION_NOT_READY`. Any
  branch that adds a `devkit` CLI option and documents it in the same branch cannot pass local readiness in this
  repository.
- **Workaround (or Interpretation Chosen)**: The user decided to integrate without the provider's readiness and
  verify on the base branch after the merge, where the running runtime includes the new options.
- **Suggestion**: When the branch changes the devkit runtime the check would run (the devkit source in this
  repository, or the locked devkit version in a consumer), leave `RULE-cli-contract` out of readiness and rely on CI
  at the branch head; otherwise keep the base-runtime check, so ordinary consumer branches pay no extra cost. Prefer
  this automatic decision to a user setting, which would be switched off and forgotten. Consumers can hit the same
  refusal on a branch that upgrades devkit and updates citations of new options (hand-written or synced projected
  assets); whether projected files are in the rule's scope is unverified.

## Diagnostic Details

- **Reproduction**: from the base checkout, `devkit integration prepare dev-bug-polish --task-kind session
  --task-id dev-bug-polish --route local --claims '{"task_kind": "overall-refactor", ...}'`.
- **Expected / Actual**: Expected readiness to pass as the branch's own `just rules-check` did; actual
  `INTEGRATION_NOT_READY` with three `RULE-cli-contract` violations for `--given`.
- **Versions**: base `main` at `7b2a425c`; branch head `1bfecd3b`.
- **Conditions**: dogfood repository, where the running devkit is the base checkout's editable install.
- **Workarounds Attempted**: none through the CLI; `devkit integration integrate` has no override.
- **Related Assets**: `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/rule.py`
  (`_running_root`), `CAP-DLV-cli-and-output`.

## Evidence

```text
[ERROR]  (INTEGRATION_NOT_READY) the configured provider refused integration
[DETAIL] CI rule violation RULE-cli-contract at docs/capabilities/delivery/CAP-DLV-cli-and-output.md:23:
         Unknown option --given of 'devkit workflow handoff' in `devkit workflow handoff ... [--given NAME]...`
(two more for answer and return)
Branch worktree: just rules-check -> [OK: no error-severity violation remains]
```

## Disposition

- **Disposition**: `SPEC-readiness-cli-runtime`: promoted by the user's decision for Planning of the recorded behavior and its contract constraints.
