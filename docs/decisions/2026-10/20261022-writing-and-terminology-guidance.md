---
id: ADR-writing-and-terminology-guidance
title: Writing and terminology guidance
summary: "For agent-read documents and glossaries, we layer writing guidance into a common instruction, one per document kind and a self-contained authoring one, keep terminology in living-spec-writing and fix five seeded glossary columns, to keep triggers precise, accepting more headers per spec context."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-seeded-glossary-columns
  - ADR-terminology-guidance-lives-in-living-spec-writing
  - ADR-layered-writing-guidance
---

# [ADR-writing-and-terminology-guidance] Writing and terminology guidance

- **Status**: Accepted
- **Date**: 2026-10-22
- **Involved Components/Capabilities**: `CAP-HARN-agent-guidance`, `CAP-DOCS-document-search`,
  `ARCH-08-2-resource-taxonomy`

---

## 1. Context & Problem Statement

Eight terminology rules ship as bundle instruction text. Their place had to be decided (where the text lives, where
the list of bare generic nouns lives, whether its size is bounded); the text is read before most documentation work, so
every added line is paid in context by many sessions. The seeded `docs/glossary.md` table
(`Term | English / Abbr | Definition & Description | Relevant Area | Remarks`) had no place for the fields the
terminology rules use: owner (rules 4 and 7), exclusions (rule 7), rejected synonyms (rule 3) and code identifiers
(rule 6); the column set, the relation of `Avoid` to the search synonyms of `docs/glossary.yaml` and the handling of
older glossaries had to be fixed.

Beyond terminology, skills, playbooks and instructions stack a condition, an action, an exception and a
cross-reference in one sentence. The `skill-authoring` playbook covers structure and size but not sentence-level
writing. Living Spec documents have templates but no type-specific patterns. `contract-authoring` and
`living-spec-writing` mix general writing rules with placement policy. Anthropic's skill authoring and prompting
guidance is the agreed baseline.

---

## 2. Decision Drivers

- The trigger: guidance must be read at the moment it applies; terminology guidance when a document names or registers
  a term, and an agent writing an ADR should not read the story or architecture patterns.
- Context budget: `devkit get-context spec` returns every instruction header to every development session, and the
  constitution tells every session to read the relevant instruction bodies.
- Projects differ in which nouns are overloaded; the bundle cannot know a project's domain.
- A narrow table stays readable in Markdown; devkit-spec's own glossary already worked with three columns
  (`Term | Definition | Defined in`).
- `devkit spec search` expands queries with the `glossary.yaml` synonym clusters (`CAP-DOCS-document-search`): a
  rejected synonym should still lead to the registered term.
- A seeded glossary is project-owned after seeding (`ADR-spec-package-on-devkit`); the bundle cannot migrate it.
- Asset boundaries: criteria are instructions, procedures are playbooks (`ARCH-08-2-resource-taxonomy`); `authoring`
  is opt-in and never depends on `spec`.

---

## 3. Considered Options

### Where terminology guidance lives
- **Fold into `living-spec-writing`** (selected by `ADR-terminology-guidance-lives-in-living-spec-writing`): extend its
  `## Glossary` section and widen its description; that instruction is already read before any `docs/` or `specs/`
  edit.
- **New `terminology` instruction** (rejected by `ADR-terminology-guidance-lives-in-living-spec-writing`): its own
  header and trigger, at the cost of a third instruction header in every `get-context` result and a second body to read
  before documentation work.

### Generic-noun list
- In the instruction only, or in the glossary only (rejected by
  `ADR-terminology-guidance-lives-in-living-spec-writing`); **a short default in the instruction plus project additions
  and exceptions in `docs/glossary.md`** (selected).

### Size bound
- No bound (rejected by `ADR-terminology-guidance-lives-in-living-spec-writing`); **a bound on added lines as an
  acceptance criterion** (selected).

### Glossary columns
- **Six columns** `Term | Definition | Owner | Distinct from / Excludes | Avoid | Code identifiers` (rejected by
  `ADR-seeded-glossary-columns`).
- **Five columns** `Term | Definition | Owner | Avoid | Code identifiers`, exclusions and adjacent terms written in the
  definition (selected by `ADR-seeded-glossary-columns`).

### Avoid and search synonyms
- An Avoid entry only as a table cell (rejected by `ADR-seeded-glossary-columns`); **also added as a synonym of the
  term's cluster in `docs/glossary.yaml`, one line of guidance** (selected); the two files generated from each other (a
  Non-Goal, rejected).

### Older glossaries
- No fallback (rejected by `ADR-seeded-glossary-columns`); **a one-line fallback** (selected).

### Writing guidance structure
- **One common instruction with per-type sections** (rejected by `ADR-layered-writing-guidance`): one header; every
  document write reads all type sections.
- **Common instruction plus one instruction per kind** (selected by `ADR-layered-writing-guidance`): five headers (about
  250 tokens per spec context); each type section is read only for its kind.
- **Per-type rules in templates only** (rejected by `ADR-layered-writing-guidance`): templates are read only when a
  document is created, not edited, and `docs/architecture/` has no template.

---

## 4. Decision Outcome

- **Terminology in `living-spec-writing`**: the terminology guidance is the body of the `## Glossary` section of the
  `living-spec-writing` instruction (`packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md`
  at decision time); the instruction's `description` names terminology and the glossary so the header announces it. The
  existing package-glossary sentence stays in the section. The Glossary stays in `living-spec-writing`.
  (ADR-terminology-guidance-lives-in-living-spec-writing, ADR-layered-writing-guidance)
- **Generic nouns**: the instruction lists a short default of bare generic nouns (rule 1); the seeded
  `docs/glossary.md` carries a project section for additional avoided generic nouns and exceptions, which the
  instruction points to. (ADR-terminology-guidance-lives-in-living-spec-writing)
- **Bound**: an acceptance criterion of the terminology spec: the change adds at most 30 lines to
  `living-spec-writing.md` (lines of at most 120 characters, the instruction's style). The `spec-sync` addition is one
  bullet of Step 1. The constitution (`AGENTS.md` of the `spec` bundle) gains nothing.
  (ADR-terminology-guidance-lives-in-living-spec-writing)
- **Seeded glossary table**: `| Term | Definition | Owner | Avoid | Code identifiers |`. The definition states what the
  term excludes and which adjacent term it is distinct from when confusion is likely. `Owner` is the defining document
  ID (`CAP-...`, `ADR-...`) or the owning component. An original-language rendering goes in the `Term` cell
  (`기능 원장 (Living Spec)`), replacing the `English / Abbr` column. Empty `Avoid` and `Code identifiers` cells are
  allowed. The two earlier authoring guidelines in the seed are replaced by a one-line pointer to the
  `living-spec-writing` instruction. (ADR-seeded-glossary-columns)
- **Avoid as synonyms**: where `docs/glossary.yaml` exists, an Avoid entry is also added as a synonym of the term's
  cluster. No generation or synchronisation between the files. (ADR-seeded-glossary-columns)
- **Older glossaries**: a glossary without these columns records owner, exclusions and avoided synonyms in its existing
  remarks or definition cells; the guidance does not require migrating a project-owned glossary.
  (ADR-seeded-glossary-columns)
- **devkit-spec's own glossary** uses the five columns: `Defined in` became `Owner`, and `Avoid` and `Code identifiers`
  are filled where a rejected synonym or an identifier is known. (ADR-seeded-glossary-columns)
- **Layered writing instructions** in the `spec` bundle, preset `core`: `document-writing` (sentence-level rules for
  every document), `decision-writing`, `capability-writing`, `usecase-writing`, `architecture-writing`.
  `contract-authoring` and `living-spec-writing` keep their own topics; a rule lives in one of them only.
  (ADR-layered-writing-guidance)
- **Authoring**: the `authoring` bundle, presets `skill-authoring` and `all`, carries `agent-asset-writing`,
  self-contained; the `skill-authoring` playbook keeps procedures only. (ADR-layered-writing-guidance)
- **Descriptions**: each writing instruction's description starts with `Read before` and stays at most 300
  characters. (ADR-layered-writing-guidance)

---

## 5. Consequences

- **Positive**: the agent reads only the guidance for the document at hand; writing rules have one owner.
  (ADR-layered-writing-guidance)
- **Negative / Risks**:
  - Five more headers in every spec context; `agent-asset-writing` restates a few common rules.
    (ADR-layered-writing-guidance)
  - Exclusions have no column of their own, so a reviewer checks them in the definition text.
    (ADR-seeded-glossary-columns)
  - Code naming outside `docs/` and `specs/` gets no separate trigger: rule 6 still covers new identifiers when a spec
    names them. A separate instruction remains possible later if sessions name code concepts without reading it.
    (ADR-terminology-guidance-lives-in-living-spec-writing)
- **Other**:
  - No new asset in `bundle.toml` for terminology; `CAP-HARN-agent-guidance` section 4.3 updates the
    `living-spec-writing` row, and section 4.7 describes the five seeded columns and the project section for avoided
    generic nouns. (ADR-terminology-guidance-lives-in-living-spec-writing, ADR-seeded-glossary-columns)
  - Projects without `docs/glossary.md` read the rules; registration steps apply only where a glossary exists.
    (ADR-terminology-guidance-lives-in-living-spec-writing)
  - The seeded `glossary.yaml` comment already asks for searched abbreviations and translations; the Avoid line extends
    that practice without a schema change. (ADR-seeded-glossary-columns)
- **Follow-ups**: rewrite other skills after the `spec-plan` pilot; add mechanical style rules once the pilot gives
  evidence. (ADR-layered-writing-guidance)

---

## 6. Confirmation

`packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` checks the instruction set, the
description prefix and length; `packages/devkit/tests/integration/bundles/authoring/test_bundle.py` checks the
authoring preset and that `agent-asset-writing` names no `spec` instruction. (ADR-layered-writing-guidance)
