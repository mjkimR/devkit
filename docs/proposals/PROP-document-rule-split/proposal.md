---
id: PROP-document-rule-split
title: Split mixed governance rules into document and lifecycle rules
summary: Splits the governance rules that mix document and lifecycle checks so document rules depend only on the document layer.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: governance/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-idea-incubation
boundaries:
  owns:
    - governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-document-layer-package
depends_on: [PROP-document-lifecycle-seams]
workflow: sdd-proposal
---

# [PROP-document-rule-split] Split mixed governance rules into document and lifecycle rules

## 1. Background & Hypothesis

Three governance rules mix document and lifecycle checks: `document_reference` (handoff resolution and the
PROP/SPEC slug collision), `spec_format` (milestone statuses, proposal effort hints, namespace on unit anchors) and
`id_convention` (spec bundle and feedback path grammars, and a helper imported from `spec_lifecycle`). Governance
also imports the policy config reader. See `docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md`.

Hypothesis: after the seams are removed, splitting these rules leaves document rules that depend only on the
document layer, with lifecycle checks in lifecycle-owned rules.

## 2. Technical Spike Questions

- **Q1**: Where each mixed rule splits, and where `is_proposal_anchor` belongs.
- **Q2**: Whether split checks keep their rule IDs or get new lifecycle rule IDs.

## 3. Proposed Design & Impact

- Split `document_reference`, `spec_format` and `id_convention`; move `trailing_comment` to a neutral module;
  give `document_summary` a neutral skeleton marker.
- Remove the governance imports of the policy config reader.
- Register new rule assets in the spec bundle; mark `spec_lifecycle`, `spec_progress`, `task_coverage`,
  `reconcile_contract`, `proposal_boundaries` and the rejected-proposal hygiene as lifecycle-owned.
- Update `CAP-GOV-spec-rules`.

## 4. Lifecycle & Retirement Criteria

- Retire with acceptance and handoff, or reject if idea incubation no longer needs a document layer without SDD.
