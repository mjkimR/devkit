---
id: PROP-table-driven-document-kinds
title: Table-driven document kind definitions
summary: "Moves each document kind's prefix, location, Living Spec membership and relation fields into one definition table that the index, the spec rules and browsing read, so a new kind is added in one place without changing current behavior."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-ux-documentation
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/
    - packages/devkit-spec/tests/
    - packages/devkit-viewer/src/devkit_viewer/features/browse/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/tests/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/architecture/
  excludes:
    - New document kinds
    - A plug-in or configuration extension point for document kinds
    - Changes to document IDs, paths, rule codes or messages
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-table-driven-document-kinds] Table-driven document kind definitions

## 1. Background & Hypothesis

A document's kind follows from its ID prefix (`CAP-DOCS-document-model` section 3.2). The facts that make up a kind
are not kept together:

- `features/documents/models/ids.py` defines the closed `Kind` enum and the `PREFIXES` map that builds the ID
  pattern.
- `features/governance/usecases/id_convention.py` repeats which kinds form the Living Spec (`_LIVING_SPEC`), which
  directory holds which kind (`_LIVING_DIRECTORIES`), and the path and ID rule of each kind in its own branch. Some
  branches assume a fixed set, for example choosing `usecases` when a kind is a use case and `capabilities`
  otherwise.
- The relation fields and the kind each accepts (`usecases` takes `UC`, `capabilities` takes `CAP`, `milestone`
  takes `MS`) live in the reference rule; summary, entrypoint, scope, hygiene, roadmap and browsing code test kinds
  in further places, and the viewer front end keeps its own knowledge of the Living Spec directories.

Adding a kind therefore means finding every such place by search. A missed branch does not fail: a fallback such as
"not a use case, so a capability" silently gives the new kind the wrong directory or rule. The UX document kind of
`MS-ux-documentation` is the first kind this would affect, and it would not be the last.

Hypothesis: one definition table per kind (prefix, kind name, location pattern, Living Spec directory, Living Spec
membership, the relation fields it declares and accepts, summary requirement, template) can be read by the index,
the spec rules, browsing and the viewer. Adding a kind then means adding a row and its template, while the
lifecycle behavior that really is kind-specific (spec lifecycle, proposal handoff, feedback lifecycle, milestone
hygiene) stays in code. The change is a refactor: every current output stays identical.

## 2. Technical Spike Questions

- **Q1**: Which per-kind facts are data that belongs in the table, and which are behavior that stays kind-specific
  code? List every current kind test (`Kind.` and `kind_of` uses across devkit-spec) and classify each.
- **Q2**: Where does the table live so that models, services and the governance rules read it without breaking the
  layer direction (models never import higher layers)?
- **Q3**: How does the viewer obtain the same definitions: served by the Python side, generated into the front end,
  or kept as a checked copy? Which choice keeps the committed front-end build in step?
- **Q4**: How is "no behavior change" shown: the existing test suites unchanged, plus identical `devkit rules check`,
  `devkit spec list` and search output on this repository before and after?

## 3. Proposed Design & Impact

- A kind definition table in the documents feature replaces the scattered constants; `Kind` and `PREFIXES` are
  derived from it, and `kind_of`, `is_id` and the ID pattern keep their signatures.
- Consumers read directories, membership and relation-field kinds from the table instead of repeating them; binary
  fallbacks between kinds are removed.
- A test adds a synthetic kind row and shows that indexing, ID convention and reference checks treat it correctly
  with no other code change.
- `CAP-DOCS-document-model` states that the table is the single definition of kinds; no document, ID, path, rule
  code or message changes.
- Non-goals: no new kind (the UX kind is a separate proposal of `MS-ux-documentation`), no plug-in or
  configuration extension point, no change to the closed set of kinds a repository can use.

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-table-driven-document-kinds`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
