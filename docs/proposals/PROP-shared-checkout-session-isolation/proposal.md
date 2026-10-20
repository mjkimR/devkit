---
id: PROP-shared-checkout-session-isolation
title: Non-blocking guidance for session branches in a shared checkout
summary: "Adds concise guidance for --no-worktree branches in shared checkouts, leaving coordination to the direct user or local orchestration main agent without requiring worktrees or adding execution barriers."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/git-policy.md
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/branches.md
    - docs/capabilities/delivery/CAP-DLV-project-policy.md
    - docs/capabilities/worktree/CAP-WT-task-worktrees.md
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-checkout-session-isolation] Non-blocking guidance for session branches in a shared checkout

## 1. Background & Hypothesis

- **Problem**: A `session` task may run on a branch started with `devkit worktree start <branch> --no-worktree` in the
  base checkout. When several agent sessions share that checkout, another session's commit can land on the task
  branch while it is checked out. One such branch held a foreign proposal commit, local integration refused it, and
  the work had to be cherry-picked onto a fresh worktree branch (`FB-no-worktree-session-branch-shared-checkout`).
- **Responsibility**: In direct mode the user coordinates sessions sharing a checkout. In local orchestration the
  main agent coordinates worker checkout and branch use. Uncoordinated concurrent writes to one checkout are outside
  this proposal's supported isolation guarantees.
- **Hypothesis**: Brief agent-facing guidance clarifies shared branch state and coordination responsibility without
  changing command behavior. An unconditional runtime notice does not identify actual concurrent work and adds no
  useful signal.

## 2. Planning Scope

The scope is documentation only: add the minimum guidance in the `spec` references and clarify the corresponding
capability contracts. No command implementation, runtime notice, session detection or coordination infrastructure
is needed.

## 3. Proposed Design & Impact

- Keep `--no-worktree` available under its existing policy. Do not require or automatically create a worktree for
  session tasks, change `GIT_POLICY` levels, add confirmation steps, introduce new refusals or acquire a session
  ownership lock.
- Add brief guidance to the `spec` skill's git-policy and branches references: `--no-worktree` switches the current
  checkout to the task branch, and other sessions using that directory observe the same branch. Direct users and
  local orchestration main agents coordinate checkout use; a separate worktree remains an available option.
- Reflect that responsibility boundary in `CAP-DLV-project-policy` and `CAP-WT-task-worktrees` (§2a). Keep command
  output and success behavior unchanged; do not add an unconditional runtime notice.
- Keep existing integration checks. Do not add foreign-commit detection, automatic commit separation or a new
  integration refusal for shared-checkout use.

**Non-Goals**: guaranteed isolation between concurrent sessions in one checkout, shared-session detection,
runtime notices, mandatory worktrees, session locks, additional approval gates and automatic recovery of mixed branches.

## 4. Development Acceptance & Verification

- In `git-policy.md`, place the shared-checkout caveat beside the session branch guidance; in `branches.md`,
  place it in §2 beside `start --no-worktree`. State that switching branches changes the branch seen by every
  session using that directory, so another session can commit to the checked-out task branch.
- In `CAP-DLV-project-policy` §3.6 and `CAP-WT-task-worktrees` §2a, clarify the same responsibility boundary:
  the direct user coordinates shared sessions; the local orchestration main agent coordinates workers. Preserve
  the existing rule that local-orchestrated workers run in worktrees. This clarification grants no new permission
  to run workers in a shared checkout. A separate worktree remains an option for a direct session task.
- Review all four documents together for those statements and for unchanged policy levels, command output,
  integration checks and approval requirements. No runtime behavior or new policy is introduced, so no PADR or
  production-code change is needed. Development effort remains `low`.
- Verify the documentation with `uv run --no-sync devkit rules check` on the four changed paths and the normal
  staged/cumulative rule checks. Run `just test-affected` for the final diff and follow any selected checks;
  no new test is needed for this wording-only clarification.

## 5. Source Feedback

`FB-no-worktree-session-branch-shared-checkout` stays `promoted` during Planning. Its existing disposition already
selects this documentation-only scope. After implementation, the Host reviews the four-file diff and verification
before deciding source resolution; Planning alone is not fix verification. The source feedback file is outside
this worker's proposal-only write scope.

## 6. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr shared-checkout-session-isolation "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff shared-checkout-session-isolation`.
- On rejection: `status: rejected` with the user's reason in the commit message.
