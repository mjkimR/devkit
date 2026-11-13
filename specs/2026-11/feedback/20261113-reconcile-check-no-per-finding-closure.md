---
id: FB-reconcile-check-no-per-finding-closure
title: A reconcile-check round has no per-finding resolve or waive like reverify
scope: repo
kind: friction
category: missing-capability
target: the spec skill's references/review-loop.md (reconcile-check closure)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-reconcile-check-no-per-finding-closure] A reconcile-check round has no per-finding resolve or waive like reverify

## 1. Friction / Question (friction, question)

- **Context**: A consumer Unit's `reconcile-check-01` raised findings; the Host fixed some and deferred one to a
  feedback record.
- **Expectation**: Close each finding explicitly, as `devkit workflow envelope reverify --resolve <n>` and
  `--waive <n>=<reason>` do for a code review round.
- **Actual**: The review loop closes a reconcile round only with a new full `reconcile-check` envelope; there is no
  `--resolve` or `--waive` for its findings. The deferred finding had to be explained in the new round's summary.
- **Workaround (or Interpretation Chosen)**: `reconcile-check-02` restated the outcome of each round-1 finding in
  prose and named the follow-up feedback.
- **Suggestion**: Let `reverify --from envelopes/reconcile-check-NN.yaml` (or a reconcile-specific closure) carry
  per-finding `resolved` and `waived` outcomes, matching the code-review path.

## Diagnostic Details

- **Reproduction**: Record a `reconcile-check` with findings, then try to close one finding as waived.
- **Expected / Actual**: Expected a per-finding outcome; actual whole-round re-check only.
- **Versions**: consumer-installed devkit, revision unknown; guidance checked at devkit `569379a06`.
- **Conditions**: `living-spec-draft` stage, two reconcile rounds.
- **Workarounds Attempted**: prose outcomes in the closing round; accepted by the stage exit.
- **Related Assets**: `references/review-loop.md` (Fixing row), `devkit workflow envelope reverify --help`
  (`--resolve`, `--waive`, `--from`), the `spec-sync` skill.

## Evidence

```text
review-loop.md Fixing: "close the round: `reverify` for code, a new `reconcile-check` for reconcile,
`reverify --from envelopes/challenger-NN.yaml` for Planning."
```
