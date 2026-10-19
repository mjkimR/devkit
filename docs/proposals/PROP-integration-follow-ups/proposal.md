---
id: PROP-integration-follow-ups
title: "Integration follow-ups: base advances, auto dispatch, pull request cleanup and host confirmation adapters"
summary: "Plans four integration extensions: tolerating base advances during approval, policy-driven dispatch under dev-integration auto, pull request and squash or rebase cleanup, and confirmation adapters for hosts beyond Codex."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: high                        # critical | high | medium | low
size: XL                              # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - integration/
    - worktree/
    - delivery/
    - packages/devkit/src/devkit/integration/
    - packages/devkit/src/devkit/worktree/
    - packages/devkit-spec/src/devkit_spec/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-follow-ups] Integration follow-ups: base advances, auto dispatch, pull request cleanup and host confirmation adapters

- **Merged draft**: this draft also carries the former `integration-base-advance` draft (Backlog merge), whose
  questions are E1 to E6 below.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`.

## 1. Background & Hypothesis

### 1.1 Problem

`SPEC-hook-driven-integration-cleanup` shipped approval-bound local integration under `dev-integration = ask` and
deferred three extensions (its Non-Goal 3); daily use since then added a fourth problem. Each is recorded as feedback:

- **Base advances** (`FB-integration-stale-on-base-advance`): an accepted `integration_integrate` confirmation was
  refused with `INTEGRATION_REQUEST_STALE` because another activity's commit landed on `main` during the confirmation.
  - *Raw receipt digest*: the request binds a digest of the base's `.devkit/config.toml` and
    `.devkit/installation.json` (`integration/service.py` `_validate`). The receipt lists bundle asset hashes, so any
    activity that edits a bundled skill invalidates every open confirmation, though no policy changed.
  - *Fast-forward only*: the request fixes `merge_method: ff-only` (`integration/models.py`), and
    `devkit worktree finish --merge` runs `git merge --ff-only` (`worktree/lifecycle.py`). Any base advance makes the
    merge impossible (`WORKTREE_MERGE_NOT_FF`) until the branch integrates the base again.
  - *Repeated confirmations*: with several activities landing on one base, each retry can be overtaken again; every
    retry is a new native confirmation for the same change. Fast-forward only was a default, not a requirement, and
    the policy check should compare the effective policy, not raw file bytes.
- **Auto dispatch** (`FB-auto-integration-dispatch`): no integration runs without an interactive confirmation under
  `dev-integration = auto`.
- **Remote and pull request** (`FB-pr-remote-and-squash-integration`): no remote push or pull request merge, and
  `WORKTREE_UNMERGED` after a squash or rebase merge, because the merge test is commit ancestry.
- **Host adapters** (`FB-multi-host-integration-ergonomics`): native confirmation only through Codex MCP elicitation;
  other hosts get `INTEGRATION_CONFIRMATION_UNAVAILABLE` and the CLI fallback.

The deferral of the last three waited for ask-mode integration to be used in real workflows. Several sessions have
since completed local integrations through `integration_integrate` with `authority="mcp-elicitation"`.

### 1.2 Hypothesis

The four extensions share the integration service, its confirmation binding and the scoped cleanup, so one Planning
can settle their common contract (what an approval binds, how execution may adapt, which authority runs it) and
decide whether they are delivered together or split. Base advances affect every integration today, so they are the
first candidate.

## 2. Technical Spike Questions

- **Q1 (Split and order)**: One spec or several? Which extension comes first, and which depends on another?

Base advances:

- **E1 (Merge method)**: fast-forward when possible, else a merge commit (`git merge --ff`), always a merge commit
  (`--no-ff`), or a policy key (`[worktree] merge = "ff" | "no-ff" | "ff-only"`) with a default.
  **Backlog leaning (user, 2026-10-19)**: consider an always-merge-commit default (`--no-ff`) first. Every stage
  boundary commits, so a unit lands about 10 to 13 commits, most of them records only; a merge commit gives one line
  per unit under `git log --first-parent` while keeping the stage commits that review, reconcile-check, final-report
  and worker envelopes cite by SHA, and keeps `git bisect` inside a unit.
- **E2 (Where the merge runs)**: in the base checkout (a conflict leaves the user's base checkout mid-merge and needs
  `git merge --abort`), or first merging the base into the source worktree and then fast-forwarding the base (the
  base checkout never sees a conflict; the source gains a merge commit).
- **E3 (Effective policy)**: the fields the digest covers: `[workflow.approvals]`, `[worktree]` (`pull_request`,
  `delete_branch`, merge policy), `[integration] provider`, and the identities of the readiness provider, finish
  guards and post-finish extensions; not asset hashes. Whether a base change to a managed asset the source also
  changed is a conflict to refuse.
- **E4 (Readiness after the base advanced)**: provider evidence binds exact source and target SHAs. Whether the
  executor re-runs `check` against the new target and proceeds when it passes, and what devkit-spec's provider must
  change so its evidence stays valid for a later target.
- **E5 (Confirmation text)**: how the form states that later base commits are merged in without another
  confirmation, and which target SHA it shows (the one at confirmation time).
- **E6 (Bounds)**: whether the executor retries when the base advances again during its own run (under the existing
  Git common-directory lock, other devkit executors are already serialized), and how many times.

The deferred extensions:

- **Q2 (Auto dispatch)**: which readiness evidence must hold before an `authority="policy-auto"` integration runs
  without a prompt, and how is that authority recorded?
- **Q3 (Remote and pull request)**: how is remote push or pull request merge authority separated from local-only
  integration, and how is a squash or rebase merge verified (recorded pull request state, tree or patch equivalence)
  before the worktree and branch are removed? A squash with branch deletion leaves the envelope SHAs unreachable
  (see the E1 leaning), so a squash path either keeps the source under another ref or is not offered for units.
- **Q4 (Host adapters)**: which confirmation surfaces do Claude Code, Antigravity and other hosts offer that keep the
  binding to `request.id` and the approved scope and never let the agent approve itself?

## 3. Proposed Design & Impact

- **Base advances**: the approval binds repository, task, source branch and SHA, target branch, worktree and branch
  cleanup, cleanup extensions and an effective-policy digest (E3); the target SHA at confirmation is shown and
  recorded, not required to hold. If the target advanced, execution merges it per E1/E2 and stops with no change to
  the base on a conflict, a changed effective policy or a failed readiness re-check (E4). `devkit worktree finish
  --merge` follows the same merge method.
- Every extension keeps the existing invariants: fail closed, exact scope binding, no network operation without
  explicit authority, and no deletion of unmerged work.
- **Impact**: `packages/devkit/src/devkit/integration/` (request model, validation, executor),
  `packages/devkit/src/devkit/worktree/lifecycle.py`, `devkit.host` adapters, devkit-spec's readiness provider, the
  `spec-integrate` skill and the worktree reference, `CAP-INT-mcp-services`, `CAP-WT-task-worktrees` and the delivery
  capabilities, `docs/development/reference/integration.md` and `worktree.md`.
- **Coordination**: the devkit-dist package separation (in Development on `dev-devkit-dist-package-separation`) moves package boundaries in `packages/devkit`; Development
  of this proposal starts after it integrates, or rebases its paths onto the new layout.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-follow-ups "<title>"`.
- If Planning splits the work: decompose into child drafts with `--decomposed-from PROP-integration-follow-ups`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-follow-ups`.
- On rejection: `status: rejected` with the user's reason in the commit message.
