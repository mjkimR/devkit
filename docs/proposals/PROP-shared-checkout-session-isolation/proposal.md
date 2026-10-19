---
id: PROP-shared-checkout-session-isolation
title: Isolation for session branches in a checkout shared by agent sessions
summary: Decides how session tasks avoid picking up other sessions' commits when they run on a --no-worktree branch in a base checkout shared by several agent sessions.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - delivery/
    - worktree/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-checkout-session-isolation] Isolation for session branches in a checkout shared by agent sessions

## 1. Background & Hypothesis

- **Problem**: A `session` task may run on a branch started with `devkit worktree start <branch> --no-worktree` in the
  base checkout. When several agent sessions share that checkout, another session's commit can land on the task
  branch while it is checked out. One such branch held a foreign proposal commit, local integration refused it, and
  the work had to be cherry-picked onto a fresh worktree branch (`FB-no-worktree-session-branch-shared-checkout`).
- **Hypothesis**: Either a policy that prefers a worktree whenever a session task is bound for local integration, or
  a coded notice from `--no-worktree` that the base checkout stays on the task branch, prevents the mix-up at low cost.

## 2. Technical Spike Questions

- **Q1**: Policy or signal: should `session` tasks bound for local integration require a worktree, or keep
  `--no-worktree` with a notice (and what code and directive)?
- **Q2**: Can devkit detect that a checkout is shared by other sessions (for example through the work-scope registry)
  so the policy or the notice applies only when it matters?
- **Q3**: How does integration report a branch that carries commits from outside the task, so the agent knows to
  separate them instead of retrying?

## 3. Proposed Design & Impact

- Affected: the `spec` skill's git-policy and branches references, `devkit worktree start --no-worktree`, and the
  delivery and worktree capabilities (`CAP-DLV-project-policy` and the worktree capability area).
- Planning compares the policy and signal options above; the decision may change `GIT_POLICY` levels.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr shared-checkout-session-isolation "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff shared-checkout-session-isolation`.
- On rejection: `status: rejected` with the user's reason in the commit message.
