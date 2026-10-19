---
id: PADR-terminology-guidance-lives-in-living-spec-writing
title: Terminology guidance lives in living-spec-writing
summary: "Places the domain-neutral terminology guidance in the Glossary section of the living-spec-writing instruction instead of a new instruction, with a short default list of generic nouns, project additions in docs/glossary.md and a length bound."
proposal: PROP-terminology-authoring-guidance
status: draft
created_at: 2026-10-19
---

# [PADR-terminology-guidance-lives-in-living-spec-writing] Terminology guidance lives in living-spec-writing

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

The proposal ships eight terminology rules (proposal section 3.2) as bundle instruction text. It must decide where the
text lives (spike Q1), where the list of bare generic nouns lives (Q2), and whether its size is bounded (Q6). The text is
read before most documentation work, so every added line is paid in context by many sessions.

## 2. Decision Drivers

- The trigger: the guidance must be read at the moment a document names or registers a term.
- Context budget: `devkit get-context spec` returns each instruction's header, and the constitution tells every session
  to read the relevant instruction bodies.
- Projects differ in which nouns are overloaded; the bundle cannot know a project's domain.

## 3. Considered Options

- **Q1-A. Fold into `living-spec-writing`**: extend its `## Glossary` section and widen its description to mention
  naming and the glossary. That instruction is already read before any `docs/` or `specs/` edit, which is where terms
  are named and registered.
- **Q1-B. New `terminology` instruction**: its own header and trigger ("before naming a new domain concept"), at the
  cost of a third instruction header in every `get-context` result and a second body to read before documentation work.
- **Q2**: the generic-noun list in the instruction only, in the glossary only, or a short default in the instruction
  plus project additions and exceptions in a section of `docs/glossary.md`.
- **Q6**: no bound, or a bound on the lines the change adds to the instruction as an acceptance criterion.

## 4. Decision Outcome

- **Q1: Option Q1-A.** The guidance becomes the body of the `## Glossary` section of
  `packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md`; the instruction's `description`
  names terminology and the glossary so the header announces it. The existing package-glossary sentence stays in the
  section.
- **Q2: both.** The instruction lists a short default of bare generic nouns (rule 1); the seeded `docs/glossary.md`
  carries a project section for additional avoided generic nouns and exceptions, which the instruction points to.
- **Q6: bounded.** An acceptance criterion of the spec: the change adds at most 30 lines to `living-spec-writing.md`
  (lines of at most 120 characters, the instruction's current style). The `spec-sync` addition is one bullet of Step 1.
- The constitution (`packages/devkit-spec/src/devkit_spec/bundle/AGENTS.md`) gains nothing.

## 5. Consequences

- No new asset in `bundle.toml`; `CAP-HARN-agent-guidance` section 4.3 updates the `living-spec-writing` row instead of
  adding one.
- Code naming outside `docs/` and `specs/` gets no separate trigger: rule 6 still covers new identifiers when a spec
  names them. A separate instruction remains possible later if sessions name code concepts without reading it.
- Projects without `docs/glossary.md` read the rules; registration steps apply only where a glossary exists.
