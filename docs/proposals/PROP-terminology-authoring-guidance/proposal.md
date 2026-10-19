---
id: PROP-terminology-authoring-guidance
title: Terminology authoring guidance and a glossary that agents read
summary: "Adds domain-neutral terminology authoring guidance to the spec bundle, reshapes the seeded glossary table around owners, exclusions, avoided synonyms and code identifiers, and makes spec-sync update the glossary, so docs/glossary.md is read while writing instead of only seeded."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-14
target_area: capabilities/harness/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/harness/
    - packages/devkit-spec/src/devkit_spec/bundle/instructions/
    - packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/
    - docs/glossary.md
  excludes:
    - docs/decisions/
    - packages/devkit-spec/src/devkit_spec/bundle/rules/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
workflow_hash: sha256:90918c632715461d07f99f683b8381bdbe6381ad6689a7575a72c002c18c1399
---

# [PROP-terminology-authoring-guidance] Terminology authoring guidance and a glossary that agents read

## 1. Background & Hypothesis

### 1.1 Problem

The starting point is a draft of terminology rules used in another project (origin: user), first incubated earlier
and carried over here because its findings hold for the `spec` bundle. The current state of the bundle:

- **Nothing reads the glossary while writing.** The only bundle mention of the glossary in an authoring path is the
  `## Glossary` section of the `living-spec-writing` instruction, which says where terms are defined and nothing about
  when to check or update them. No `spec*` skill mentions it, so `spec-sync` never asks whether a change introduced or
  renamed a domain term. The seeded `docs/glossary.md` is written once and then not consulted.
- **The seeded guideline reads as permission to rename code.** The second authoring guideline of
  `packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md` is "Code symbols (classes, DB tables, API fields) should adhere to the
  canonical terminology defined in this glossary." Tidying document terms can be read as a mandate to rename API fields
  and tables; what is actually needed, a way to map terms to existing identifiers, is missing.
- **The table has no place for the rules.** The seeded columns are `Term | English / Abbr | Definition & Description |
  Relevant Area | Remarks`: no owner, no adjacent concepts to keep apart, no rejected synonyms, no code identifiers.
- devkit-spec's own `docs/glossary.md` already moved part of the way: its tables are `Term | Definition | Defined in`,
  where "Defined in" names the owning document ID, and it settles that `docs/` as a whole is the Living Spec (the
  scope conflict earlier glossaries had).

### 1.2 Hypothesis

Ship domain-neutral terminology guidance as bundle instruction text, reshape the seeded glossary table around the
fields that guidance uses, and add one impact question to `spec-sync`. Every session then sees the guidance header
through `devkit get-context spec` and reads the body before writing documents, and the glossary becomes a document that
is checked while writing and updated at reconciliation instead of a seeded file nobody opens.

- No new human gate or question point. The guidance informs the agent's naming decisions and asks for no approval.
- No command change: instructions are bundle assets (`CAP-HARN-agent-guidance`), and the skeleton stays opt-in
  (`ADR-docs-skeleton-is-opt-in`). Projects without a `docs/glossary.md` still receive the guidance; registration
  steps apply only where a glossary exists.

## 2. Technical Spike Questions

Settled in Planning; the decisions and their options are in `PADR-terminology-guidance-lives-in-living-spec-writing`
(Q1, Q2, Q6) and `PADR-seeded-glossary-columns` (Q3, Q4, Q5).

- **Q1. Separate instruction or a section of `living-spec-writing`.** Folded into the `## Glossary` section of
  `living-spec-writing`; its description is widened to name terminology and the glossary. No new asset.
- **Q2. Where the generic-noun list lives.** Both: a short default in the instruction (rule 1), project additions and
  exceptions in a section of the seeded `docs/glossary.md`.
- **Q3. Column set.** `Term | Definition | Owner | Avoid | Code identifiers`; exclusions and adjacent terms are written
  in the definition; an original-language rendering goes in the `Term` cell (`기능 원장 (Living Spec)`).
- **Q4. `Avoid` and `glossary.yaml` synonyms.** One line of guidance: where `docs/glossary.yaml` exists, an Avoid entry
  is also added as a synonym of the term's cluster. No generation between the files.
- **Q5. Existing glossaries.** One-line fallback: without the columns, owner, exclusions and avoided synonyms go in the
  existing remarks or definition cells; no migration of a project-owned glossary is required.
- **Q6. Context budget.** An acceptance criterion: the change adds at most 30 lines to `living-spec-writing.md`; the
  `spec-sync` change is one Step 1 bullet.

## 3. Proposed Design & Impact

### 3.1 Placement

| Location | Content |
| --- | --- |
| `packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md` (`## Glossary` section and description, Q1) | The guidance of 3.2, at most 30 added lines (Q6) |
| `packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md` | The table of 3.3, a project section for avoided generic nouns and exceptions, a one-line pointer to the guidance; the two existing authoring guidelines removed |
| `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/SKILL.md`, Step 1 | One impact question: did the change introduce or rename a domain term? Then update `docs/glossary.md` |
| `docs/glossary.md` (dogfood) | Migrated to the five columns of 3.3: `Defined in` becomes `Owner`, `Avoid` and `Code identifiers` added |

The constitution (`packages/devkit-spec/src/devkit_spec/bundle/AGENTS.md`) gains nothing: it already tells every session to read the
relevant instruction bodies, and repeating the guidance there costs context in every session.

### 3.2 Guidance Draft

The normative level follows the `contract-authoring` instruction: no check enforces these rules, so the text uses
boundary statements ("does not authorize") and SHOULD rather than MUST.

```markdown
1. Do not name a new domain concept with a bare generic noun (target, resource, scope,
   context, state, status, revision, data, item). Add a qualifier that shows what it applies
   to, who owns it, or where it ends. Padding (`target data`) is not a qualifier.
2. Use the full registered term in titles, headings, table cells and sentences meant to
   stand alone. A short form is fine inside a paragraph whose subject is already clear.
3. One concept, one term. Record rejected synonyms in the Avoid column and do not alternate.
4. Same spelling, different owner or meaning: register each separately with its owner
   (approval request version vs. deployment revision). Never bulk-replace a word across contexts.
5. Use established terms and proper nouns (User Story, idempotency, product names) with their
   standard meaning; describe only the project's scope of use.
6. Keep document terms and code identifiers distinct. Quote existing API fields, types, paths
   and JSON exactly and map them ("approval subject (`target` field)"). This guidance does not
   authorize renaming code, APIs or schemas; a rename is its own spec. New identifiers SHOULD
   follow the registered term.
7. Before registering a term, check overlap with existing rows and record its owner and what it
   excludes. In Living Spec documents, rename in place without "formerly X" notes.
8. ADRs, docs/materials/, completed specs, quotations and generated output keep their original
   wording and are not reused as the current contract.
```

Beside the rules the section carries three short lines: project additions to the rule 1 list and exceptions live in a
section of `docs/glossary.md` (Q2); an Avoid entry is also a synonym of the term's cluster in `docs/glossary.yaml`
where that file exists (Q4); a glossary without the columns of 3.3 records owner, exclusions and avoided synonyms in its
existing cells (Q5). The existing package-glossary sentence of the section stays.

Relative to the original draft: rule 3 (one concept, one term) is new, covering the direction the draft missed; the
draft's last item is split into 7 (when to check, tied to in-place rewriting) and 8 (records keep their wording,
mapped to ADRs, materials and completed specs); domain-specific examples are replaced with generic ones.

### 3.3 Glossary Table

```markdown
| Term | Definition | Owner | Avoid | Code identifiers |
```

- **Definition**: also states what the term excludes and which adjacent term it is distinct from when confusion is
  likely (rule 7).
- **Owner**: the document ID that defines the term (`CAP-...`, `ADR-...`) or the owning component; rules 4 and 7.
- **Avoid**: rejected synonyms; rule 3. Where `docs/glossary.yaml` exists, each is also a synonym of the term's cluster.
- **Code identifiers**: the matching API fields, types and paths; rule 6.
- Empty `Avoid` and `Code identifiers` cells are allowed. A glossary with older columns records these fields in its
  remarks or definition cells (Q5).

### 3.4 Non-Goals

- No deterministic rule checks generic or avoided terms: the judgement is contextual and false positives are costly.
  A hygiene rule is a separate proposal once repeated violations are observed.
- No bulk renaming of code, API or database identifiers.
- No generation or synchronisation between `glossary.md` and `glossary.yaml`.
- No command change.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: none expected; the instruction mechanism is devkit's resource taxonomy and the bundle's
  instruction assets (`CAP-HARN-agent-guidance`).
- Research: none needed.
- On acceptance: Q1 to Q6 are settled (section 2); set `status: accepted` and run `devkit spec proposal handoff
  terminology-authoring-guidance`.
- On rejection: record a rejection ADR in `docs/decisions/` and delete the proposal directory.
