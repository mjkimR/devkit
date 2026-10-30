---
id: MAT-base-observation-options
title: Worker base-checkout observation options
summary: "Compare dropping the base-checkout HEAD equality, a declared-Host-advance list and a derived scope-overlap notice for detecting worker writes that escape into the base checkout, with failure traces and the change inventory."
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
| C: derived scope-overlap notice; inspect lists base commits made after the audit base that touch the worker's write scope, and in-scope base dirty paths, as a `NOTICE` | Yes, when the escape touches the write scope | Passes; a notice only when the commit touches this worker's scope | None in the common case; accounting only for a notice | One window derivation, one notice code, documents, tests; no record |

## Failure traces

- **T1 dirty escape** (a relative-path write lands in the base working tree): A, B and C all surface it no later than
  integration (`WORKTREE_BASE_DIRTY`). C names it at validation when the path is in the write scope.
- **T2 committed escape** (the worker commits on the base branch): A accepts it, and after the sibling the advance is
  never audited. B stops on it. C names it at validation when it touches the write scope; an escape commit that
  touches only paths outside the write scope stays unnamed. A worker stages only scope paths, so such a commit needs
  two mistakes (an out-of-scope `git add` and a commit in the wrong cwd).
- **T3 foreign advance** (another session commits to `main`): A and C accept it without ceremony unless it touches
  the worker's scope (C then names a real collision). B stops validation.

## Derivable window for C

The pre-spawn HEAD is not recorded durably; a design that needs it adds a record. C derives its window instead:

- Commits on the first-parent chain of the base checkout's HEAD after its merge base with the returned head.
- Only commits whose committer time is later than the audit base `<accepted>`'s committer time. Every worker commit,
  including an escape, is made after `<accepted>`, so the filter excludes advances the Host saw before spawning and
  keeps every escape. Earlier advances the Host has not merged would otherwise repeat in every later turn.
- Each commit's paths are its first-parent changes; a merge commit contributes everything it brought in.
- The write scope is the derived or overridden scope of the same inspection; when the scope check is `not-run`, no
  overlap is computed and the existing `SPEC_WORKER_CHECK_NOT_RUN` notice names the cause.

## Change inventory

- `spec-delegate/references/worker.md` (Validate) and `payload.md` (Workers): replace the equality and the pre-spawn
  record with the notice rule.
- `features/worker/usecases/inspect.py`, `inputs.py`, `cli/commands.py`, the worker notice class beside
  `WorkerCheckNotRunNotice`.
- `CAP-DLV-delivery-workflows`: the acceptance requirement "unchanged base" and the Worker result inspection section,
  its JSON fields and code table.
- A new ADR superseding the base-checkout clauses of `ADR-orchestration-workers`
  (`ADR-worker-delivers-committed-result`, `ADR-informational-range-inspection-reuses-existing-checks`).
- Tests: `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` (worker.md tokens) and
  `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`.
- Completed specs and earlier materials that restate the rule stay unedited as history.
