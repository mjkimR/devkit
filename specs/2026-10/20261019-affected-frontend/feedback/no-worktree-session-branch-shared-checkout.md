---
id: FB-no-worktree-session-branch-shared-checkout
title: A --no-worktree session branch in the shared base checkout picked up another session's commit
scope: repo
kind: friction
category: other
target: devkit-spec bundle skills/spec/references/git-policy.md (session without a worktree) and devkit worktree start --no-worktree
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-no-worktree-session-branch-shared-checkout] A --no-worktree session branch in the shared base checkout picked up another session's commit

Concurrency between agent sessions that share one checkout.

## 1. Friction / Question (friction, question)

- **Context**: A `session` bugfix (the smoke script fix) ran on `dev-fix-smoke-response-style`, started with
  `devkit worktree start <branch> --no-worktree` in the base checkout, as git-policy.md allows for `session` depth.
- **Expectation**: The branch carries only this session's commits until integration.
- **Actual**: Another agent session working in the same checkout committed a proposal draft onto the checked-out
  branch between the review and this session's commit. `integration_integrate` then refused the branch
  (`INTEGRATION_NOT_READY`: a touched proposal unit is not accepted), and its first call also failed with
  `WORKTREE_BASE_ON_BRANCH` because the base checkout was on the task branch.
- **Workaround (or Interpretation Chosen)**: Started a fresh worktree branch from `main`, cherry-picked only this
  session's commit, integrated it, and left the mixed branch for the other session's owner.
- **Suggestion**: Prefer a worktree for session tasks bound for local integration (or whenever other sessions may
  share the checkout), and have `devkit worktree start --no-worktree` warn that the base checkout stays on the task
  branch until it is switched back.

## Diagnostic Details

- **Reproduction**: Two sessions in one checkout; one starts a `--no-worktree` branch and the other commits while it
  is checked out. Not reproduced deliberately.
- **Expected / Actual**: Expected an isolated branch; it held a foreign `docs(proposals)` commit before this
  session's own commit.
- **Versions**: devkit workspace `main` around c05b3c5.
- **Conditions**: `[GIT_POLICY: worktree=required pull_request=auto]`, `dev-integration = ask`, local MCP integration.
- **Workarounds Attempted**: Cherry-pick onto a worktree branch; integration then completed.
- **Related Assets**: git-policy.md, worktree.md, `integration_integrate`.

## Evidence

```text
git log main..dev-fix-smoke-response-style
  a218e2d fix(smoke): check the response-style skill layout the bundle deploys
  6e86dfe docs(proposals): add integration-base-advance draft      <- other session
integration_integrate (session): WORKTREE_BASE_ON_BRANCH, then INTEGRATION_NOT_READY
  "touched proposal unit docs/proposals/PROP-integration-base-advance is not accepted"
git-policy.md: "`session` depth is never required to [use a worktree]"
```
