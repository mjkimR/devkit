---
id: PROP-shared-paging-contract
title: One paging contract for listing commands
summary: Moves devkit exec list onto the shared PAGE and NEXT_CMD paging lines and decides paging for maintenance history list, so listing commands share one grammar.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/harness/
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/harness/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-paging-contract] One paging contract for listing commands

## 1. Background & Hypothesis

Three paging contracts coexist: `echo_page` (docs, spec entrypoints: `[PAGE: ...]` plus `[NEXT_CMD ... --offset N]`, `--limit 0` for all),
`exec list` (its own `[EXECUTION_LIST: ...]` and JSON `next_offset`, limit 1-100) and `maintenance history list`
(`--limit` only, no paging fields). Agents parse each separately, and a change to the shared format misses `exec`.
Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C2-8.

## 2. Technical Spike Questions

- **Q1**: Can exec keep `EXECUTION_RUN` lines while emitting the shared page lines, and what limit bounds does it keep?
- **Q2**: Does maintenance history need paging at all?

## 3. Proposed Design & Impact

- Emit `[PAGE]`/`[NEXT_CMD]` through `echo_page` for `exec list`. Revise CAP-HARN-isolated-execution §4 (sentinel contract change).
- Leave or align maintenance history depending on Q2.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr shared-paging-contract "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept shared-paging-contract --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-paging-contract.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
