---
id: PROP-design-bundle-layout
title: Area-scoped directory bundles for formal design documents
summary: "Moves formal design documents from flat prefixed files to area-scoped directory bundles and places domain documents under area directories, before lifecycle and viewer integration consume the path grammar."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
milestone: MS-documentation-system-evolution
depends_on:
  - SPEC-formal-document-kinds
boundaries:
  owns:
    - packages/devkit-docs/
    - docs/capabilities/documents/
    - docs/capabilities/traceability/
    - docs/capabilities/governance/CAP-GOV-spec-rules.md
    - docs/designs/
    - docs/domain/
    - docs/decisions/
    - docs/README.md
    - docs/proposals/PROP-design-bundle-layout/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/references/migration.md
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py
    - packages/devkit-spec/tests/
    - packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/documents.md
    - packages/devkit-adaptive/tests/
    - .devkit/installation.json
  excludes:
    - packages/devkit-viewer/
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

`SPEC-design-document-lifecycle` has completed on the flat grammar: its spec and adaptive guidance and its
end-to-end scenarios name `<ID>/artifacts/` and flat design and domain paths. `PROP-design-document-viewer` is in
Development and pins the flat grammar in its core contract material, with no viewer code written yet. Each further
delivery on the flat grammar adds migration work, so the grammar change lands now: it migrates the landed lifecycle
consumers itself, and the viewer adopts it after it lands.

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
- **Q4**: Which landed lifecycle consumers in the spec and adaptive bundles, and their tests, assume the flat
  grammar or the stem-is-ID rule, and what is the narrowest edit that makes them grammar-neutral or bundle-aware?

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
- **Decision record.** `PADR-area-scoped-design-bundles` records the layout; at handoff it becomes an ADR that supersedes in part the flat canonical path and `<ID>/artifacts/` support clauses of
  `ADR-formal-role-document-identities` for the kinds this proposal changes. Its identity, status, relation,
  ownership and entrypoint clauses stay in force.
- **Contracts and assets.** Update the path grammar in `CAP-DOCS-document-model`, `CAP-DOCS-documentation-ownership`,
  `CAP-DOCS-namespaces` and `CAP-TRACE-code-entrypoints`, the kind definition rows, the affected rules and their
  tests, `docs/README.md`, and the design and domain templates and writing instructions in the docs bundle. These
  asset edits change path, `area` and support-file statements only.
- **Landed lifecycle consumers.** This proposal updates the spec and adaptive bundle guidance and the lifecycle
  tests that state the flat grammar (Q4). Those edits change path and support-file statements only, not lifecycle
  behavior.
- **Viewer.** `PROP-design-document-viewer` continues its Development on the flat grammar. When this proposal lands,
  it records a follow-up for the viewer to adopt the bundle grammar; the viewer's own unit or a later proposal does
  that work.

### Planning decisions

- **Q1 — kind layout fact, not table rows alone.** `area_scoped` drives only hand-written Living Spec grammar
  entries, and `anchor` is coupled to anchor-derived summaries, so the kind table gains one layout fact per kind
  (`flat`, `area` or `area-bundle` with its anchor file name). `area_scoped` becomes derived from that layout
  (`area` or `area-bundle`), so the table holds one source of truth; the layout anchor is separate from the
  summary `anchor`, so designs keep their summary rule. The table's Living Spec identity definition says the ID is
  the file stem for `flat` and `area` kinds and the bundle directory name for `area-bundle` kinds.
  `RULE-id-convention`, the role support
  classifier, `RULE-spec-format` (the `area` exemption and the derived ID of an anchor), `entrypoint_bearing` and
  the search file-name pin read that fact instead of kind checks. The index, `devkit docs resolve`, `refs`,
  `list --area` and `list --file` key on frontmatter IDs and need no change.
- **Q2 — bundle support.** Inside a design bundle only `design.md` carries an ID. Every other file in the bundle is
  parent-owned support: Markdown stays ID-free and names its parent; non-Markdown needs no identity. An identified
  Markdown file inside a bundle is a stray, reported with a remediation to promote it to a peer bundle. A bundle
  without its anchor is an orphan. Support may sit at any depth below the bundle directory; identified Markdown at
  any depth, including a nested `DESIGN-*/design.md`, is a stray. `README.md` stays exempt everywhere, as today,
  including inside bundles and area directories. Independent detail stays a peer bundle with its own DESIGN ID; bundles never
  nest. Domain support keeps `<ID>/artifacts/` beside the domain file in its area directory.
- **Q3 — moves.** Aliases, `related_*`, canonical references and entrypoint reverse lookup are ID-keyed, so an area
  move keeps them; `area` follows the directory and `devkit rules fix` repairs a stale value but never moves files.
  A move across docs roots changes namespace membership, as today. Bundle anchor file names leave the search
  file-name pin, so `design.md` pins no bundle. Open spec units store literal target paths: the migration rewrites
  any open unit's target that names a moved document in the same commit; completed specs and materials stay as
  written. On the Planning base no open unit targets the moved paths; Development reports one it finds as a
  problem to the Host instead of writing outside its scope.
- **Q4 — landed lifecycle consumers.** Most lifecycle prose is grammar-neutral. Path and "artifact subtree"
  statements change in the spec-sync skill, the adaptive documents reference, the brownfield migration reference
  and the proposal scaffold text. Both composed lifecycle end-to-end scenarios (spec and adaptive) and the
  devkit-spec entrypoint and baseline fixtures are rebuilt on the bundle and area paths; lifecycle behavior does
  not change. The brownfield adoption skill and the spec completion reference mention supporting artifacts
  without a path and stay as written. The work stays one feature spec, so the size rises to L instead of a split.

### Non-Goals

- No change to DESIGN, DOMAIN or OPS identity, prefixes, status vocabulary, `related_*` fields or the ownership
  boundaries between roles.
- No viewer change; the viewer adopts the grammar in a follow-up after this proposal lands.
- No change to lifecycle behavior; only the path and support-file statements of landed lifecycle assets change.
- No area or bundle for operations documents, and no bundle for domain documents.
- No change to template sections or authoring guidance; `PROP-formal-document-templates` owns that alignment and
  follows this proposal.
- No registry or validation of area names beyond the directory and `area` field match.

### Expected acceptance evidence

- **B1 — Grammar**: Positive and negative rule tests cover the design bundle path, the domain area path, the
  `area` match, the anchor file, bundle support files at the top and a nested depth, a stray identified document
  (including a nested bundle), an anchor-less bundle and a bundle `README.md`, in the global root and a registered
  namespace root. A kind-table test proves `area_scoped` follows the layout. `devkit rules fix` derives a bundle
  anchor's ID from its directory and repairs a stale `area` without moving files. `RULE-code-entrypoints` reports
  a dead entrypoint in a bundle design.
- **B2 — Identity preserved**: `devkit docs resolve`, `devkit docs refs`, search, list and `entrypoints` reverse
  lookup return the migrated design and domain documents under unchanged IDs; an area move test keeps the ID and its references. `devkit spec entrypoints derive` accepts a bundle design target, and searching `design.md`
  pins no bundle.
- **B3 — Migration**: The delivered design and domain documents pass `devkit rules check` at their canonical paths with ordinary links repaired.
- **B4 — Contracts**: The superseding ADR, the capability documents, templates and instructions, and the landed
  spec and adaptive lifecycle assets state one path grammar per kind; the lifecycle end-to-end scenarios pass on it.
  A search of the owned contract and asset paths for a flat design path or a design-scoped `<ID>/artifacts/`
  returns only domain and operations statements and historical records.
- **B5 — Viewer follow-up**: A recorded follow-up names the viewer's flat-grammar pins, including its
  delivered-core reconcile clause and support-layout statements in its target documents, and the bundle grammar to
  adopt; until then the viewer tests against synthetic fixtures rather than this repository's moved documents.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q4 and records the layout choice as a PADR. This stays one L feature proposal: the layout
code, migration and lifecycle fixtures form one change with one task kind. Acceptance
and handoff follow the existing gates. It runs in parallel with the viewer's Development. Retirement requires
B1–B5.
