---
id: PROP-design-bundle-layout
title: Area-scoped directory bundles for formal design documents
summary: "Moves formal design documents from flat prefixed files to area-scoped directory bundles and settles grouping for domain documents, before lifecycle and viewer integration consume the path grammar."
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
would change the ID. It did not compare the layout use cases and UX documents use: an area directory with a matching
`area` field and an area-free ID.

Hypothesis: an area-scoped directory bundle gives each design one path for the document and its support, and gives
delivery work an area prefix, without changing design identity, references or the ownership model.

`PROP-design-document-lifecycle` and `PROP-design-document-viewer` are accepted and pin the flat grammar in their
blueprints. Neither has a spec. A path grammar change after their Development would require migrating the rules,
the lifecycle tooling, the viewer and every consumer repository; before it, the change touches the rules and five
documents.

## 2. Technical Spike Questions

- **Q1**: Does the kind definition table's existing `area_scoped` and `anchor` facts carry the design grammar in
  `RULE-id-convention`, `RULE-spec-format`, the index and `devkit docs resolve`, or does the bundle need
  kind-specific path code? Which consumers assume the file stem is the ID for these kinds?
- **Q2**: Is the design `area` vocabulary the capability area set, or a free directory name as for use cases? Which
  area owns a design that explains a mechanism spanning two capability areas?
- **Q3**: Which Markdown may live inside a design bundle beside `design.md`? The delivered rule keeps
  parent-owned support ID-free and unindexed, and gives independently findable detail its own DESIGN ID. Does the
  bundle keep that rule with the `artifacts/` level removed, and how does identity governance tell support from a
  stray identified document?
- **Q4**: Do domain documents take an area directory as well? Compare the flat layout, a required area directory
  with a matching `area` field, and an optional single grouping level, against documents that relate concepts of
  several areas, expected catalog growth in consumer repositories and the cost of changing the grammar after a
  release. Operations documents stay flat.
- **Q5**: How do pins, aliases, namespace roots and `entrypoints` reverse lookup behave when a design moves between
  areas or docs roots while keeping its ID?
- **Q6**: Who updates the flat-grammar pins of `PROP-design-document-lifecycle` and `PROP-design-document-viewer`,
  and do both proposals take a prerequisite edge to this proposal before their handoff?
- **Q7**: Do the design, domain and operations templates change in this proposal? The five delivered documents
  follow none of the templates' numbered sections, no rule checks sections, the templates carry no authority
  boundary section although `CAP-DOCS-documentation-ownership` §3.3 asks for one, and their guidance is body prose
  rather than comments.

## 3. Proposed Design & Impact

- **Design path.** A design is the directory `<docs-root>/designs/<area>/DESIGN-<slug>/` with the anchor file
  `design.md`. The directory name is the ID. The `area` field matches the area directory. The ID carries no area,
  so an area move changes the path and keeps the ID, aliases and incoming references.
- **Design support.** Parent-owned support files live in the bundle beside `design.md`; the `artifacts/` level is
  removed for designs. Supporting Markdown stays ID-free and names its parent. Independently findable detail keeps
  its own DESIGN ID and bundle.
- **Domain and operations.** Operations documents keep the flat file grammar. Domain documents follow the outcome
  of Q4.
- **Migration.** Move `DESIGN-distribution-transactions` and `DESIGN-distribution-file-directory-replacement` into
  bundles under the `distribution` area and repair ordinary links. Move domain documents when Q4 selects grouping.
  IDs do not change, so ID references need no rewrite.
- **Decision record.** A new ADR supersedes in part the flat canonical path clause of
  `ADR-formal-role-document-identities` for the kinds this proposal changes. Its identity, status, relation,
  ownership and entrypoint clauses stay in force.
- **Contracts and assets.** Update the path grammar in `CAP-DOCS-document-model`, `CAP-DOCS-documentation-ownership`,
  `CAP-DOCS-namespaces` and `CAP-TRACE-code-entrypoints`, the kind definition rows, the affected rules and their
  tests, `docs/README.md`, and the design template and writing instruction in the docs bundle. Template alignment
  for all three kinds follows Q7.
- **Dependent proposals.** `PROP-design-document-lifecycle` and `PROP-design-document-viewer` consume the grammar
  this proposal delivers; Q6 settles how their pins change.

### Non-Goals

- No change to DESIGN, DOMAIN or OPS identity, prefixes, status vocabulary, `related_*` fields or the ownership
  boundaries between roles.
- No viewer or lifecycle implementation; those stay with their proposals.
- No area or bundle for operations documents.

### Expected acceptance evidence

- **B1 — Grammar**: Positive and negative rule tests cover the design bundle path, the `area` match, the anchor
  file, bundle support files and a stray identified document, in the global root and a registered namespace root.
- **B2 — Identity preserved**: `devkit docs resolve`, `devkit docs refs`, search, list and `entrypoints` reverse
  lookup return the migrated designs under unchanged IDs; an area move test keeps the ID and its references.
- **B3 — Migration**: The delivered design documents, and the domain documents when Q4 selects grouping, pass
  `devkit rules check` at their canonical paths with ordinary links repaired.
- **B4 — Contracts**: The superseding ADR, the capability documents, templates and instructions state one path
  grammar per kind, and the dependent proposals' pins agree with it.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q7 and records the layout choice as a PADR. This stays one M feature proposal. Acceptance and
handoff follow the existing gates, and handoff precedes the handoff of `PROP-design-document-lifecycle` and
`PROP-design-document-viewer`. Retirement requires B1–B4.
