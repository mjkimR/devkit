---
id: PADR-pull-request-merge-with-pinned-source-and-verified-landing
title: Pull request merge with pinned source and verified landing
summary: The pull request route merges with the PR head pinned to the approved source once required checks pass, after checking a locally built merge on the fetched target. An unchecked landing is a notice, never a checked success; cleanup stops only when the target lacks the source.
proposal: PROP-integration-pull-request-cleanup
status: draft
created_at: 2026-10-20
---

# [PADR-pull-request-merge-with-pinned-source-and-verified-landing] Pull request merge with pinned source and verified landing

- **Status**: Draft
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

`SPEC-integration-follow-ups` lets a local approval absorb target advances when the merge is clean, the effective
policy is unchanged and readiness passes on the result commit, which it builds itself and fast-forwards onto with a
compare-and-swap. A pull request merge is performed by the platform: `gh pr merge --match-head-commit` (REST `sha`)
pins the PR head, but nothing pins the base, and the platform builds its own merge commit onto whatever the target is
at that moment.

## 2. Decision Drivers

- The approved source SHA is what lands; a changed source needs a new approval.
- Required CI, review and branch protection stay conditions of the merge (the PR is the gate, not bypassed).
- What lands is checked; what could not be checked is reported as such, never as success.
- No destructive cleanup on an unknown outcome, and none that could lose source commits.
- The approving call never waits for CI or review.

## 3. Considered Options

- **A**: fetch the target, build the prospective merge locally (the follow-ups build), run the policy digest and
  readiness on it, recheck the remote target immediately before the call, merge with the head pinned, then verify the
  landed merge commit (second parent the source, first parent the checked target, tree equal to the checked tree).
- **B**: require the platform's "branch must be up to date" rule, so any target advance refuses the merge; every
  advance then changes the source and needs a new approval.
- **C**: push the locally built merge commit to the remote target with a lease; GitHub marks the PR merged. Exact
  compare-and-swap, but it bypasses the PR merge and its protections (or silently uses an admin bypass).

## 4. Decision Outcome

Option A. `prepare` fetches the target's remote ref; the fetched remote SHA is the confirmation target, the
source must contain it and the target policy is read from it. The approval binds the source SHA (enforced
server-side by the head pin) and that confirmation target; before the merge call the fetched target must descend from the confirmation target, the prospective merge must be
clean, the effective policy unchanged and readiness must pass on it. After the call, devkit fetches and reads the PR's
merge commit `M`: `M^2` equals the source and `M` is contained in the fetched target. When `M^1` is the checked target
and `M`'s tree equals the checked tree, the landing is checked; any other landing is never reported as checked (see
the decisions below). B is not required; C is rejected for this
route (it removes the PR gate the route exists for).

Decided by the user in this Planning (`envelopes/answer-01.yaml`):

- **Checks and review** (q-checks-wait a): the merge call is made only when the PR is mergeable with required checks
  and reviews satisfied, which happens in the approving call when the agent already pushed a ready PR whose checks
  passed. Otherwise the approving call publishes and returns `INTEGRATION_CHECKS_PENDING`, and `integration_resume`
  merges later only while the remote target still equals the last build target (else a new confirmation).
- **Unchecked landing** (q-unchecked-landing, outside the offered options): once the merge is confirmed (PR `MERGED`,
  `M^2` the source) and the source is an ancestor of the fetched target, cleanup runs whether or not the landing was
  checked. Every landing other than the checked one (an advance in the window, a tree mismatch, a first parent outside
  the confirmation target's history, `M` not in the fetched target) is reported as the notice
  `INTEGRATION_LANDED_UNCHECKED` with its reason and a directive naming the landed-target check the readiness
  provider declares, runnable after cleanup.
  devkit does not re-run guards, readiness or the policy digest on `M`; cleanup uses the scope bound in the approved
  request. Cleanup stops only when the fetched target does not contain the source (`INTEGRATION_SOURCE_NOT_CONTAINED`).

A merge call whose outcome is unknown is resolved only from the PR state; while it stays unknown no cleanup runs.

## 5. Consequences

- A residual race remains and is disclosed in the form and the result; a commit landing in the window is merged
  without devkit's checks and only reported, since cleanup does not wait for it.
- On a repository with required checks or reviews the usual flow is two calls (approve, then `integration_resume`)
  unless the agent opened the PR and let its checks pass before `prepare`. A target commit landing while checks run
  costs a target merge into the source, re-verification, a new confirmation and a new check run; on a target that
  moves faster than its checks the route may never merge, which is disclosed.
- The merge commit is GitHub's: its committer, signature and message handling are the platform's; no local commit
  hooks or trailers apply.
- Cleanup verifies PR state `MERGED`, `M^2` the source and the source contained in the fetched target; later target
  commits and an unchecked landing do not block cleanup.
