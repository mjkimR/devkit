---
id: PADR-collect-only-scope-observation
title: Collect is the only scope observation surface
summary: For the scope registry, we retire register, query, compare and hidden update with the update path, keep creation snapshots of declarations only and narrow collect, to keep one observation entry and one paths-changed pipeline, accepting creation-time records.
proposal: PROP-consolidate-spec-scope-commands
supersedes: [ADR-worktrees-and-scope]
status: draft
created_at: 2026-11-11
---

# [PADR-collect-only-scope-observation] Collect is the only scope observation surface

- **Status**: Draft
- **Date**: 2026-11-11

---

## 1. Context & Problem Statement

`ADR-worktrees-and-scope` moved scope observation to the Host (`devkit spec scope collect`) and removed the
workers' registration, update and ACK duties. It still kept the hidden maintenance `update` with its ACK contract,
three collect modes and the commands of the earlier worker-driven registry: `register`, `query` (with a journal
reader behind `--history`) and `compare`. No guidance, CI job or other package invokes `register`, `query`,
`compare` or `update`; only `collect`, `release` and `sweep` have callers. The update path alone uses `request_id`
replay, the ACK model, the record's `last_*` fields and the journal's `update` events. The registry keeps a second
"paths changed since base" pipeline (`observe_git`) beside collect's, and after `update` goes its only caller is the
creation registration, where the registration HEAD is the range start, so its committed range is always empty.
Evidence: the proposal's `materials/scope-command-callers.md`.

## 2. Decision Drivers

- One observation entry for the Host, with no command or option that has no caller.
- One implementation of the committed range and dirty paths.
- Keep what collect, the post-finish cleanup, `release` and `sweep` need: records, tokens, revisions, locking and
  the journal writes.
- Keep partial coverage visible; never present missing evidence as no overlap.
- No external consumers exist, so the surface changes without a compatibility period.

## 3. Considered Options

- **Retire the unused commands and the update path; creation records declarations only** (selected): one
  pipeline, smaller registry; records cannot be refreshed and stay creation-time snapshots.
- **Keep the commands hidden** (rejected): the write path, its codes and its tests stay maintained for no caller.
- **Keep `observe_git` for creation and share helpers with collect** (rejected): the creation range is empty by
  construction, so the shared code would serve only the dirty files of the creation commit, which collect observes
  live anyway.
- **Fold `compare` into collect as declaration inputs** (open: proposal question on `compare`): it would add input
  options to the command being narrowed.

## 4. Decision Outcome

Supersedes in part `ADR-worktrees-and-scope`: in §4 "Host-owned scope observation", the clauses that `scope collect`
has `snapshot`, `refs` and default `worktrees` modes, and that the maintenance `update` stays directly callable with
its ACK contract; in §6, the sentence that the maintenance ACK tests remain regression checks. Its other decisions,
including opt-in fetch, bounded deadlines, the read-only collection and the post-finish cleanup, remain in force.

- `devkit spec scope register`, `query` (with `--history`), `compare` and the hidden `update` are removed. The
  scope group keeps `collect`, `release` and the hidden `sweep`.
- The registry update operation, `request_id` replay, the ACK and its `[SCOPE_ACK]` sentinel, `SPEC_SCOPE_ACK_FAILED`
  and `SPEC_SCOPE_TOKEN_MISSING` are removed. Records are written by creation registration and removed by `release`,
  `sweep` and the post-finish cleanup; a record read from disk may still carry the retired `last_*` fields.
- Creation registration (`devkit spec proposal handoff`, `devkit spec new`) stores the bundle's declarations, its
  unresolved inputs and the base anchors (`base_revision`, `base_ref`); it collects no Git paths. Collect is the only
  paths-changed pipeline and keeps the registration cap of `CAP-COLL-work-scope-registry` §4.1 for registered
  observations.
- `collect` always observes at its full depth (records, local and remote-tracking `plan-*`/`dev-*` refs, accessible
  worktrees). `--mode` and `--base` are removed; `--fetch`, `--timeout` and `--source-timeout` remain.
- The journal keeps its writes; how it is read follows the proposal's answer on the journal reader.

## 5. Consequences

- **Positive**: one observation command and one Git pipeline; the registry loses its only optimistic-update write
  path and two codes; fix strings no longer name commands that have no caller.
- **Negative / Risks**:
  - A record's scope stays as declared at creation; collect's live worktree and ref observations supersede it when
    they succeed, so a snapshot only stands in for a source collect cannot reach.
  - A base that the selection chain (`devkitBase`, record base, integration hints) cannot settle stays
    `unknown-base`, a coverage gap, with no per-call override; `SPEC_SCOPE_COLLECTION_PARTIAL` already names the
    recovery (commit the unit on its activity branch).
- **Follow-ups**: none.

## 6. Confirmation

Development verifies the acceptance criteria of the handed-off spec with scope and delivery integration tests: the
removed commands are unknown to the CLI, creation registration writes declarations without observed paths,
collect results for registered and unregistered sources keep their §4.1/§4.9 ranges, the post-finish cleanup,
`release` and `sweep` keep their contracts, and records carrying the retired fields stay readable.
