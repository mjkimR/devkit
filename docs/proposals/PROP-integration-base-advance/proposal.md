---
id: PROP-integration-base-advance
title: Integration that tolerates base advances
summary: 'Lets local integration proceed when the base advanced after approval: merge instead of fast-forward only, bind approval to the source and the effective policy rather than the exact base commit and raw receipt bytes, and stop only on conflicts, policy changes or failed readiness.'
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: capabilities/integration/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/integration/
    - capabilities/worktree/
    - packages/devkit/src/devkit/integration/
    - packages/devkit/src/devkit/worktree/
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-spec/tests/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-base-advance] Integration that tolerates base advances

- **Origin**: `FB-integration-stale-on-base-advance`. An accepted `integration_integrate` confirmation for
  `plan-high-effort-review-loop` was refused with `INTEGRATION_REQUEST_STALE` because another activity's commit
  landed on `main` during the confirmation; the branch had to integrate `main` again and ask for a second
  confirmation.
- **Decided in Backlog**: fast-forward only was a default, not a requirement; integration may merge. The policy
  check compares the effective policy, not raw file bytes.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`.

## 1. Background & Hypothesis

### 1.1 Problem

- **Raw receipt digest.** The request binds a digest of the base's `.devkit/config.toml` and
  `.devkit/installation.json` (`integration/service.py` `_validate`). The receipt lists bundle asset hashes, so any
  activity that edits a bundled skill invalidates every open confirmation, though no policy changed.
- **Fast-forward only.** The request fixes `merge_method: ff-only` (`integration/models.py`), and the classic
  `devkit worktree finish --merge` runs `git merge --ff-only` (`worktree/lifecycle.py`). Any base advance makes the
  merge impossible (`WORKTREE_MERGE_NOT_FF`) until the branch integrates the base again.
- **Repeated confirmations.** With several activities landing on one base, each retry can be overtaken again; every
  retry is a new native confirmation for the same change.

### 1.2 Hypothesis

Binding the confirmation to the source commit, the target branch and the effective policy, and merging the advanced
base instead of requiring a fast-forward, keeps one confirmation per integration while still refusing what the user
did not see: conflicts, a changed policy, and readiness that no longer holds.

## 2. Technical Spike Questions

- **Q1. Merge method.** Fast-forward when possible, else a merge commit (`git merge --ff`), or always a merge commit
  (`--no-ff`), or a policy key (`[worktree] merge = "ff" | "no-ff" | "ff-only"`) with a default.
- **Q2. Where the merge runs.** In the base checkout (a conflict leaves the user's base checkout mid-merge and needs
  `git merge --abort`), or first merging the base into the source worktree and then fast-forwarding the base (the
  base checkout never sees a conflict; the source gains a merge commit).
- **Q3. Effective policy.** The fields the digest covers: `[workflow.approvals]`, `[worktree]` (`pull_request`,
  `delete_branch`, merge policy), `[integration] provider`, and the identities of the readiness provider, finish
  guards and post-finish extensions; not asset hashes. Whether a base change to a managed asset the source also
  changed is a conflict to refuse.
- **Q4. Readiness after the base advanced.** Provider evidence binds exact source and target SHAs. Whether the
  executor re-runs `check` against the new target and proceeds when it passes, and what the SDD provider (devkit-spec)
  must change so its evidence stays valid for a later target.
- **Q5. Confirmation text.** How the form states that later base commits are merged in without another confirmation,
  and which target SHA it shows (the one at confirmation time).
- **Q6. Bounds.** Whether the executor retries when the base advances again during its own run (under the existing
  Git common-directory lock, other devkit executors are already serialized), and how many times.

## 3. Proposed Design & Impact

- **Approval scope**: repository, task, source branch and SHA, target branch, worktree and branch cleanup, cleanup
  extensions, effective-policy digest (Q3). The target SHA at confirmation is shown and recorded, not required to hold.
- **Execution**: if the target advanced, merge it per Q1/Q2; stop with no change to the base on a conflict, a changed
  effective policy, or a readiness re-check that fails (Q4). Otherwise integrate and run the approved cleanup.
- **CLI parity**: `devkit worktree finish --merge` follows the same merge method.
- **Scope Excluded**: PR operations, fetch, push and remote deletion (unchanged); squash and rebase integration;
  changing who may approve.
- **Impact**: `packages/devkit/src/devkit/integration/` (request model, validation, executor),
  `packages/devkit/src/devkit/worktree/lifecycle.py`, the devkit-spec readiness provider, `spec-integrate` and the
  worktree reference, `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `docs/development/reference/integration.md`
  and `worktree.md`.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions are recorded as PADRs in `decisions/`; research goes in `materials/`.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff integration-base-advance`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
