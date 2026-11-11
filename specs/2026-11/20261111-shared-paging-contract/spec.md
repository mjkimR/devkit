---
id: SPEC-shared-paging-contract
title: One paging contract for listing commands
summary: "Moves devkit exec list text output onto the shared PAGE and NEXT_CMD paging lines and states that paging grammar once in the agent output architecture, so listing commands that page share one grammar; maintenance history list stays an unpaged bounded listing."
status: completed
created: 2026-11-11
related_capabilities:
  - CAP-HARN-isolated-execution
  - CAP-HARN-command-mount
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-shared-paging-contract] One paging contract for listing commands

## 1. Problem Statement & Motivation

Handed off from proposal PROP-shared-paging-contract on 2026-11-11.

Three paging contracts coexist. `echo_page` in `devkit_dist.adapters.cli` (used by `devkit docs` and the
`devkit spec` entrypoint listings) prints `[PAGE: total= offset= limit= count= next=]` after the items and
`[NEXT_CMD: ... --offset N]` when more items follow. `devkit exec list` prints its own `[EXECUTION_LIST: ...]`
line before the runs, and `maintenance history list` takes only `--limit`. An agent parses each form separately,
and a change to the shared format misses `exec`. Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md`
finding C2-8.

The grammar itself is stated only inside `CAP-HARN-command-mount` §4.5, which owns the `devkit spec` and
`devkit docs` mounts, so a command outside those groups has no contract to follow.

## 2. User Stories

- **US-1**: As an agent listing retained execution runs, I want `devkit exec list` to end with the same `[PAGE]`
  and `[NEXT_CMD]` lines as `devkit docs list`, so one matcher pages every listing command.
- **US-2**: As a developer adding a listing command, I want the paging grammar stated once in the agent output
  architecture, so I reuse `echo_page` instead of inventing a third form.

## 3. Non-Goals

1. **Scope Excluded**: JSON paging keys across commands; `exec list --format json` keeps `runs`, `total`, `offset`,
   `limit` and `next_offset`.
2. **Scope Excluded**: `--limit 0` ("all") for `exec list`. **Rationale**: retained runs grow without a bound and
   each listed run reads its manifest; exec keeps limit 1-100, default 20.
3. **Scope Excluded**: paging for `maintenance history list`; `CAP-DLV-maintenance-history` is not changed.
   **Rationale**: it is a "newest N runs" query that stops reading shards once `limit` runs are found; a `total`
   would force reading every shard and an offset shifts as publications are prepended.
4. **Scope Excluded**: a new shared paging helper beyond `echo_page`, and any change to `echo_page` or
   `packages/devkit-dist/`.
5. **Scope Excluded**: `docs list`'s own `hidden` field and `[HISTORY_CMD]` line, which stay in
   `CAP-HARN-command-mount` §4.5 and `CAP-DOCS-document-lookup`.
6. **Scope Excluded**: a transition alias for `[EXECUTION_LIST: ...]`; no agent asset or command parses it.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A page with more runs ends with PAGE and NEXT_CMD
- **Given** 25 retained runs
- **When** an agent runs `uv run devkit exec list`
- **Then** stdout is 20 `[EXECUTION_RUN: ...]` lines, then `[PAGE: total=25 offset=0 limit=20 count=20 next=20]`,
  then `[NEXT_CMD: uv run devkit exec list --limit 20 --offset 20]`; the exit code is `0` and no
  `[EXECUTION_LIST: ...]` line is printed

### [AC-02] The last page has next=- and no NEXT_CMD
- **Given** 25 retained runs
- **When** an agent runs `uv run devkit exec list --offset 20`
- **Then** stdout is 5 `[EXECUTION_RUN: ...]` lines, then `[PAGE: total=25 offset=20 limit=20 count=5 next=-]`,
  and no `[NEXT_CMD: ...]` line

### [AC-03] A custom limit is repeated in NEXT_CMD
- **Given** 25 retained runs
- **When** an agent runs `uv run devkit exec list --limit 5 --offset 5`
- **Then** the last two lines are `[PAGE: total=25 offset=5 limit=5 count=5 next=10]` and
  `[NEXT_CMD: uv run devkit exec list --limit 5 --offset 10]`

### [AC-04] An empty list is an explicit PAGE line
- **Given** no retained runs
- **When** an agent runs `uv run devkit exec list`
- **Then** stdout is exactly `[PAGE: total=0 offset=0 limit=20 count=0 next=-]` followed by a newline, exit `0`

### [AC-05] Exec keeps its limit bounds and error code
- **Given** any repository
- **When** an agent runs `uv run devkit exec list` with `--limit 0`, `--limit 101` or `--offset -1`
- **Then** the command fails with `EXECUTION_LIST_ARGUMENT_INVALID` and exit `2`, printing no `[PAGE: ...]` line

### [AC-06] JSON output is unchanged
- **Given** 25 retained runs
- **When** an agent runs `uv run devkit exec list --format json`
- **Then** stdout is one JSON object with the keys `runs`, `total`, `offset`, `limit` and `next_offset`, and
  `next_offset` is `20`

### [AC-07] The paging grammar is stated once and referenced
- **Given** the Living Spec after this change
- **When** a reader looks up the paging lines
- **Then** `ARCH-08-1-agent-output` §3 states the `[PAGE]` and `[NEXT_CMD]` grammar and that per-command limit
  bounds stay in each command's capability, and §10 has a checklist item that a listing command that pages prints
  them through `echo_page` (or `fields_line` when it adds fields after `next`, as `docs list` does); `CAP-HARN-command-mount` §4.5 and `CAP-HARN-isolated-execution` §4 refer to
  `ARCH-08-1-agent-output` for the grammar while keeping their own limits; and `rg -n EXECUTION_LIST` over
  `docs/architecture`, `docs/capabilities`, `docs/development` and `packages/devkit/src` matches only
  `EXECUTION_LIST_ARGUMENT_INVALID`

## 5. Assumptions

- `echo_page` computes `next` as `offset + count`; `ListExecutions` computes `next_offset` as `offset + limit`.
  They are equal whenever more runs follow, so text and JSON report the same next offset.
- `[NEXT_CMD]` always repeats `--limit <N>`, also at the default, as `devkit docs list` does, so the line stays
  correct if the default changes.
- The `--offset` help text names both the `[PAGE]` `next` field and the JSON `next_offset` key.
