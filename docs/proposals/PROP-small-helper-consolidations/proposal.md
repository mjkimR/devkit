---
id: PROP-small-helper-consolidations
title: Consolidate the remaining duplicated runtime helpers
summary: 'Consolidates three deferred duplicates: the UTF-8 output helper copied from devkit-cli into devkit-dist, the hand-rolled YAML quoting of subagent projections, and the four Git tracked/ignored probes.'
status: draft                         # draft | reviewing | accepted | rejected
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

# [PROP-small-helper-consolidations] Consolidate the remaining duplicated runtime helpers

## 1. Background & Hypothesis

Three small duplicates were deferred by the code pass (`docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`):
- X-13: `_utf8_output` is copied from devkit-cli into devkit-dist (and devkit-dist host CLI). A shared public devkit-cli helper is a semver-minor addition.
- DS-09: subagent projection hand-rolls YAML quoting, and a switch to the shared serializer changes projected bytes on the next sync.
- DS-10: four Git tracked/ignored probes do the same query.

## 2. Technical Spike Questions

- **Q1**: X-13: may devkit-dist depend on a new public devkit-cli helper, or should the helper move to devkit-core?
- **Q2**: DS-09: is a one-time projection byte change acceptable (receipt and managed copies re-sync)?
- **Q3**: Which DS-10 probes have different ignore semantics that must stay?

## 3. Proposed Design & Impact

- One helper per duplicate, with each caller's options kept or explicitly approved (the review-refactor helper-adoption lesson).
- The decomposer may split this into three small items if Planning finds them independent.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr small-helper-consolidations "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept small-helper-consolidations --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff small-helper-consolidations.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
