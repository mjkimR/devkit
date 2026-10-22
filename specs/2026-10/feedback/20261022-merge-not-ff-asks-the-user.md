---
id: FB-merge-not-ff-asks-the-user
title: WORKTREE_MERGE_NOT_FF asks the user to approve the routine base merge
scope: repo
kind: friction
category: tool-error
target: WORKTREE_MERGE_NOT_FF advisory (integration_integrate, spec_plan_accept)
origin: user
severity: workaround
recurring: true
status: open
created_at: 2026-10-22
---

# [FB-merge-not-ff-asks-the-user] WORKTREE_MERGE_NOT_FF asks the user to approve the routine base merge

## 1. Friction / Question (friction, question)

- **Context**: Integrating Development units under shared base `dev-integration=auto`, and requesting
  `spec_plan_accept` for Planning branches, while other units kept landing on the base.
- **Expectation**: Merging the moved base into the task branch is the documented first step of `spec-integrate`
  ("Merge the base, never rebase ... repeat after an integration refused on a later target"), so a branch behind its
  target is a routine Host step, not a user decision.
- **Actual**: Both tools refuse with `WORKTREE_MERGE_NOT_FF` whose advisory is mode `INTERACTION`, actor `USER`:
  "Stop and ask the user. Do not retry". The Host stopped and asked twice in one session; the merge itself needed no
  decision.
- **Workaround (or Interpretation Chosen)**: The Host merged the base into the task branch, re-verified and retried,
  treating the existing integration policy as the authority.
- **Suggestion**: Give the code an actor and mode that route the Host to `spec-integrate` Step 1 (merge the base,
  re-verify, retry) when the task branch only lags its target, and keep `INTERACTION` for cases that need a decision
  (diverged history the Host did not create, a conflict that needs a design choice).

## Evidence

```text
integration_integrate: WORKTREE_MERGE_NOT_FF mode=INTERACTION actor=USER
  "dev-contract-alignment neither contains the target main at d12a6ea3 nor is contained in it"
spec_plan_accept: WORKTREE_MERGE_NOT_FF mode=INTERACTION actor=USER (plan-document-index-cache, target 397286e1)
Both resolved by `git merge main` in the task worktree, re-verification and one retry.
```
