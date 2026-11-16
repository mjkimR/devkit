---
id: FB-viewer-adopts-bundle-grammar
title: The formal document viewer adopts the design bundle and domain area grammar
scope: repo
kind: change-request
category: docs-mismatch
target: PROP-design-document-viewer
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-viewer-adopts-bundle-grammar] The formal document viewer adopts the design bundle and domain area grammar

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `SPEC-design-document-viewer` plans against the flat formal-role grammar that
  `ADR-formal-role-document-identities` selected: every design, domain and operations document is a flat file
  `<root>/<directory>/<PREFIX>-<slug>.md` with no `area` field, and parent-owned support lives under a sibling
  `<root>/<directory>/<PARENT-ID>/artifacts/`. The flat grammar is pinned in these places:
  - `PROP-design-document-viewer-target` section 2 "Core interface and sequencing": the kind table rows
    `<root>/designs/DESIGN-<word-led-slug>.md` and `<root>/domain/DOMAIN-<word-led-slug>.md`; the statement that
    H1 and stem match the ID and that formal roles carry no `area` field; the support paragraph that places
    artifacts under `<root>/<role-directory>/<PARENT-ID>/artifacts/<relative-path>` and calls independent details
    flat peer files; and the maintenance paragraph that moves `<OLD-ID>/artifacts/` to `<NEW-ID>/artifacts/` on a
    rename and carries that subtree on a docs-root move.
  - The same section's delivered-core reconcile clause: Development consumes the delivered core implementation and
    reconciles any material difference before dependent verification. The pinned core contract (source commit
    `504e2e1`, content SHA-256 `1d724834…`) predates this grammar, so that reconcile is now a known, material
    difference rather than a hypothetical one.
  - The proposal's `materials/core-contract.md`: section 1 "Kind, identity and location" (one flat identity grammar
    for all three kinds), section 3 "Content ownership and independent detail" (`<PARENT-ID>/artifacts/` storage,
    the artifact path classification and the rename and root-move subtree rules), section 7 "Migration identities"
    (the four migrated documents at flat paths) and section 8 "Formal alternatives and enforcement allocation" (the
    selected flat role root and the rejected grouped roots).
  - The proposal's `materials/support-matrix.md`: the "Inspection and provenance" summary ("flat prefixed peer
    files"; "Artifacts use <role>/<PARENT-ID>/artifacts/<relative>") and the core pin it records, which the matrix
    rows, the "Artifact implementation refinement" section and the "Required Development validation" fixtures
    inherit.
  - The target's supporting-artifact screen draft and formal-document reading flow draft (section 5 "Screens"), as
    far as they locate a supporting file by an `artifacts/` subtree.
- **Proposed Procedure**: Adopt the grammar `ADR-area-scoped-design-bundles` records and `CAP-DOCS-document-model`
  now states, in the viewer's own Development unit or a follow-up proposal:
  - **Design**: the directory `<root>/designs/<area>/DESIGN-<slug>/` with the anchor `design.md`. The directory
    name is the ID, and the `area` field equals the area directory. Every other file in the bundle, at any depth,
    is parent-owned support: Markdown is ID-free and names its parent, non-Markdown carries no identity. Identified
    Markdown in a bundle is a stray (invalid core input), a bundle without `design.md` is an orphan, independent
    detail is a peer bundle, and bundles never nest. `README.md` stays exempt.
  - **Domain**: the file `<root>/domain/<area>/DOMAIN-<slug>.md` with a matching `area` field; support stays under
    `<ID>/artifacts/` beside it in the same area directory.
  - **Operations**: unchanged; flat `<root>/operations/OPS-<slug>.md`, no `area`, support under `<ID>/artifacts/`.
  - **Moves**: an area move changes the path and `area` and keeps the ID, aliases and incoming references; a design
    rename or root move carries the whole bundle; a move across docs roots changes namespace membership.
  - **Navigation**: the viewer groups designs and domain documents by area where it lists them, labels a bundle
    by its ID rather than the shared `design.md` file name, and lists a bundle's support files from the bundle
    directory rather than an `artifacts/` subtree.
  - Until the adoption lands, viewer tests use synthetic fixtures for formal documents instead of this repository's
    migrated documents, whose paths now follow the bundle and area grammar.
- **Expected Benefit**: The viewer consumes the grammar the rules enforce, so its supporting-file view, kind counts
  and reference graph match `devkit docs` output, and the delivered-core reconcile has a named target instead of a
  discovered mismatch.
- **Cost & Risk**: The target blueprint, the two materials and the dependent UX and UC drafts change, and the viewer
  core pin is refreshed against the delivered rules. A viewer that keeps flat-path assumptions misses support files
  inside bundles, shows `design.md` as a node label, or treats a design bundle's support Markdown as an orphan.
- **Attempted**: Hypothesis. The viewer source hardcodes no formal path (`SPEC-design-bundle-layout` Planning
  scout evidence); only the proposal documents above pin the grammar. Line numbers are not cited because the proposal on
  main may differ from its Development branch.

## Diagnostic Details

- **Reproduction**: Search `SPEC-design-document-viewer` and its materials for `DESIGN-<word-led-slug>.md`,
  `DOMAIN-<word-led-slug>.md`, `<PARENT-ID>/artifacts/` and "flat".
- **Expected / Actual**: Expected the viewer contract to state the bundle and area grammar; it states the flat
  grammar of `ADR-formal-role-document-identities`.
- **Versions**: `SPEC-design-bundle-layout` Development branch, 2026-11-16; viewer core pin source commit `504e2e1`.
- **Conditions**: `SPEC-design-document-viewer` is in Development with no viewer code written for formal kinds;
  `SPEC-design-bundle-layout` lands the grammar change and migrates `DESIGN-distribution-transactions`,
  `DESIGN-distribution-file-directory-replacement`, `DOMAIN-bundle-selection-and-installation` and
  `DOMAIN-delivery-relationships` under unchanged IDs.
- **Workarounds Attempted**: not attempted; `SPEC-design-bundle-layout` excludes viewer changes.
- **Related Assets**: `ADR-area-scoped-design-bundles`, `ADR-formal-role-document-identities`,
  `CAP-DOCS-document-model`, `CAP-DOCS-documentation-ownership`, `CAP-DOCS-namespaces`, `CAP-TRACE-code-entrypoints`,
  `SPEC-design-document-viewer`, `PROP-design-document-viewer-target`, `SPEC-design-bundle-layout` (AC-07).

## Evidence

```text
PROP-design-document-viewer-target §2 kind table:
  design / DESIGN / designs | <root>/designs/DESIGN-<word-led-slug>.md
  domain / DOMAIN / domain  | <root>/domain/DOMAIN-<word-led-slug>.md
PROP-design-document-viewer-target §2: "H1 and stem match ID; no area field."
PROP-design-document-viewer-target §2: "Artifacts live under <root>/<role-directory>/<PARENT-ID>/artifacts/<relative-path>"
PROP-design-document-viewer-target §2: "Development must consume the delivered core implementation and reconcile any
  material difference before dependent verification."
materials/core-contract.md §3: "Store it under <root>/<directory>/<PARENT-ID>/artifacts/<relative-path>"
materials/support-matrix.md "Inspection and provenance": "flat prefixed peer files ... Artifacts use
  <role>/<PARENT-ID>/artifacts/<relative>"
Migrated paths on this branch: docs/designs/distribution/DESIGN-distribution-transactions/design.md,
  docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md,
  docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md,
  docs/domain/delivery/DOMAIN-delivery-relationships.md
```
