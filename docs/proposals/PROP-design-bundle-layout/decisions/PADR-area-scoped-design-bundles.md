---
id: PADR-area-scoped-design-bundles
title: Area-scoped design bundles and domain area directories
summary: Formal designs live in area-scoped directory bundles with a design.md anchor and in-bundle support, and domain documents in area directories; IDs stay area-free, and operations stay flat.
proposal: PROP-design-bundle-layout
supersedes: [ADR-formal-role-document-identities]
status: draft
created_at: 2026-11-16
---

# [PADR-area-scoped-design-bundles] Area-scoped design bundles and domain area directories

- **Status**: Draft
- **Date**: 2026-11-16

---

## 1. Context & Problem Statement

`ADR-formal-role-document-identities` placed design, domain and operations documents at flat canonical paths
`<docs-root>/<directory>/<PREFIX>-<slug>.md`, with parent-owned support under a sibling `<ID>/artifacts/`
directory. A design and its support then occupy two sibling paths, and the flat directories offer no write
boundary narrower than every design or every domain document. That decision rejected an area that is part of the
ID, but did not compare the area directory with an area-free ID that use cases and UX documents already use.

## 2. Decision Drivers

- One path holds a design and its support, so a rename, root move or write boundary names one directory.
- A proposal can scope design or domain work by an area path prefix.
- An area move keeps the ID, its aliases and incoming references.
- No registry of area names; the project chooses its areas.
- The rules derive the path grammar from the kind table, not from scattered kind checks.

## 3. Considered Options

1. **Keep the flat grammar.** No migration, but support stays split from its document and no area prefix exists.
2. **Area directory with an area-free ID, design bundle (chosen).** Designs become
   `<docs-root>/designs/<area>/DESIGN-<slug>/design.md` with support beside the anchor; domain documents become
   `<docs-root>/domain/<area>/DOMAIN-<slug>.md` with support under `<ID>/artifacts/` in the area directory.
3. **Area directory without a bundle for designs.** Gives the area prefix, but keeps the split support paths.
4. **Area inside the ID.** Rejected by `ADR-formal-role-document-identities`: an area move would change the ID.

## 4. Decision Outcome

Chosen option 2.

- **Design.** A design is the directory `<docs-root>/designs/<area>/DESIGN-<slug>/` with the anchor `design.md`.
  The directory name is the ID, and the `area` field equals the area directory. Every other file in the bundle is
  parent-owned support: Markdown is ID-free and names its parent, and non-Markdown carries no identity. An
  identified Markdown file inside a bundle is a stray, and a bundle without its anchor is an orphan. Independent
  detail is a peer bundle with its own DESIGN ID; bundles never nest. Support may sit at any depth in the bundle;
  identified Markdown at any depth is a stray, and `README.md` stays exempt.
- **Domain.** A domain document is `<docs-root>/domain/<area>/DOMAIN-<slug>.md` with a matching `area` field. Its
  support stays under `<ID>/artifacts/` in the same area directory.
- **Operations.** Operations documents keep the flat grammar and carry no `area`.
- **Areas.** An area is a directory name the project chooses; validation checks only that the `area` field equals
  the directory.
- **Kind table.** The kind table records each kind's layout (`flat`, `area` or `area-bundle` with its anchor file
  name), from which `area_scoped` derives, and identity, support, frontmatter, entrypoint and search rules read it.

Supersedes in part `ADR-formal-role-document-identities`: the flat canonical path clause and the
`<ID>/artifacts/` support clause for design and domain documents. Its identity, prefix, status, relation,
ownership and entrypoint clauses stay in force.

## 5. Consequences

- Good: a design and its support move, rename and fall under a write boundary as one directory.
- Good: design and domain work can be scoped by an area prefix.
- Good: IDs, aliases and ID references survive an area move; the index and resolution are unchanged.
- Bad: the rules gain layout-aware grammar, support classification and entrypoint eligibility code.
- Bad: this repository's designs, domain documents and lifecycle fixtures migrate once; the viewer
  adopts the grammar in a follow-up.
- Neutral: formal kinds are unreleased and no consumer repository holds flat design or domain documents, so no
  consumer migration path is needed.
- Neutral: an area move edits the `area` field with the path; `devkit rules fix` repairs a stale value.

## 6. Confirmation

Rule tests cover the design bundle, the domain area path, the `area` match, bundle support, a stray identified
document and an anchor-less bundle in the global root and a registered namespace root. The migrated documents pass
`devkit rules check`, and `devkit docs resolve`, `refs` and entrypoint reverse lookup return them under unchanged
IDs.
