---
id: ADR-collect-only-scope-observation
title: Collect is the only scope observation surface
summary: For the scope registry, we retire register, query, compare and hidden update with the update path, keep creation snapshots without their own Git range code and drop collect --mode, to keep one observation entry and one paths-changed pipeline, accepting creation-time records.
proposal: SPEC-consolidate-spec-scope-commands
supersedes: [ADR-worktrees-and-scope]
status: accepted
created_at: 2026-11-11
---

# [ADR-collect-only-scope-observation] Collect is the only scope observation surface

- **Status**: Accepted
- **Date**: 2026-11-11

---

## 1. Context & Problem Statement

`ADR-worktrees-and-scope` moved scope observation to the Host (`devkit spec scope collect`) and removed the
workers' registration, update and ACK duties. It still kept the hidden maintenance `update` with its ACK contract,
three collect modes and the commands of the earlier worker-driven registry: `register`, `query` (with a journal
reader behind `--history`) and `compare`. No guidance, CI job or other package invokes `register`, `query`,
`compare` or `update`; only `collect`, `release` and `sweep` have callers. The update path alone uses `request_id`
replay, the ACK model, the record's `last_*` fields and the journal's `update` events. The registry keeps a second
"paths changed since base" pipeline (`observe_git`) beside collect's; after `update` goes its only caller is the
creation registration, whose range starts at the registration HEAD, so its committed range is always empty and only
its staged, unstaged and untracked listing contributes. Evidence: the proposal's `docs/materials/2026-11/20261111-consolidate-spec-scope-commands/scope-command-callers.md`.

## 2. Decision Drivers

- One observation entry for the Host, with no command or option that has no caller.
- One implementation of the committed range and dirty paths.
- Keep what collect, the post-finish cleanup, `release` and `sweep` need: records, tokens, revisions and locking.
- Keep partial coverage visible; never present missing evidence as no overlap, including for snapshot-only sources
  (a registry shared with another host, a local source collect cannot read).
- No external consumers exist, so the surface changes without a compatibility period.

## 3. Considered Options

- **Retire the unused commands and the update path; creation keeps its snapshot through collect's observation
  service** (selected): one pipeline, smaller registry; records cannot be refreshed and stay creation-time
  snapshots.
- **Keep the commands hidden** (rejected): the write path, its codes and its tests stay maintained for no caller.
- **Creation records declarations only** (rejected): drops the uncommitted
  handoff output that a snapshot-only source relies on.
- **Keep `observe_git` for creation** (rejected): it duplicates collect's range logic for a range that is empty at
  creation.
- **Fold `compare` into collect as declaration inputs** (rejected): it adds input options to the command
  being narrowed for drafts that `future`-only overlap would not serialize anyway.
- **Keep the journal, with a `scope history` reader or without any reader** (rejected): it keeps the event model,
  append locking and two warning codes for diagnostics nothing reads, in a file without retention.
- **Drop `collect --base`** (rejected): remote-tracking `plan-*`/`dev-*` refs carry no base marker, so when
  `<remote>/HEAD` and the main checkout branch differ they would report `unknown-base` with no override, or need a
  new base-selection rule.

## 4. Decision Outcome

Supersedes in part `ADR-worktrees-and-scope`: in §4 "Host-owned scope observation", the clause that `scope collect`
has `snapshot`, `refs` and default `worktrees` modes, and the clause that the maintenance `update` stays directly
callable with its existing ACK contract; in §6, the clause that the maintenance ACK tests remain regression checks.
Its other decisions, including opt-in fetch, bounded deadlines, read-only collection, the ownership tests and the
post-finish cleanup, remain in force; its wording about `query` and history reads (§4 "Registry storage and read
access", §5, §6) is reworded to the remaining read surfaces without changing those decisions.

- `devkit spec scope register`, `query` (with `--history`), `compare` and the hidden `update` are removed. The
  scope group keeps `collect`, `release` and the hidden `sweep`.
- The registry update operation, `request_id` replay, the ACK and its `[SCOPE_ACK]` sentinel and the codes
  `SPEC_SCOPE_ACK_FAILED`, `SPEC_SCOPE_TOKEN_MISSING` and `SPEC_SCOPE_RECORD_MISSING` are removed. Records are written
  by creation registration and removed by `release`, `sweep` and the post-finish cleanup; a record on disk may still
  carry the retired `last_*` fields.
- Creation registration (`devkit spec proposal handoff`, `devkit spec new`) stores the bundle's declarations, its
  unresolved inputs, the base anchors (`base_revision`, `base_ref`) and the dirty paths at creation obtained from
  collect's observation service; `observe_git` is removed. Collect is the only implementation of the committed range
  and keeps the registration cap of `CAP-COLL-work-scope-registry` §4.1 for registered observations.
- `collect` always observes at its full depth (records, local and remote-tracking `plan-*`/`dev-*` refs, accessible
  worktrees). `--mode` is removed; `--base` (the explicit base override for candidates without a base marker),
  `--fetch`, `--timeout` and `--source-timeout` remain.
- The registry journal, its reader and the codes `SPEC_SCOPE_JOURNAL_UNAVAILABLE` and
  `SPEC_SCOPE_JOURNAL_LINE_INVALID` are removed; an existing journal file is left untouched.

## 5. Consequences

- **Positive**: one observation command and one Git pipeline; the registry loses its only optimistic-update write
  path, the journal and five codes; fix strings no longer name commands that have no caller.
- **Negative / Risks**:
  - A record's scope stays as observed at creation; collect's live worktree and ref observations supersede it when
    they succeed, and later private edits on another host stay invisible as before.
  - Queued Backlog drafts and drafts accepted on the base have no observation until they get a `plan-*` or `dev-*`
    source.
  - Registry changes leave no history trail; diagnosing a vanished record relies on Git and the post-finish notices.
- **Follow-ups**: none.

## 6. Confirmation

Development verifies the acceptance criteria of the handed-off spec with scope and delivery integration tests: the
removed commands are unknown to the CLI, creation registration records declarations and dirty paths without its own
range code, collect results for registered and unregistered sources keep their §4.1/§4.9 ranges, the post-finish
cleanup, `release` and `sweep` keep their contracts, records carrying the retired fields stay readable, and the
code table matches the defined codes in both directions.
