---
id: SPEC-shared-paging-contract
title: One paging contract for listing commands
summary: Moves devkit exec list onto the shared PAGE and NEXT_CMD paging lines and decides paging for maintenance history list, so listing commands share one grammar.
status: planned
created: 2026-11-11
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-shared-paging-contract] One paging contract for listing commands

## 1. Problem Statement & Motivation

Handed off from proposal PROP-shared-paging-contract on 2026-11-11.

### 1. Background & Hypothesis

Three paging contracts coexist: `echo_page` (docs, spec entrypoints: `[PAGE: ...]` plus `[NEXT_CMD ... --offset N]`, `--limit 0` for all),
`exec list` (its own `[EXECUTION_LIST: ...]` and JSON `next_offset`, limit 1-100) and `maintenance history list`
(`--limit` only, no paging fields). Agents parse each separately, and a change to the shared format misses `exec`.
Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C2-8.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement One paging contract for listing commands so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Can exec keep `EXECUTION_RUN` lines while emitting the shared page lines, and what limit bounds does it keep?
  Yes. `echo_page` (`devkit_dist.adapters.cli`) only prints `[PAGE: ...]` and `[NEXT_CMD: ...]` after the items, so
  `exec list` prints its `[EXECUTION_RUN: ...]` lines unchanged and then `echo_page("uv run devkit exec", total,
  offset, limit, count, ["list", "--limit", str(limit)])`. `isolated_execution/cli.py` already imports from
  `devkit_dist.adapters.cli`; no new import edge. The `next` value is the same: `ListExecutions` computes
  `offset + limit` when below `total`, `echo_page` computes `offset + count`, equal whenever more items follow.
  Exec keeps its bounds (limit 1-100, default 20, offset nonnegative, `EXECUTION_LIST_ARGUMENT_INVALID`): the
  `--limit 0` "all" form of `docs list` is not adopted, because retained runs grow without a bound and each listed
  run reads its manifest; `echo_page` already treats any positive limit correctly.
- **Q2**: Does maintenance history need paging at all? No. `history list` is a "newest N runs" query over a remote
  history branch: `listing()` reads year shards newest first and stops as soon as `limit` eligible runs are found.
  A `total` would force reading every shard, and an offset over a branch that later publications prepend to shifts
  between calls. No agent asset calls it (only `docs/development/reference/maintenance-history.md` shows one
  example), and `--source-sha` and `--outcome` already narrow it. It stays a bounded, unpaged listing with
  `HISTORY_LIST` and `HISTORY_RUN`; the shared grammar applies only to commands that page.

### 3. Proposed Design & Impact

- `devkit exec list` text output: the `[EXECUTION_RUN: ...]` lines, then `[PAGE: total= offset= limit= count= next=]`
  and, when more runs follow, `[NEXT_CMD: uv run devkit exec list --limit <N> --offset <next>]`, all through
  `echo_page`. `[EXECUTION_LIST: ...]` is removed with no transition alias: no agent asset or command parses it (its
  only consumer is `packages/devkit/tests/unit/features/isolated_execution/test_output.py`). An empty list prints
  `[PAGE: total=0 offset=0 limit=20 count=0 next=-]`, which keeps the explicit empty-list result §4 requires.
- JSON output is unchanged (`runs`, `total`, `offset`, `limit`, `next_offset`): JSON paging keys are out of scope.
- `ARCH-08-1-agent-output` gains a short paging subsection under §3 (stdout text): the `[PAGE: total= offset=
  limit= count= next=]` line after the items, `[NEXT_CMD: ...]` only when more items follow, `next=-` on the last
  page, and that each command's limit bounds (and whether it accepts `--limit 0`) stay in its own capability. §10
  gains a checklist item: a listing command that pages uses these lines through `echo_page`.
- `CAP-HARN-command-mount` §4.5 keeps its mounted-group facts and points to `ARCH-08-1-agent-output` for the
  grammar instead of stating it; `CAP-HARN-isolated-execution` §4 (sentinel list and the list paging sentence) points
  to it too and keeps exec's limits; `docs/development/reference/exec.md` (sentinel list) is updated to match.
- Development: one feature spec, `sdd-spec-feature`; tests in `packages/devkit/tests/unit/features/isolated_execution/`.

#### Planning decisions

- Exec keeps limit 1-100 (default 20) and its error code; it does not adopt `--limit 0` (Q1).
- `maintenance history list` stays unpaged (Q2); `CAP-DLV-maintenance-history` is not changed.
- `[EXECUTION_LIST: ...]` is dropped without an alias; JSON output keeps its current keys.
- The shared paging grammar is stated once in `ARCH-08-1-agent-output` (a short subsection and a §10 checklist
  item); `CAP-HARN-command-mount` §4.5 and `CAP-HARN-isolated-execution` §4 point to it, and per-command limits stay
  in each capability (user, q1).

#### Non-Goals

- JSON paging keys across commands; `--limit 0` for exec; paging for `maintenance history list`; a new shared
  paging helper beyond `echo_page`; `docs list`'s own `hidden` and `[HISTORY_CMD]` lines.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr shared-paging-contract "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept shared-paging-contract --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-paging-contract.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

