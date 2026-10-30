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
| Commit on the base branch | Host comparison; integration refuses with `WORKTREE_MERGE_NOT_FF` until the Host merges the base | The integrating command merges a conflict-free advance itself; nothing audits it |

A committed escape is the case that would stay hidden; a dirty escape always surfaces at integration.

## Options

| Option | Detects a committed escape | Foreign-session advance (2026-10-30) | Host ceremony | Contract and code cost |
| --- | --- | --- | --- | --- |
| A: drop the HEAD equality and the pre-spawn record; audit only `<accepted>..<returned>`, the worktree and the base's dirty paths | No; after the sibling it lands unaudited | Passes | None | Documents and two tests; no code |
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

## Derivable window for C

The pre-spawn HEAD is not recorded durably; a design that needs it adds a record. C derives its window instead
(revised after `challenger-01`):

- The non-merge commits reachable from the base checkout's HEAD and not from the returned head
  (`git rev-list --no-merges <base HEAD> --not <returned>`), so no merge base is needed.
- Only commits whose committer time is at or after the audit base `<accepted>`'s committer time. Every worker commit,
  including an escape, is made after `<accepted>`, so the filter keeps every escape and drops advances the Host saw
  before spawning; otherwise earlier unmerged advances would repeat in every later turn.
- Each commit contributes its own changed paths. A first-parent walk would credit an escape to the Host's merge
  commit when another unit is fast-forwarded under `merge = "ff-only"` (`CAP-WT-task-worktrees`), so merges are
  skipped and the escape is named by itself.
- The write scope is the derived or overridden scope of the same inspection. When the scope check is `not-run` or the
  window's Git query fails, no overlap is computed and `SPEC_WORKER_CHECK_NOT_RUN` names the cause.
- Accounting is deterministic: the Host's own commit, a commit contained in a source the Host integrated, or a dirty
  path the Host wrote. Git cannot tell another session's commit from a worker escape, so the user confirms those.

## Change inventory

- `spec-delegate/references/worker.md` (Validate) and `payload.md` (Workers): replace the equality and the pre-spawn
  record with the accounting rule.
- `features/worker/usecases/inspect.py`, `inputs.py`, `cli/commands.py`, the worker warning class beside
  `WorkerCheckNotRunNotice`.
- `CAP-DLV-delivery-workflows`: the acceptance requirement "unchanged base" and the Worker result inspection section,
  its JSON fields and code table.
- A new ADR superseding the base-checkout clauses of `ADR-orchestration-workers` (committed results and their
  validation; informational range inspection), with a pointer line in that ADR.
- Tests: `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` (worker.md tokens) and
  `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`.
- Completed specs and earlier materials that restate the rule stay unedited as history.
