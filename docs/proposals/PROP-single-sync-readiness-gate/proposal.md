---
id: PROP-single-sync-readiness-gate
title: One readiness gate for a synchronized checkout
summary: Measures what devkit status and devkit sync --check each detect, then makes one of them the single readiness gate or documents the remaining split.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/distribution/
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-single-sync-readiness-gate] One readiness gate for a synchronized checkout

## 1. Background & Hypothesis

The devkit bundle's completion criterion requires both `devkit status` and `devkit sync --check` to exit 0. Their
problem catalogs overlap (`NOT_SYNCHRONIZED`, `SYNC_CONFLICT`, `WORKSPACE_UNSAFE`, `TRANSACTION_PENDING`,
`SELECTION_INVALID`), but separate implementations produce them (`get_project_status` and the sync planner). So each
new problem class is added, documented and tested twice. Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C1-4.

## 2. Technical Spike Questions

- **Q1**: Which problems does each command detect that the other does not (measured on fixtures)?
- **Q2**: Can `sync --check` be the single gate, with `status` kept as a diagnostic report?

## 3. Proposed Design & Impact

- Record the detection matrix first.
- Then either route `status` problem detection through the sync planner or document the deliberate split, and change the completion criterion to one command where possible.
- Any merge of outputs is a contract change: CAP-DIST, reference and the devkit bundle instruction.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr single-sync-readiness-gate "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept single-sync-readiness-gate --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff single-sync-readiness-gate.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
