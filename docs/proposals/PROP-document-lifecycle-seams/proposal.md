---
id: PROP-document-lifecycle-seams
title: Document layer free of lifecycle imports
summary: Makes the document model, the namespace reader and the shared base modules independent of the delivery process inside devkit-spec, with the lifecycle supplying its behavior through extension points.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: documents/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-idea-incubation
boundaries:
  owns:
    - documents/
    - traceability/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-document-layer-package
workflow: sdd-proposal
---

# [PROP-document-lifecycle-seams] Document layer free of lifecycle imports

## 1. Background & Hypothesis

The document code in devkit-spec knows delivery-process concepts: `DocumentIndex` treats completed spec
bundles as historical, browse reads Planning branches and lifecycle fields, the namespace reader lives in
`policy/services/config.py`, and `base/errors.py`, `base/units.py` and `base/axes.py` serve both sides. The coupling
survey `docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md` lists these seams. Moving the document layer into its own package first needs it to stop
importing the lifecycle; otherwise the new package imports devkit-spec or drags policy along.

Hypothesis: extension points let the lifecycle supply its behavior, so `features/documents` and the document side
of `features/entrypoints` import nothing from policy, proposals, delivery, scope or worker, while SDD repositories
observe the same behavior.

## 2. Technical Spike Questions

- **Q1**: Kind vocabulary: do lifecycle kinds stay in the shared kind table (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`), and are milestones document or lifecycle vocabulary?
- **Q2**: Extension points: how the lifecycle supplies the history predicate, the unit-anchor predicate, the live dependency predicate, the bundle layout resolver and the list display fields.
- **Q3**: Configuration: who owns namespaces in `[tool.spec]`; whether two packages can contribute to one config template (the devkit-dist template registers one `[tool.<name>]` owner per table).

## 3. Proposed Design & Impact

- Add the extension points above and remove the `browse.py` dependency on `planning_branches`.
- Move `Namespace` and its reader out of `policy/services/config.py`.
- Split `base/errors.py`, `base/units.py` and `base/axes.py` by owner, keeping the documented `SPEC_` codes.
- Split `features/entrypoints` into the document side (paths, apply) and the lifecycle side (derive, bundle).
- Add an architecture constraint so `features/documents` cannot import the process features.
- Update `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`, `CAP-DOCS-namespaces`, `CAP-TRACE-code-entrypoints`
  and `CAP-DLV-project-policy` where the seams change them. A kind change that the viewer's hard-coded prefixes
  mirror is reported as a follow-up.

## 4. Lifecycle & Retirement Criteria

- Retire with acceptance and handoff, or reject if idea incubation no longer needs a document layer without SDD.
