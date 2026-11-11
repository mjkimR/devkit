---
id: PROP-consolidate-spec-scope-commands
title: Consolidate the spec scope commands around collect
summary: Retires or folds the devkit spec scope register, query, compare and hidden update commands and the second paths-changed pipeline into the Host's collect observation, keeping release, sweep and the journal.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/collaboration/
priority: low                         # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/collaboration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-consolidate-spec-scope-commands] Consolidate the spec scope commands around collect

## 1. Background & Hypothesis

Guidance uses only `devkit spec scope collect` (spec-orchestrate), plus `sweep` and `release` (worktree reference).
`register`, `query`, `compare` and the hidden `update` have no documented caller outside `CAP-COLL-work-scope-registry`,
yet they keep the registry write path (update ACK, `--request-id` idempotency, journal events) and a second
"paths changed since base" pipeline (code-pass SP-1). `collect` exposes `--mode snapshot|refs`, `--base`, `--fetch`
and two timeouts that no caller varies (C3-3). `query --history` switches the command into a journal reader with its
own paging grammar (C3-6). Sources: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C3-2, C3-3, C3-6; `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` SP-1.

Hypothesis: one observation entry (`collect`) plus `release`, `sweep` and a journal reader covers every documented
workflow with one pipeline.

## 2. Technical Spike Questions

- **Q1**: Which commands does any Host procedure, extension or CI still need (`register` is reached internally by handoff)?
- **Q2**: `ADR-worktrees-and-scope` retains the hidden `update` and its ACK contract, and decides the collect modes. Which clauses need a superseding decision?
- **Q3**: Should `compare` fold into collect's declared and future evidence, and should the journal become `scope history`?

## 3. Proposed Design & Impact

- Retire the unused commands and the registry write path they alone use, keeping handoff's internal registration.
- Narrow `collect` to the depth and options its callers use. Unify the two paths-changed pipelines (SP-1).
- Give the journal its own reader with the shared `--limit/-n` paging grammar.
- Update CAP-COLL §4.4/§4.9, CAP-HARN-command-mount §4.2, UC-run-parallel-work-safely, error `[FIX]` strings, the ADR and tests. This is a contract change; the size may need a decomposer split.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr consolidate-spec-scope-commands "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept consolidate-spec-scope-commands --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff consolidate-spec-scope-commands.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
