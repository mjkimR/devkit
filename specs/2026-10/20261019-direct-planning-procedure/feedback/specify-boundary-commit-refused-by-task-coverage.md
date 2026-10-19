---
id: FB-specify-boundary-commit-refused-by-task-coverage
title: Commit gate refuses the specify stage boundary until tasks cover every AC
scope: repo
kind: friction
category: instruction-conflict
target: development-worker
skill: spec-specify
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-19
---

# [FB-specify-boundary-commit-refused-by-task-coverage] Commit gate refuses the specify stage boundary until tasks cover every AC

## 1. Friction / Question (friction, question)

- **Context**: a `development-worker` turn of `SPEC-direct-planning-procedure` on a handed-off bundle, committing
  after `specify` as the contract asks ("Commit at every stage boundary").
- **Expectation**: the `spec-specify` Definition of Done says `devkit rules check <dir>` may report "coverage the
  tasks have not been written for yet", so a `spec.md`-only commit at the `specify` boundary should pass.
- **Actual**: the pre-commit gate refused the commit with `GATE_RULES_FAILED` (`RULE-task-coverage`, error) because
  the skeleton `tasks.md` covered only AC-01.
- **Workaround (or Interpretation Chosen)**: wrote `plan.md` and `tasks.md` first and committed `specify`, `plan` and
  `tasks` together.
- **Suggestion**: either let `RULE-task-coverage` skip a `tasks.md` that still carries the skeleton marker, or say in
  `spec-specify` and the worker contract that the first commit after `specify` comes at `tasks`.

## Evidence

```text
[ERROR]  (GATE_RULES_FAILED) 1 rule violation(s) in the staged tree
[DETAIL] RULE-task-coverage specs/2026-10/20261019-direct-planning-procedure/tasks.md:1: acceptance criteria without a task: AC-02, AC-03, AC-04, AC-05
```

## Diagnostic Details

- **Reproduction**: on a handed-off bundle, rewrite `spec.md` with more than one AC, leave the `tasks.md` skeleton,
  `git add spec.md && git commit`.
- **Conditions**: `local-orchestrated` Development, `activity-effort: medium`, base `d981971`.
- **Related Assets**: `.devkit/managed/spec/rules/task_coverage/`, `spec-specify` §5, the `development-worker`
  contract step 8.

- **Disposition**: Dismissed as a skill-versus-stage boundary misunderstanding. The existing sdd-spec-feature
  specify stage lists spec-specify, spec-plan and spec-tasks together, requires all three nonskeleton documents and
  lint-clean, and declares all three as its artifacts. A spec.md-only commit is not that stage boundary. Verified
  with `devkit workflow show sdd-spec-feature`; task coverage continues to guard the real boundary. No rule relaxation
  or implementation change is needed.
