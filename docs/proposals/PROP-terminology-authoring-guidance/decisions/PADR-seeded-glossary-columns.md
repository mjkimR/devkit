---
id: PADR-seeded-glossary-columns
title: Seeded glossary columns
summary: "Fixes the seeded glossary table to Term, Definition, Owner, Avoid and Code identifiers, with exclusions written in the definition, Avoid entries mirrored as search synonyms and a remarks fallback for older glossaries."
proposal: PROP-terminology-authoring-guidance
status: draft
created_at: 2026-10-19
---

# [PADR-seeded-glossary-columns] Seeded glossary columns

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

The seeded `docs/glossary.md` table (`Term | English / Abbr | Definition & Description | Relevant Area | Remarks`) has no
place for the fields the terminology rules use: owner (rules 4 and 7), exclusions (rule 7), rejected synonyms (rule 3)
and code identifiers (rule 6). The proposal must fix the column set (spike Q3), the relation of `Avoid` to the search
synonyms of `docs/glossary.yaml` (Q4) and what projects with an older glossary do (Q5).

## 2. Decision Drivers

- A narrow table stays readable in Markdown; devkit-spec's own glossary already works with three columns
  (`Term | Definition | Defined in`).
- `devkit spec search` expands queries with the `glossary.yaml` synonym clusters (`CAP-DOCS-document-search`): a
  rejected synonym should still lead to the registered term.
- A seeded glossary is project-owned after seeding (`ADR-docs-skeleton-is-opt-in`); the bundle cannot migrate it.

## 3. Considered Options

- **Q3-A. Six columns**: `Term | Definition | Owner | Distinct from / Excludes | Avoid | Code identifiers`.
- **Q3-B. Five columns**: `Term | Definition | Owner | Avoid | Code identifiers`, with exclusions and adjacent terms
  written in the definition.
- **Q4**: an Avoid entry is only a table cell, or it is also added as a synonym of the term's cluster in
  `docs/glossary.yaml` (one line of guidance), or the two files are generated from each other (a Non-Goal).
- **Q5**: no fallback, or a one-line fallback for glossaries without the new columns.

## 4. Decision Outcome

- **Q3: Option Q3-B.** The seeded table is `| Term | Definition | Owner | Avoid | Code identifiers |`. The definition
  states what the term excludes and which adjacent term it is distinct from when confusion is likely. `Owner` is the
  defining document ID (`CAP-...`, `ADR-...`) or the owning component. An original-language rendering goes in the
  `Term` cell (`기능 원장 (Living Spec)`), replacing the `English / Abbr` column. Empty `Avoid` and `Code identifiers`
  cells are allowed. The two existing authoring guidelines are removed and replaced by a one-line pointer to the
  `living-spec-writing` instruction.
- **Q4: one line of guidance.** Where `docs/glossary.yaml` exists, an Avoid entry is also added as a synonym of the
  term's cluster. No generation or synchronisation between the files.
- **Q5: one-line fallback.** A glossary without these columns records owner, exclusions and avoided synonyms in its
  existing remarks or definition cells; the guidance does not require migrating a project-owned glossary.
- devkit-spec's own `docs/glossary.md` migrates to the five columns: `Defined in` becomes `Owner`, and `Avoid` and
  `Code identifiers` are added, filled where a rejected synonym or an identifier is known.

## 5. Consequences

- `CAP-HARN-agent-guidance` section 4.7 describes the five seeded columns and the project section for avoided generic
  nouns.
- Exclusions have no column of their own, so a reviewer checks them in the definition text.
- The seeded `glossary.yaml` comment already asks for searched abbreviations and translations; the Avoid line extends
  that practice without a schema change.
