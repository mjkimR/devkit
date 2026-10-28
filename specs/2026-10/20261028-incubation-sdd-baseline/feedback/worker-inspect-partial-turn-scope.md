---
id: FB-worker-inspect-partial-turn-scope
title: Worker inspection cannot derive scope before reconcile exists
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/worker/usecases/inputs.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-28
---

# [FB-worker-inspect-partial-turn-scope] Worker inspection cannot derive scope before reconcile exists

## 1. Friction / Question

- **Context**: The first independent baseline Development turn ended cleanly at build-verify with Task 1 complete and Task 2 pending prerequisite integration.
- **Expectation**: Worker inspection derives the committed unit and task boundaries even before the later reconcile artifact is written.
- **Actual**: Scope inspection was not-run because derive_scope unconditionally read the absent reconcile.md through git show. Other ancestry/head/worktree/envelope/rules/workflow checks passed.
- **Workaround**: Repeat inspection with the complete explicit allowed --scope list; scope then passed with no outside path.
- **Suggestion**: Derive available unit/task boundaries before reconcile exists, while retaining stage checks that require it later. Distinguish an absent not-yet-drafted artifact from a malformed existing record; add a partial-turn regression rather than hiding a failed check.

## Diagnostic Details

- **Reproduction**: At the first worker head3e63b730, run devkit spec worker inspect with its accepted base7264bb43 and no scope override.
- **Expected / Actual**: Expected scope from unit/tasks; actual scope status not-run with GIT_FAILED for an absent reconcile.md. This was not evidence of a scope pass.
- **Versions**: devkit-spec0.1.4, initial baseline worker turn.
- **Conditions**: A spec-feature unit intentionally paused at build-verify before independent review and Living Spec draft; the repository permits a completed scoped turn with remaining work.
- **Workarounds Attempted**: Explicit full scope override passed; no inspector implementation was changed.
- **Related Assets**: features/worker/usecases/inputs.py derive_scope; spec-delegate worker validation; worker records for completed partial turns.

## Evidence

```text
scope.status = not-run
cause.code = GIT_FAILED
git show: path '<unit>/reconcile.md' does not exist in commit3e63b730
changed_paths included only the assigned unit, new playbook/manifest/test and declared receipt sync output
Explicit --scope unit --scope playbook --scope manifest --scope test --scope receipt:
  scope.status = pass; outside_scope = []
```

The target's derive_scope reads reconcile.md unconditionally after parsing tasks.md. This observation concerns early scoped-turn inspection, not final reconciliation requirements.


## Disposition

Resolved by `SPEC-worker-inspection-fixes`. Optional absent reconciliation now preserves unit/task scope while malformed present and missing required records remain not-run. Cumulative rules use an independent rules_base while accepted-turn ancestry and changed paths retain base. Verification: 48 worker inspector regression tests, including actual RULE-reconcile-contract evaluation for an earlier-turn-created target, overrides, invalid references and compact/full/text evidence; affected tests and package lint/types pass.
