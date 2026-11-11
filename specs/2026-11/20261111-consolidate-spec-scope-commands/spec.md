---
id: SPEC-consolidate-spec-scope-commands
title: Consolidate the spec scope commands around collect
summary: Retires the devkit spec scope register, query, compare and hidden update commands with the registry update path, the journal and the second paths-changed pipeline, narrowing scope observation to collect beside release and sweep.
status: completed
created: 2026-11-11
related_capabilities:
  - CAP-COLL-work-scope-registry
  - CAP-HARN-command-mount
  - CAP-HARN-agent-guidance
  - CAP-DLV-proposal-planning
related_usecases:
  - UC-run-parallel-work-safely
workflow: sdd-spec-feature
---

# [SPEC-consolidate-spec-scope-commands] Consolidate the spec scope commands around collect

## 1. Problem Statement & Motivation

Handed off from proposal PROP-consolidate-spec-scope-commands on 2026-11-11.

- **Preserved Materials**: `docs/materials/2026-11/20261111-consolidate-spec-scope-commands`
  (`scope-command-callers.md`: callers, the update write path, codes and the two pipelines at the Planning head).
- **Target Docs Blueprint**: `PROP-consolidate-spec-scope-commands-target` (Living Spec targets for this plan and
  `reconcile.md`).
- **Decision**: `ADR-collect-only-scope-observation`, superseding in part `ADR-worktrees-and-scope`.

Guidance uses only `devkit spec scope collect` (spec-orchestrate), plus `sweep` and `release` (spec worktree
reference, spec-integrate). `register`, `query` (with its `--history` journal reader), `compare` and the hidden
`update` have no documented caller outside `CAP-COLL-work-scope-registry`, yet they keep the registry write path
(the update ACK, `--request-id` replay, journal events) and a second "paths changed since base" pipeline
(`observe_git` beside collect's observation service). `collect --mode` selects a depth no caller varies: every mode
already reads the registry snapshots, and the default is the only value guidance passes.

One observation entry (`collect`) plus `release` and `sweep` covers every documented workflow with one pipeline.

## 2. User Stories

- **US-1**: As the orchestrating Host agent, I want `devkit spec scope` to offer only `collect`, `release` and the
  hidden `sweep`, so that no command, option or fix string points me at a surface nobody needs.
- **US-2**: As the Host, I want creation registration and `collect` to share one implementation of the paths a task
  changed, so that a snapshot and a live observation of the same task cannot disagree on how the paths are read.
- **US-3**: As a maintainer, I want the registry without its update path and journal, so that its records, locking
  and codes are only what `collect`, `release`, `sweep` and the post-finish cleanup use.

`UC-run-parallel-work-safely` changes: step 1 compares planned declarations through `collect` once a unit has a
`plan-*` or `dev-*` source, and queued drafts are not observed.

## 3. Non-Goals

1. **Scope Excluded**: no replacement for `compare` or `query --history`, and no `scope history` command.
2. **Scope Excluded**: no change to `collect`'s inventory, base selection, range rules, horizons, budgets, limits,
   report shape (apart from the removed `mode` field) or its read-only access to the registry.
3. **Scope Excluded**: no migration or rewrite of existing records or of an existing `journal.jsonl`; old records stay
   readable as they are and an old journal file is neither read nor removed.
4. **Scope Excluded**: no change to the `devkit.post_finish` extension's `ScopedCleanup` contract, its targets or its
   notices, and no change to `packages/devkit/` or `packages/devkit-dist/`.
5. **Scope Excluded**: no change to `release` or `sweep` options, outputs or exit codes; their journal side effect
   goes with the journal.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Only collect, release and sweep remain

- **Given** the installed `devkit spec` CLI
- **When** `devkit spec scope --help` is read, and `devkit spec scope register`, `query`, `compare` or `update` is run
- **Then** the help lists `collect` and `release` (and no other visible command), `sweep` stays a hidden command, each
  removed name exits 2 with Click's `No such command` usage error, and no source or test asserts a `[SCOPE_ACK` line.

### [AC-02] Creation registration records declarations and dirty paths through the observation service

- **Given** a linked worktree on `dev-<slug>` with uncommitted handoff output (a new file, a staged change and an
  unstaged change) and one untracked path whose name is outside the path contract (contains a colon or a glob
  character)
- **When** `devkit spec proposal handoff` or `devkit spec new` registers the unit
- **Then** the stored record holds the bundle's declared scopes, every valid dirty path as `observed`, the
  declaration's unresolved inputs plus one `invalid-path` entry (source `observed`) for the invalid name,
  `base_revision` = HEAD at creation and `base_ref` = the base checkout's branch, and no `missing-base-ref`,
  `missing-base-revision` or `unknown-base-revision` reason; the `[SCOPE: ...]` line and JSON `scope` object keep their
  fields and the commands exit 0 as before.

### [AC-03] Collect observes every source without a mode

- **Given** a registered `dev-*` worktree, an unregistered `dev-*` branch and a `plan-*` ref
- **When** `devkit spec scope collect` runs with no options
- **Then** it reports the snapshot, ref and worktree observations, the registered one with `range_method` =
  `registered-cap` and the unregistered ones with `branch-relative`, the same horizons and coverage the former
  default `worktrees` mode reported, and its JSON has no `mode` key.

### [AC-04] Collect options

- **Given** the `collect` command
- **When** it runs with `--mode <any value>`
- **Then** it exits 2 with Click's `No such option` usage error; `--base`, `--fetch`, `--timeout` and
  `--source-timeout` keep their validation (`ARGUMENT_INVALID`, exit 2, for a budget outside 1..300 or an unconfigured
  remote) and their effects.

### [AC-05] Records and journal from before the change

- **Given** a registry namespace holding a record written before the change (with `last_request_id`, `last_added`,
  `last_removed` and observed scopes) and an existing `journal.jsonl`
- **When** `collect`, `release`, `sweep --apply` and the post-finish cleanup run against it
- **Then** they read the record without a new warning, keep their outputs, codes and the `ScopedCleanup` contract,
  write no journal line, and leave `journal.jsonl` byte-identical; a record written by creation registration after the
  change still carries the `last_*` keys with their zero values (schema version 1 unchanged).

### [AC-06] Codes and fix strings name only what exists

- **Given** the scope feature, its errors in `devkit_spec.base.errors` and the post-finish cleanup
- **When** the codes test compares the `SPEC_SCOPE_*` codes (plus `SPEC_POST_FINISH_CLEANUP`) those classes define
  with the code rows of `CAP-COLL-work-scope-registry` §4.8, and a test scans every `fix` of those classes and every
  fix string in the scope feature
- **Then** both sets are equal in both directions (`SPEC_SCOPE_ACK_FAILED`, `SPEC_SCOPE_TOKEN_MISSING`,
  `SPEC_SCOPE_RECORD_MISSING`, `SPEC_SCOPE_JOURNAL_UNAVAILABLE` and `SPEC_SCOPE_JOURNAL_LINE_INVALID` are gone from
  both), and no fix names `scope register`, `scope query`, `scope compare`, `scope update`, `--request-id`,
  `--task-id` (outside `release`) or `--mode`.

## 5. Decisions and assumptions

### Decided in Planning (user)

- **q1 Journal**: the scope journal and its reader are removed, together with the journal error codes.
- **q2 compare**: `devkit spec scope compare` is retired with no replacement.
- **q3 Creation dirty paths**: creation registration keeps recording the dirty paths at creation, read through
  collect's observation service.
- **q4 `--base`**: the `collect --base` option is kept.

Historical record: `eb2d5dba4bfd08a06e492a0d427ad4a7afa27309:docs/proposals/PROP-consolidate-spec-scope-commands/envelopes/answer-01.yaml`.

### Planning decisions carried

- **Collect options**: `--mode` goes with the JSON `mode` field; `SPEC_SCOPE_COLLECTION_FAILED` fixes stop naming a
  mode, and the report-metadata limit fix says to report the limit. `SPEC_SCOPE_COLLECTION_PARTIAL` offers the budgets
  for `source-timeout` only, not for `result-limit`. `--fetch`, `--timeout`, `--source-timeout` and `--base` stay.
- **Creation registration** keeps its best-effort, verbose-only failure handling and runs its Git reads under the
  `[tool.spec.scope] timeout`. Its committed range is empty by construction, so the Git-side unresolved reasons of
  §4.1 are no longer stored on new records; collect reports an unusable base as `unknown-base`.
- **Codes**: `own()` returns no record when the token or its record is gone; `SPEC_SCOPE_TOKEN_MISSING`,
  `SPEC_SCOPE_RECORD_MISSING`, `SPEC_SCOPE_ACK_FAILED` and the two journal codes go. `SPEC_SCOPE_TOKEN_EXISTS`,
  `SPEC_SCOPE_TASK_EXISTS` and `SPEC_SCOPE_SHARED_WORKTREE` stay as verbose diagnostics of creation registration,
  their fixes no longer naming `scope query`, `scope update` or `--task-id`. `SPEC_SCOPE_SPEC_NOT_FOUND` stays defined
  and documented: creation registration raises it internally for a missing bundle and swallows it.
- **Use case wording**: queued Backlog drafts and drafts accepted with `--direct` on the base stay unobserved until
  they have a `plan-*` or `dev-*` source.

### Assumptions (Development)

- **A1 Superseded ADR body**: the Development write scope admits only the "Superseded in part" line of
  `ADR-worktrees-and-scope`, and `RULE-decision-supersession` requires that line to repeat the superseder's statement
  verbatim, so it stays as the handoff wrote it. The in-place rewording of the `query`/history mentions in its §4, §5
  and §6, which that statement announces, is outside this write scope and is left for the Host.
- **A2 Records keep the retired keys**: records stay schema version 1 and creation keeps writing `last_request_id`,
  `last_added` and `last_removed` with empty and zero values, so readers of either age see one shape; nothing reads
  them.
- **A3 Dirty-path runner**: creation registration calls the observation service's dirty-path listing with the
  command's `Deadline` (`[tool.spec.scope] timeout`), so a timeout still fails the registration (swallowed as a
  verbose diagnostic) instead of returning partial coverage.
- **A4 Sweep and release journal**: their journal appends were side effects only; removing them changes neither their
  output nor their exit code.

## 6. Source feedback

None: the proposal was drafted from `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` (C3-2,
C3-3, C3-6) and `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` (SP-1), not from feedback IDs.
