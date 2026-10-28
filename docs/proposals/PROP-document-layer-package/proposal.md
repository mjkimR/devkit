---
id: PROP-document-layer-package
title: Document layer package
summary: Moves the document system (model, formats, document rules and lookup commands) out of devkit-spec into its own package so that delivery processes such as SDD and idea incubation build on it without coupling it to the SDD lifecycle.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: documents/
priority: medium                      # critical | high | medium | low
size: XL                              # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-idea-incubation
boundaries:
  owns:
    - documents/
    - governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-document-layer-package] Document layer package

## 1. Background & Hypothesis

devkit-spec holds two kinds of feature in one package and one bundle. The document system (the document model,
lookup and search, namespaces, formats, templates, writing instructions and document rules) serves any repository
that keeps devkit documents. The delivery process (proposals, specs, workflows, scope, workers, lifecycle rules and
the `/spec` skills) is SDD. The bundle's `core` preset installs both together, and the document code knows
lifecycle concepts: the index treats completed spec bundles as historical, browse reads Planning branches, and the
namespace reader shares the `[tool.spec]` reader with lifecycle policy.

Hypothesis: a separate document package that knows no delivery process, with SDD and idea incubation built on it,
removes the coupling. A repository can then keep verified devkit documents without SDD, and a new delivery process
plugs in without editing the document layer. No external consumer of devkit-spec exists yet, so the split can
change interfaces in place.

The coupling survey `docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md` lists the seams, a
candidate boundary, the affected records and a size estimate.

## 2. Technical Spike Questions

- **Q1**: Packaging: a new wheel, or a second regular package in devkit-spec's wheel, and the new wheel's version
  policy under `ADR-package-split-and-namespaces` and `ADR-single-release-version`.
- **Q2**: Kind vocabulary: do lifecycle kinds (PROP, SPEC, PLAN, TASKS, REC, FB) stay in the document package's
  kind table, and are milestones document or lifecycle vocabulary?
- **Q3**: Extension points: how the lifecycle supplies the history predicate, unit anchors, the bundle layout and
  list display fields to the document package.
- **Q4**: Configuration: who owns namespaces in `[tool.spec]`, and can two packages contribute to one config
  template?
- **Q5**: Distribution: two bundles or one bundle with two presets, the `auto_select` default and the owner of
  `docs-skeleton`; where the mixed rules (`document_reference`, `spec_format`, `id_convention`) split.
- **Q6**: CLI: one `devkit spec` group composed from both packages, or a separate document group.

## 3. Proposed Design & Impact

- **Document package**: `features/documents` without lifecycle fields and history rule, the document rules,
  entrypoints paths and apply, the namespace reader, document error classes and `resolve`/`refs`/`list`/`search`.
  It depends on devkit-core, devkit-agt and devkit-dist, never on the delivery process.
- **devkit-spec**: proposals, delivery, scope, worker, lifecycle policy and rules, entrypoints derive, the CLI
  composition and the lifecycle assets; it depends on the document package and registers its lifecycle behavior
  through the extension points of Q3.
- Impact: about 7,200 lines move largely unchanged and about twenty seams change; the capabilities, architecture
  pages and ADRs listed in the survey change with them. Repositories that keep SDD see the same behavior.
- Size `XL`: the survey estimates three to four specs. Decompose before Planning; one candidate order is the
  extension points and shared modules first, then the package move, then the bundle split.

## 4. Lifecycle & Retirement Criteria

- Retire with acceptance when the decomposed children are accepted, or reject if idea incubation no longer needs a
  document layer without SDD.
