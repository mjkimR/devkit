---
id: PLAN-design-bundle-layout
spec: SPEC-design-bundle-layout
---

# Technical Plan: `SPEC-design-bundle-layout` Area-scoped directory bundles for formal design documents

## 1. Constitution & Invariant Review

`ADR-area-scoped-design-bundles` supersedes in part the flat canonical path and `<ID>/artifacts/` support clauses of
`ADR-formal-role-document-identities` for DESIGN and DOMAIN; identity, relation, ownership and entrypoint clauses
stay. `ARCH-05-2-components` is unchanged: the work stays in the existing devkit-docs `documents` and `governance`
features and the existing devkit-spec entrypoint edge to devkit-docs. No new feature, layer, edge or test tier.

## 2. Architecture Overview & Impact

- Target Area: documents/
- The kind table (`devkit_docs.features.documents.models.kinds`) gains one layout fact per kind: `flat`, `area` or
  `area-bundle` with an anchor file name. `area_scoped` becomes a derived property; the summary `anchor` keeps its
  current meaning and coupling.
- Governance consumers read the layout instead of kind checks: `id_convention` (grammar, directory walk, binary
  support scan, orphan and stray reports), `role_artifacts` (support classification and parent lookup),
  `spec_format` (`area` exemption from `area_scoped`, anchor-derived ID and title for bundle anchors),
  `entrypoint_paths` (bundle-aware `entrypoint_bearing`) and `search` (bundle anchor names leave the file-name pin).
- The index, `resolve`, `refs`, `list` and alias handling are ID-keyed and stay unchanged.

## 3. Component & Interface Design

- Grammar: DESIGN `<root>/designs/<area>/DESIGN-<slug>/design.md`; DOMAIN `<root>/domain/<area>/DOMAIN-<slug>.md`;
  OPS `<root>/operations/OPS-<slug>.md`. `<root>` is the global docs root or a registered namespace root.
- Support: in a design bundle every non-anchor file at any depth is support; Markdown is ID-free and names its
  parent. Identified Markdown at any depth is a stray; a bundle directory without `design.md` is an orphan.
  DOMAIN and OPS keep `<ID>/artifacts/`, beside the document in its directory.
- `README.md` stays exempt everywhere.
- CLI flags, result codes and JSON shapes stay unchanged; new rule findings reuse the rules' existing reporting
  path with stable codes.

## 4. Migration

Move `DESIGN-distribution-transactions` and `DESIGN-distribution-file-directory-replacement` to
`docs/designs/distribution/<ID>/design.md`, `DOMAIN-bundle-selection-and-installation` to `docs/domain/distribution/`
and `DOMAIN-delivery-relationships` to `docs/domain/delivery/`, add `area`, and repair the one outbound relative
link. IDs do not change, so ID references need no rewrite. No open unit targets the moved paths.

## 5. Error Handling & Edge Cases

Nested support, nested bundles, anchor-less bundles, README in bundles and area directories, blank `id` on an
anchor, stale `area` after an area move, cross-root moves (namespace membership changes as today), and a search for
the anchor file name.

## 6. Verification & Test Plan

- Unit and rule tests in devkit-docs for AC-01 to AC-04 (kind table, `id_convention`, `spec_format`,
  `code_entrypoints` rule tests, search).
- Integration tests in devkit-docs for AC-05 (formal kinds, area move), devkit-spec entrypoint integration test for
  derive on a bundle design.
- devkit-spec and adaptive lifecycle end-to-end scenarios rebuilt on bundle and area paths (AC-06).
- `uv run devkit rules check`, lint, type checks and `just test-affected`; the AC-06 search over owned contract and
  asset paths.
