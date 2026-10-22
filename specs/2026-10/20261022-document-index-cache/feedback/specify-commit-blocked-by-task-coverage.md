---
id: FB-specify-commit-blocked-by-task-coverage
title: spec-specify suggests a spec-only step the commit gate refuses
scope: repo
kind: friction
category: instruction-conflict
target: the spec-specify skill
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-specify-commit-blocked-by-task-coverage] spec-specify suggests a spec-only step the commit gate refuses

## 1. Friction / Question (friction, question)

- **Context**: A development worker rewriting a handed-off `spec.md`, committing at every stage boundary.
- **Expectation**: The spec-specify completion says `devkit rules check <dir>` may report task coverage not yet
  written and "next is spec-plan", which reads like a point where `spec.md` alone can be committed.
- **Actual**: The pre-commit rules gate refuses the commit with `GATE_RULES_FAILED` because `RULE-task-coverage`
  is an error while `tasks.md` is a skeleton. The `specify` stage of `sdd-spec-feature` only ends once `plan.md` and
  `tasks.md` are written too, so spec, plan and tasks go into one commit.
- **Workaround (or Interpretation Chosen)**: Wrote `plan.md` and `tasks.md`, then committed the three together.
- **Suggestion**: State in the spec-specify completion that `spec.md`, `plan.md` and `tasks.md` of the `specify`
  stage are committed together, because the commit gate refuses uncovered acceptance criteria.

## Diagnostic Details

- **Reproduction**: Rewrite `spec.md` of a handed-off Unit with new `[AC-NN]` IDs, leave `tasks.md` a skeleton,
  `git commit`.
- **Expected / Actual**: Expected a spec-only commit to be possible; observed the gate refusal.
- **Versions**: worktree `dev-document-index-cache`.
- **Conditions**: Commit gate installed (`rules-check` at `pre-commit`).
- **Workarounds Attempted**: One commit with spec, plan and tasks; accepted.
- **Related Assets**: the spec-specify, spec-plan and spec-tasks skills, `RULE-task-coverage`.

## Evidence

```text
[ERROR]  (GATE_RULES_FAILED) 1 rule violation(s) in the staged tree
[DETAIL] RULE-task-coverage .../tasks.md:1: acceptance criteria without a task: AC-02, ..., AC-11
```

- **Disposition (resolved)**: Clarified in `spec-specify` completion instructions (`SKILL.md`) that the `specify` stage boundary is reached and committed only after `spec.md`, `plan.md` and `tasks.md` are all written, avoiding early commit refusal by `RULE-task-coverage`.
