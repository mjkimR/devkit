---
id: PROP-design-bundle-layout
title: Area-scoped directory bundles for formal design documents
summary: "Moves formal design documents from flat prefixed files to area-scoped directory bundles and places domain documents under area directories, before lifecycle and viewer integration consume the path grammar."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-documentation-system-evolution
depends_on:
  - SPEC-formal-document-kinds
boundaries:
  owns:
    - packages/devkit-docs/
    - docs/capabilities/documents/
    - docs/capabilities/traceability/
    - docs/designs/
    - docs/domain/
    - docs/decisions/
    - docs/README.md
    - docs/proposals/PROP-design-bundle-layout/
  excludes:
    - packages/devkit-viewer/
    - packages/devkit-spec/
    - packages/devkit-adaptive/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-design-bundle-layout] Area-scoped directory bundles for formal design documents

## 1. Background & Hypothesis

`SPEC-formal-document-kinds` delivered design, domain and operations as formal kinds with one shared path grammar:
a flat file `<docs-root>/<directory>/<PREFIX>-<slug>.md`, with parent-owned support under a sibling
`<ID>/artifacts/` directory. `ADR-formal-role-document-identities` selected that layout and named the condition for
revisiting it: a durable organization need that title, summary, search and `related_*` links cannot express.

Three observations on the delivered state motivate revisiting the layout for design documents:

- **Split document and support.** A design and its support occupy two sibling paths, `DESIGN-<slug>.md` and
  `DESIGN-<slug>/artifacts/`. A rename, a root move and a write boundary each name both. Worked examples and
  datasheets are part of the design role, so support files are an expected part of a design, not an exception.
- **No area-scoped write boundary.** A proposal's `boundaries.owns` scopes work by path prefix, such as
  `docs/capabilities/delivery/`. The flat `docs/designs/` directory offers no prefix narrower than every design.
- **A design has a home area.** A design explains the mechanism behind a capability's guarantees and declares
  `entrypoints` into one implementation. Both delivered designs carry the area in their slug
  (`DESIGN-distribution-transactions`, `DESIGN-distribution-file-directory-replacement`).

`ADR-formal-role-document-identities` rejected an area option whose area is part of the ID, because an area move
would change the ID, and because no exclusive area taxonomy exists for these roles. It did not compare the layout
use cases and UX documents use: an area directory with a matching `area` field and an area-free ID. In that layout
an area is the parent directory's name, not a member of a registered set: `RULE-id-convention` checks only that the
`area` field equals the directory. A document relating concepts of several areas takes an area name of its own, so
no assignment to an existing area is forced.

Domain documents have the same grouping need. A domain catalog grows with the concept clusters of a project, and
consumer repositories with a large business domain group models by bounded context. An area directory lets each
project name those groups itself.

Hypothesis: an area-scoped directory bundle gives each design one path for the document and its support, and gives
delivery work an area prefix, without changing design identity, references or the ownership model.

`PROP-design-document-lifecycle` and `PROP-design-document-viewer` are accepted and pin the flat grammar in their
blueprints. Neither has a spec. A path grammar change after their Development would require migrating the rules,
the lifecycle tooling, the viewer and every consumer repository; before it, the change touches the rules and five
documents.

## 2. Technical Spike Questions

- **Q1**: Do the kind definition table's existing `area_scoped` and `anchor` facts carry the design grammar in
  `RULE-id-convention`, `RULE-spec-format`, the index and `devkit docs resolve`, or does the bundle need
  kind-specific path code? Which consumers assume the file stem is the ID for these kinds?
- **Q2**: Which Markdown may live inside a design bundle beside `design.md`? The delivered rule keeps
  parent-owned support ID-free and unindexed, and gives independently findable detail its own DESIGN ID. Does the
  bundle keep that rule with the `artifacts/` level removed, and how does identity governance tell support from a
  stray identified document?
- **Q3**: How do pins, aliases, namespace roots and `entrypoints` reverse lookup behave when a design or domain
  document moves between areas or docs roots while keeping its ID?
- **Q4**: Who updates the flat-grammar pins of `PROP-design-document-lifecycle` and `PROP-design-document-viewer`,
  and do both proposals take a prerequisite edge to this proposal before their handoff?

## 3. Proposed Design & Impact

- **Design path.** A design is the directory `<docs-root>/designs/<area>/DESIGN-<slug>/` with the anchor file
  `design.md`. The directory name is the ID. The `area` field matches the area directory. The ID carries no area,
  so an area move changes the path and keeps the ID, aliases and incoming references.
- **Area names.** An area is a directory name the project chooses, as for use cases and UX documents. No registry
  lists valid areas, and design and domain areas need not equal a capability area.
- **Design support.** Parent-owned support files live in the bundle beside `design.md`; the `artifacts/` level is
  removed for designs. Supporting Markdown stays ID-free and names its parent. Independently findable detail keeps
  its own DESIGN ID and bundle.
- **Domain path.** A domain document is the file `<docs-root>/domain/<area>/DOMAIN-<slug>.md` with a matching
  `area` field and an area-free ID. Its parent-owned support keeps the sibling `<ID>/artifacts/` directory inside
  the area directory.
- **Operations.** Operations documents keep the flat file grammar.
- **Migration.** Move `DESIGN-distribution-transactions` and `DESIGN-distribution-file-directory-replacement` into
  bundles under the `distribution` area. Move `DOMAIN-bundle-selection-and-installation` under `distribution` and
  `DOMAIN-delivery-relationships` under `delivery`. Repair ordinary links. IDs do not change, so ID references need
  no rewrite.
- **Decision record.** A new ADR supersedes in part the flat canonical path clause of
  `ADR-formal-role-document-identities` for the kinds this proposal changes. Its identity, status, relation,
  ownership and entrypoint clauses stay in force.
- **Contracts and assets.** Update the path grammar in `CAP-DOCS-document-model`, `CAP-DOCS-documentation-ownership`,
  `CAP-DOCS-namespaces` and `CAP-TRACE-code-entrypoints`, the kind definition rows, the affected rules and their
  tests, `docs/README.md`, and the design and domain templates and writing instructions in the docs bundle. These
  asset edits change path, `area` and support-file statements only.
- **Dependent proposals.** `PROP-design-document-lifecycle` and `PROP-design-document-viewer` consume the grammar
  this proposal delivers; Q4 settles how their pins change.

### Non-Goals

- No change to DESIGN, DOMAIN or OPS identity, prefixes, status vocabulary, `related_*` fields or the ownership
  boundaries between roles.
- No viewer or lifecycle implementation; those stay with their proposals.
- No area or bundle for operations documents, and no bundle for domain documents.
- No change to template sections or authoring guidance; `PROP-formal-document-templates` owns that alignment and
  follows this proposal.
- No registry or validation of area names beyond the directory and `area` field match.

### Expected acceptance evidence

- **B1 — Grammar**: Positive and negative rule tests cover the design bundle path, the domain area path, the
  `area` match, the anchor file, bundle support files and a stray identified document, in the global root and a
  registered namespace root.
- **B2 — Identity preserved**: `devkit docs resolve`, `devkit docs refs`, search, list and `entrypoints` reverse
  lookup return the migrated design and domain documents under unchanged IDs; an area move test keeps the ID and its references.
- **B3 — Migration**: The delivered design and domain documents pass `devkit rules check` at their canonical paths with ordinary links repaired.
- **B4 — Contracts**: The superseding ADR, the capability documents, templates and instructions state one path
  grammar per kind, and the dependent proposals' pins agree with it.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q4 and records the layout choice as a PADR. This stays one M feature proposal. Acceptance and
handoff follow the existing gates, and handoff precedes the handoff of `PROP-design-document-lifecycle` and
`PROP-design-document-viewer`. Retirement requires B1–B4.
