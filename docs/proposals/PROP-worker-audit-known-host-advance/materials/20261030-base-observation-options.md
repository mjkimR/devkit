---
id: MAT-base-observation-options
title: Worker base-checkout observation options
summary: "Compare dropping the base-checkout HEAD equality, a declared-Host-advance list and a derived scope-overlap warning for detecting worker writes that escape into the base checkout, with failure traces and the change inventory."
created_at: 2026-10-30
---

# [MAT-base-observation-options] Worker base-checkout observation options

## Evidence boundary

Read-only analysis of the `plan-worker-audit-known-host-advance` worktree at base `fdba6646`, by the Planning worker
and one `scout` (`envelopes/scout-01.yaml`). Nothing was executed against a live base checkout; the traces below are
derived from code reading. The 2026-10-30 foreign-session advance comes from the Host's report: another session
committed to `main` while a Development worker ran, and `devkit spec worker inspect --base <accepted>` passed.

## What the rule protects

- The rule "the base checkout's status and HEAD match what you recorded before spawning"
  (`spec-delegate/references/worker.md`, Validate) and the pre-spawn record (`payload.md`, Workers) came from a
  2026-10-15 review finding: a worker's relative-path write lands in the base checkout and the range audit misses it
  (`specs/2026-10/20261015-orchestration-mode/envelopes/review-01.yaml`). A worker's default cwd may be the base
  checkout (`ADR-codex-native-worker-execution`).
- The protected asset is detection of a worker write outside its worktree. The HEAD equality is one way to get it;
  it also stops on every foreign or Host advance, which caused the serialization in `MAT-git-operator-consumer-pilot`.
- The rule is prose only. `devkit spec worker inspect` reports `base_checkout.head` and `dirty_paths` as information
  and never fails on them (`features/worker/usecases/inspect.py`; `test_linked_worktree_observes_base_without_checking_it`).
  The commit gate has no branch check, so a worker can commit on the base branch.

## Detectors after `PROP-integration-merge-moved-target`

| Escape | Today | After the sibling lands |
| --- | --- | --- |
| Uncommitted file in the base checkout | Host comparison; integration refuses a dirty base (`WORKTREE_BASE_DIRTY`) | Unchanged: integration still refuses a dirty base |
| Commit on the base branch | Host comparison; integration refuses with `WORKTREE_MERGE_NOT_FF` until the Host merges the base; a full escape also fails inspection's head or ancestry | A full escape still fails head or ancestry; a partial escape is merged without audit |

A partial committed escape is the case that would stay hidden; a dirty escape always surfaces at integration.

## Options

| Option | Detects a committed escape | Foreign-session advance (2026-10-30) | Host ceremony | Contract and code cost |
| --- | --- | --- | --- | --- |
| A: drop the HEAD equality and the pre-spawn record; audit only `<accepted>..<returned>` and the worktree | A full escape fails head or ancestry; a partial escape lands unreviewed after the sibling (CI still runs) | Passes | None | Documents and two tests; no code |
| B: the Host declares its own advances; inspect requires the base to move from the recorded pre-spawn HEAD only through declared commits | Yes | Stops validation, because the commit is undeclared | A durable pre-spawn record plus a declaration per Host integration | New record or flags, walk, codes, documents, tests |
| C: derived scope-overlap warning; inspect lists base commits made after the audit base that touch the worker's write scope, and in-scope base dirty paths, as a `WARNING` | Yes, when the escape touches the write scope | Passes; a warning only when the commit touches this worker's scope (the user then confirms it) | None in the common case; accounting only for a warning | One window derivation, one warning code, a sentinel, documents, tests; no record |

## Failure traces

- **T1 dirty escape** (a relative-path write lands in the base working tree): A, B and C all surface it no later than
  integration (`WORKTREE_BASE_DIRTY`). C names it at validation when the path is in the write scope.
- **T2 committed escape** (the worker commits on the base branch): existing checks catch a full escape, because a
  worker whose final commit (the worker envelope) landed on the base leaves its branch without that envelope, so
  inspection's head or ancestry fails. A partial escape (some commits on the base, the rest on the branch) passes
  the range audit. Today the Host's equality or integration's `WORKTREE_MERGE_NOT_FF` catches it; after the sibling,
  A lets it land unreviewed (CI still runs on its content). B stops on it. C names it at validation when it touches
  the write scope; an escape commit that touches only paths outside the write scope stays unnamed. A worker stages
  only scope paths, so such a commit needs two mistakes (an out-of-scope `git add` and a commit in the wrong cwd).
  No committed escape has been observed in this repository.
- **T3 foreign advance** (another session commits to `main`): A and C accept it without ceremony unless it touches
  the worker's scope (C then names a real collision for the user to confirm). B stops validation.

## Review of C

C first used a first-parent window with a committer-time filter, then a non-merge window. The review rounds found:

- `challenger-01`: a first-parent walk credits an escape to the Host's merge commit under `merge = "ff-only"`
  (`CAP-WT-task-worktrees`); a notice cannot be counted by `--strict` (`ARCH-08-1-agent-output`), so the level must be
  `WARNING`; "another session's write" cannot be told from an escape in Git.
- `challenger-02`: committer times in this repository do not follow ancestry. The audit base `fdba6646` is dated
  18:05:25 +0900 while its descendants on this Planning branch are dated 17:37-17:43 (the commit gate rewrites
  commits), so a time-bounded window drops escapes. Accounting by "a source the Host integrated contains it" credits
  an escape that a base merge carried into another unit's branch.
- Without a time bound, a topology-only window lists every in-scope base commit not yet in the worker branch. Once
  the sibling makes base merges conditional, that includes other units' integrated commits on shared boundaries
  (for example `docs/capabilities/delivery/`) in every turn, each needing Host accounting or user confirmation.
- Narrowing the overlap to the unit directory removes the noise but names little for Development: the spec directory
  does not exist in the base checkout, so a Development escape lands on code paths.

Planning therefore recommends A and keeps C as the alternative for the user. A preventive follow-up, if an escape is
ever observed, is a commit-gate check refusing a base-checkout commit that touches a path an active task worktree's
unit owns (`CAP-COLL-work-scope-registry`).

## Change inventory (option A)

- `spec-delegate/references/worker.md` (Validate) and `payload.md` (Workers): drop the equality and the pre-spawn
  record.
- `CAP-DLV-delivery-workflows`: drop "unchanged base" from the acceptance requirements; word the base-checkout
  observation without a Host comparison.
- A new ADR naming the superseded base-checkout clauses of `ADR-orchestration-workers`, with a pointer line in that
  ADR.
- Tests: `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` (worker.md tokens).
- Completed specs and earlier materials that restate the rule stay unedited as history.
