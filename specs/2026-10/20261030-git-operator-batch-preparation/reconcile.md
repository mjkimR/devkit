---
reconcile_id: REC-git-operator-batch-preparation
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: `SPEC-git-operator-batch-preparation`

## Contract comparison

- `CAP-DLV-delivery-workflows` §4.6.1 adds one paragraph of EARS rules for the preparation list, as `git-operator.md`
  (Input, Procedure, Authority and boundaries, Return), `git-operator-dispatch.md`, `git-operator-operations.md` and
  `spec-delegate/references/payload.md` state it: only `prepare-worktree` forms a finite, exact list with every job
  field repeated per item and one retained base and base ref (AC-01); the list's authority covers only its listed
  items (AC-05); items run serially in the listed order, each with its own refresh and Codex approval request, the
  base HEAD is checked against the dispatched base ref before each item, and the list stops at the first item that is
  not completed with later items not attempted (AC-02); the return holds `items` (the single-job return unchanged)
  and `not_attempted` (identity, intended effects, null CLI result) with the three-status rule and no partial status
  (AC-03); a setup or sync remainder returns to the Host and the Host retries only the remaining items it still
  authorizes after verifying the returned state (AC-04). The paragraph cites `SPEC-git-operator-batch-preparation`
  and `MAT-git-operator-batch-dispatch-observation`. The tests paragraph names the preparation-list wording, and the
  unverified list adds a live partial preparation list (spec non-goal 5). Verified by the AC-01..AC-06 contract-text
  tests in `test_git_operator.py`.
- The GOP-06 sentence of §4.6.1 and the single-job return wording are unchanged; `SPEC-git-operator-result-readiness`
  owns them, and their regression tests pass unchanged.
- The CAP-DLV `summary` is unchanged: "reusable lean git-operator executes Host-authorized lifecycle jobs" still
  covers a preparation list of `prepare-worktree` jobs, and §4.6's role table row ("exact guarded lifecycle effects
  in the current Host job") holds for each listed item.

## No impact

- `CAP-WT-task-worktrees`: unchanged; every item runs the existing `devkit worktree start`, and the diff against the
  base for `packages/devkit/` is empty (AC-07; 122 worktree CLI tests pass unchanged).
- `UC-drive-development-to-integration` extension 1b and Scenario 22 ("the Host reuses git-operator for read-only
  preparation and exact authorized execution") stay true for a list; the use case's goal and steps do not change, and
  no use case is in this unit's write scope.
- No architecture contract, ADR, glossary term or screen changed. "preparation list" qualifies the bare noun "item"
  and is defined by the role contract and §4.6.1; it names no new domain concept that needs a glossary row.

## Entrypoints

`devkit spec entrypoints derive` proposed five new paths for `CAP-DLV-delivery-workflows`; none is written. The
doorway `subagents/git-operator.md` is already declared; the dispatch, operations and payload references are
guidance read from it, the test is not a doorway, and `.devkit/installation.json` is a sync output.

## Deferred work

None. The live stop and retry behavior of a real partial list is an unverified area, not deferred scope: the spec
excludes measuring it (non-goal 5), and `MAT-git-operator-batch-dispatch-observation` records that it is unexercised.
