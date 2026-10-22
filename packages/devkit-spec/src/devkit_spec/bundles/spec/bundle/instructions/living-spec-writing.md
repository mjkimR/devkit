---
name: living-spec-writing
description: Read before authoring, editing or reviewing docs/ or specs/ documents. Defines current-state writing, decision placement, history placement, completed specs, use case and capability traceability, summaries, ID references, terminology and the glossary.
---

# Living Spec Writing

## Current State and History

- When behavior or a decision changes, rewrite the affected statements in `docs/` in place, citing the source ID
  (ADR, MAT, SPEC) where the reason matters. Add no dated headings, correction notes ("changed from X to Y") or
  history sections.
- History belongs in Git, ADRs and dated `docs/materials/`. A changed decision is a new ADR with `supersedes`;
  editing an ADR without changing its decision, and consolidation through the `adr-compaction` playbook, are allowed.
- Temporary checklists and PR task lists belong in `specs/`, not `docs/`.

## Decision Placement

- Record decisions and their rationale in ADRs; other documents link the ADR by ID instead of repeating its reasoning.
- Keep decisions and ADR references out of always-loaded guidance (constitutions, guidance blocks), because Planning
  searches related ADRs. Exception: a minimum operational rule an agent needs before it can search, when its absence
  causes a named failure.

## Completed Specs and Traceability

- A spec with `status: completed` stays in place as history; start a later behavior change in a new spec. Read the
  current contract in `docs/capabilities/` and `docs/usecases/`, not in completed specs.
- Link use cases and capabilities both ways through YAML `usecases:` and `capabilities:`; never nest one inside the
  other.

## Summaries

- Write `summary` as one or two English sentences that state the subject and its boundary for a reader who has never
  seen the document, because `devkit spec search` finds documents by it. Skip status, history and boilerplate
  ("This document describes ..."). Titles and bodies may use any language.
- Rewrite the summary whenever the document's contract changes.
- Write it as a double-quoted YAML string (`summary: "..."`): an unquoted value containing `: ` or starting with a
  backtick breaks the frontmatter, and the document drops out of the index.

## References

- Refer to ID-bearing documents by full ID in prose and exact ID in relationship fields, without Markdown paths; keep
  ordinary links for URLs, images, code paths and documents without IDs.
- To rename a document whose ID derives from its path, move the file, set the new ID and keep the old ID in `aliases`
  (for a spec bundle, on `spec.md`, `plan.md`, `tasks.md` and `reconcile.md`); an approved ADR is renamed only by
  compaction. Then run `devkit rules fix` to move current references to the new ID.

## Glossary

- Terms are defined in `docs/glossary.md`. A package's documents (`docs/packages/<name>/`) may keep
  `docs/packages/<name>/glossary.md`, read together with the root glossary. A package redefinition applies to that
  package's documents only.
- Check the glossary while naming a domain concept or registering a term. No check enforces the rules below.

1. Do not name a new domain concept with a bare generic noun (target, resource, scope, context, state, status,
   revision, data, item); add a qualifier that shows what it applies to, who owns it or where it ends. Project
   additions and exceptions live in a section of `docs/glossary.md`.
2. Use the full registered term in titles, headings, table cells and sentences meant to stand alone.
3. One concept, one term. Record rejected synonyms in the Avoid column; where `docs/glossary.yaml` exists, also add
   each Avoid entry as a synonym of the term's cluster.
4. Register the same spelling with a different owner or meaning separately, with its owner; never bulk-replace a word
   across contexts.
5. Quote existing API fields, types, paths and JSON exactly and map them to the term ("approval subject (`target`
   field)"). This guidance does not authorize renaming code, APIs or schemas; a rename is its own spec.
6. Before registering a term, check overlap with existing rows and record its owner and what it excludes.

A glossary without the `Owner`, `Avoid` and `Code identifiers` columns records them in its existing remarks or
definition cells.
