---
id: PADR-merge-commit-outside-checkout
title: Merge commit built outside the base checkout
summary: Integration lands each task as a merge commit (no-ff by default, ff-only as the [worktree] merge alternative), built in the object store from the current target and the approved source and fast-forwarded onto the base, so the base checkout never sees a conflict.
proposal: PROP-integration-follow-ups
status: draft
created_at: 2026-10-19
---

# [PADR-merge-commit-outside-checkout] Merge commit built outside the base checkout

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Integration runs `git merge --ff-only` in the base checkout (`worktree/lifecycle.py` `finish`), and the request fixes
`merge_method: ff-only` (`integration/models.py`). Any commit landing on the target during a confirmation makes the
approved integration impossible (`WORKTREE_MERGE_NOT_FF`, `INTEGRATION_REQUEST_STALE`). A unit lands 10 to 13
commits, most of them records, which its envelopes cite by SHA.

## 2. Decision Drivers

- The base checkout, which the user works in, must never be left mid-merge.
- Every SHA the unit's records cite stays reachable and an ancestor of the base.
- The tree that lands is the tree that was checked.
- History shape does not depend on timing; a project can still require linear history.

## 3. Considered Options

- **Merge method**: `ff-only` (today); `ff` (merge commit only when needed); `no-ff` always; squash or rebase.
- **Where**: `git merge --no-ff` in the base checkout (a conflict leaves it mid-merge); merge the base into the source
  worktree, then fast-forward (the source gains a commit after approval and the base's first parent becomes the
  source side); build the merge in the object store with `git merge-tree --write-tree` and `git commit-tree`, check
  it, then fast-forward the base onto it.

## 4. Decision Outcome

`[worktree] merge = "no-ff" | "ff-only"`, default `"no-ff"` (user decision), for the integration service and
`devkit worktree finish --merge`. Under `no-ff` the result commit is built in the object store with the target as
first parent and the approved source tip as second, under a devkit-composed message, and the base only
fast-forwards to it. Without an advance the tree is the source tree (`commit-tree <source>^{tree}`); with one the
service builds it with `git merge-tree --write-tree` (Git 2.38 or later, probed only then, `WORKTREE_GIT_UNSUPPORTED`
below; a conflict is `WORKTREE_MERGE_CONFLICT` with nothing changed). A source already contained in the target builds nothing (a rerun is a no-op, and a fresh prepare yields a
cleanup-only request). The message uses
validated branch names only (`chore(merge): integrate <branch> into <target>`); the build lives in `devkit.worktree`,
honours identity and signing configuration, runs with a 30-second bound and no terminal prompt and refuses with
`WORKTREE_COMMIT_FAILED` and nothing changed on failure. `prepare` still requires the source to contain the target, except for a source the target already contains,
which yields a cleanup-only request (guards and readiness on `merge-base(target, source)`, the source as its result,
the target's policy as expected); only later advances are merged in. Conflict and not-fast-forward fixes are
package-neutral and SHA-preserving: merge the target into the branch, re-verify, prepare again. `ff-only` in either policy wins. Under `ff-only` the
result commit is the source tip and an advanced target is refused as today. The CLI `finish --merge`, which runs no
readiness provider, builds a merge commit only when the target did not advance and keeps `WORKTREE_MERGE_NOT_FF`
otherwise; it takes the integration lock in its command entry. `ff`, squash and rebase are not offered locally.

## 5. Consequences

- One `--first-parent` line per task; stage commits stay bisectable; ancestry checks keep working.
- `commit-tree` runs no commit hooks: the result's tree is checked by the readiness provider
  (`PADR-target-advance-readiness`), not by the commit gates.
- `validate_finish(merged=True)` and the service's merge recovery change from "HEAD equals the source" to "HEAD
  contains the latest result commit".
- One extra commit per integration even when the target did not move.
- Commit-msg hook trailers (DCO, Change-Id) are not added to the merge commit.
- The `WORKTREE_PUSH_REJECTED` fix stops recommending `git pull --rebase`: `git pull --rebase=merges` if a fixture
  shows it keeps the unit's SHAs, else `git fetch <remote> <ref>` then `git merge --no-ff -m "chore(merge): integrate
  <remote>/<ref> into <target>" FETCH_HEAD` (`git pull` has no message option), with its first-parent cost
  documented.
- Options also weighed: a scratch detached worktree running `git merge --no-ff` (hooks run, older Git works, could
  host tests) lost on checkout cost, a temporary worktree to clean up and the executor's no-commands rule.
