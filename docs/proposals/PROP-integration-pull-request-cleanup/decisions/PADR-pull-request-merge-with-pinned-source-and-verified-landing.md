---
id: PADR-pull-request-merge-with-pinned-source-and-verified-landing
title: Pull request merge with pinned source and verified landing
summary: The pull request route merges with the PR head pinned to the approved source after checking a locally built merge on the fetched target, then verifies the platform merge commit's parents and tree; a merge onto an unchecked target is never reported as a checked success.
proposal: PROP-integration-pull-request-cleanup
status: draft
created_at: 2026-10-20
---

# [PADR-pull-request-merge-with-pinned-source-and-verified-landing] Pull request merge with pinned source and verified landing

- **Status**: Draft
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

`PROP-integration-follow-ups` lets a local approval absorb target advances when the merge is clean, the effective
policy is unchanged and readiness passes on the result commit, which it builds itself and fast-forwards onto with a
compare-and-swap. A pull request merge is performed by the platform: `gh pr merge --match-head-commit` (REST `sha`)
pins the PR head, but nothing pins the base, and the platform builds its own merge commit onto whatever the target is
at that moment.

## 2. Decision Drivers

- The approved source SHA is what lands; a changed source needs a new approval.
- Required CI, review and branch protection stay conditions of the merge (the PR is the gate, not bypassed).
- What lands is checked; what could not be checked is reported as such, never as success.
- No destructive cleanup on an unknown outcome.

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
and `M`'s tree equals the checked tree, the landing is checked. Three other cases get distinct codes and are never
reported as checked: `M^1` descends from the checked target (an advance in the window between the last check and the
merge, which devkit cannot close), `M^1` does not descend from the confirmation target (a rewritten target), and an
equal first parent with a different tree (the platform merged differently). The result policy digest is evaluated on
`M`. What follows each case (post-hoc checks, cleanup or a stop) follows the user's decision in this Planning. A merge call whose outcome is unknown is resolved only from the PR state; while it stays unknown no
cleanup runs. B is not required; C is rejected for this route (it removes the PR gate the route exists for).

## 5. Consequences

- A residual race remains and is disclosed in the form and the result.
- The merge commit is GitHub's: its committer, signature and message handling are the platform's; no local commit
  hooks or trailers apply.
- Cleanup verifies PR state `MERGED`, the source contained in the fetched target and the recorded merge commit
  contained in it; later target commits do not block cleanup.
