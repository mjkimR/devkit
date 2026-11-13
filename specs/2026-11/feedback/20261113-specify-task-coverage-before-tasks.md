---
id: FB-specify-task-coverage-before-tasks
title: Specify ends with an expected task-coverage violation, which made commit points unclear
scope: repo
kind: friction
category: spec-ambiguity
target: the spec-specify skill (Completion)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-specify-task-coverage-before-tasks] Specify ends with an expected task-coverage violation, which made commit points unclear

## 1. Friction / Question (friction, question)

- **Context**: A consumer spec author wrote `spec.md` with Screens drafts, then ran an optional UX review before
  `plan.md`.
- **Expectation**: A clear point at which the spec (and the UX review envelope about it) is committed.
- **Actual**: `spec-specify` Completion says `devkit rules check` reports only "task coverage not yet written" and
  "Do not commit yet: the `specify` stage boundary is committed only once `plan.md` and `tasks.md` satisfy
  `RULE-task-coverage`". The UX review envelope was committed on its own while `spec.md` stayed uncommitted, and the
  skeleton `tasks.md` placeholder made the coverage report list acceptance criteria that no task could yet cover.
  The author reported the commit points as unclear.
- **Workaround (or Interpretation Chosen)**: Committed the ux-review envelope alone, then committed spec, plan and
  tasks together once coverage passed.
- **Suggestion**: State the commit sequence for a `specify` that includes a UX review (envelope before or with the
  spec), and have the coverage report say that a skeleton `tasks.md` is expected to fail until `spec-tasks`.

## Diagnostic Details

- **Reproduction**: `devkit spec new <slug>`, write `spec.md` with Screens, run `devkit rules check <dir>`.
- **Expected / Actual**: Expected a clear commit point; actual a deferred commit across three skills.
- **Versions**: consumer-installed devkit, revision unknown; skill text checked at devkit `569379a06`.
- **Conditions**: `sdd-spec-feature` Unit with an optional UX review at `specify`.
- **Workarounds Attempted**: as above.
- **Related Assets**: `spec-specify` skill Completion, `spec-ux-review` Report ("when the reviewed `spec.md` is
  uncommitted, state that in an assumption"), `RULE-task-coverage`.

## Evidence

```text
spec-specify Completion: "Do not commit yet: the `specify` stage boundary is committed only once `plan.md` and
`tasks.md` satisfy `RULE-task-coverage`."
consumer history: ux-review-01 envelope committed alone before the plan commit.
```
