---
id: SPEC-terminology-authoring-guidance
title: Terminology authoring guidance and a glossary that agents read
summary: "Adds domain-neutral terminology authoring guidance to the spec bundle, reshapes the seeded glossary table around owners, exclusions, avoided synonyms and code identifiers, and makes spec-sync update the glossary, so docs/glossary.md is read while writing instead of only seeded."
status: in-progress
created: 2026-10-19
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DLV-delivery-workflows
related_stories:
  - US-keep-the-living-spec-consistent
workflow: sdd-spec-feature
---

# [SPEC-terminology-authoring-guidance] Terminology authoring guidance and a glossary that agents read

## 1. Problem Statement & Motivation

Handed off from proposal PROP-terminology-authoring-guidance on 2026-10-19; the Planning decisions are
`ADR-terminology-guidance-lives-in-living-spec-writing` (where the guidance lives, the generic-noun list, the length
bound) and `ADR-seeded-glossary-columns` (the seeded columns, Avoid entries as search synonyms, older glossaries).
Target Docs Blueprint: `PROP-terminology-authoring-guidance-target`.

The `spec` bundle seeds a `docs/glossary.md`, but nothing reads it while writing:

- The `## Glossary` section of the `living-spec-writing` instruction says only where terms are defined, nothing about
  when to check or update them, and no `spec*` skill mentions the glossary, so `spec-sync` never asks whether a change
  introduced or renamed a domain term.
- The seeded authoring guideline "Code symbols (classes, DB tables, API fields) should adhere to the canonical
  terminology defined in this glossary" reads as a mandate to rename code; a way to map terms to existing identifiers
  is missing.
- The seeded columns (`Term | English / Abbr | Definition & Description | Relevant Area | Remarks`) have no owner, no
  rejected synonyms and no code identifiers.

The change ships eight domain-neutral terminology rules as the body of the instruction's `## Glossary` section,
reshapes the seeded glossary table around the fields those rules use, adds one glossary question to `spec-sync`
Step 1 and migrates devkit's own `docs/glossary.md` to the new columns. The guidance asks for no approval and adds no
gate; no command changes (instructions are bundle assets, `CAP-HARN-agent-guidance`), and the docs skeleton stays
opt-in (`ADR-docs-skeleton-is-opt-in`).

### Assumptions

- The three short lines the proposal places beside the rules (project additions to the generic-noun list, Avoid
  entries as `glossary.yaml` synonyms, the older-glossary fallback) are written as the last sentence of rule 1, the
  last sentence of rule 3 and one closing paragraph: each sits next to the rule it qualifies and the section stays
  inside the 30-line bound.
- The 30-line bound counts the lines `git diff --numstat` reports as added to `living-spec-writing.md` against the
  handoff base, the rewritten `description` line included; each added body line is at most 120 characters (the ADR's
  reading of the instruction's style). The `description` stays one frontmatter line, as it already exceeded 120
  characters before the change, and existing longer body lines are not rewritten.
- devkit's own `docs/glossary.md` leaves `Avoid` empty: no rejected synonym is established in devkit's documents, and
  an Avoid entry would also have to enter `docs/glossary.yaml`, which this change does not edit. `Code identifiers`
  is filled where a definition already names an identifier.
- The seeded `docs/glossary.md` keeps its title and lead sentence; the pointer to the guidance follows the lead.

## 2. User Stories

- **US-1**: As an agent writing a `docs/` or `specs/` document, I want terminology rules and a glossary I am told to
  check, so that a new concept gets a qualified, registered term and existing code identifiers are mapped instead of
  renamed. Relates to `US-keep-the-living-spec-consistent`.
- **US-2**: As an agent reconciling a change in `spec-sync`, I want Step 1 to ask whether the change introduced or
  renamed a domain term, so that `docs/glossary.md` is updated with the rest of the Living Spec.

## 3. Non-Goals

1. **Scope Excluded**: a deterministic rule that checks generic or avoided terms.
   - **Rationale**: the judgement is contextual and false positives are costly.
   - **When to Reconsider**: repeated violations are observed; a hygiene rule is then its own proposal.
2. **Scope Excluded**: renaming code, API, schema or database identifiers, in devkit or as a mandate to consumers.
3. **Scope Excluded**: generating or synchronising `docs/glossary.md` and `docs/glossary.yaml` from each other.
4. **Scope Excluded**: any command, rule, workflow or `bundle.toml` change, a new instruction asset, or a constitution
   (`packages/devkit-spec/src/devkit_spec/bundle/AGENTS.md`) change.
5. **Scope Excluded**: migrating a project-owned glossary; a seeded file stays as written (`ADR-docs-skeleton-is-opt-in`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The instruction carries the terminology rules
- **Given** the `living-spec-writing` instruction of the `spec` bundle
- **When** its `## Glossary` section and frontmatter are read
- **Then** the section keeps the package-glossary sentence, holds eight numbered rules matching the proposal's
  guidance draft (generic nouns, full term, one concept one term, same spelling different owner, established terms,
  document terms versus code identifiers, registration check, records keep their wording), contains the sentence
  "does not authorize renaming code, APIs or schemas", and the `description` names terminology and the glossary

### [AC-02] The guidance names the glossary links and the fallback
- **Given** the `## Glossary` section of AC-01
- **When** it is read
- **Then** it states that project additions and exceptions to the rule 1 list live in a section of `docs/glossary.md`,
  that an Avoid entry is also a synonym of the term's cluster where `docs/glossary.yaml` exists, and that a glossary
  without the `Owner`, `Avoid` and `Code identifiers` columns records them in its existing cells

### [AC-03] The instruction grows by at most 30 lines
- **Given** `living-spec-writing.md` at the handoff base c0a37b07e18cde2dfdac37e9620d09d73b44dd6c
- **When** `git diff --numstat c0a37b07e18cde2dfdac37e9620d09d73b44dd6c -- packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md` runs
- **Then** the added count is at most 30 and every added line below the frontmatter is at most 120 characters

### [AC-04] The seeded glossary uses the five columns
- **Given** the seed `packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md`
- **When** it is read
- **Then** its table header is exactly `| Term | Definition | Owner | Avoid | Code identifiers |`, it has a section for
  avoided generic nouns and accepted exceptions, it points to the `living-spec-writing` instruction, and neither
  "Authoring Guidelines" nor "Code symbols (classes, DB tables, API fields)" appears in it

### [AC-05] The seeded glossary still installs cleanly
- **Given** a fresh Git repository with the `spec` bundle synced
- **When** `devkit add spec:docs-skeleton` runs and then `devkit rules check`
- **Then** `docs/glossary.md` is written with the five-column header and `devkit rules check` exits 0

### [AC-06] spec-sync asks the glossary question in one Step 1 bullet
- **Given** `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/SKILL.md`
- **When** its diff against the handoff base is read
- **Then** exactly one bullet is added, under `### Step 1`, asking whether the change introduced or renamed a domain
  term and directing an update of `docs/glossary.md` where it exists, and the file stays within the 12288-byte skill
  document budget (`packages/devkit-spec/tests/test_bundle_budgets.py` passes)

### [AC-07] devkit's own glossary uses the five columns
- **Given** devkit's `docs/glossary.md`
- **When** it is read
- **Then** every term table has the header `| Term | Definition | Owner | Avoid | Code identifiers |`, every row keeps
  its owning document ID in `Owner`, the column name `Defined in` no longer appears, and the lead paragraph names the
  five columns

