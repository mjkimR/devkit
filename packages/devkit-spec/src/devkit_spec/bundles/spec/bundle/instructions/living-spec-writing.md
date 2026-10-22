---
name: living-spec-writing
description: Read before authoring, editing or reviewing docs/ or specs/ documents. Defines current-state writing, decision placement, history placement, completed specs, story-capability traceability, summaries, ID references, terminology and the glossary.
---

# Living Spec Writing

## Current State and History

- When behavior or a decision changes, rewrite the affected statements in `docs/` in place, citing the source ID (ADR, MAT, SPEC) where the reason matters: `docs/` is a current-state ledger, not a changelog.
- Do not add dated headings, correction notes ("corrected on ...", "changed from X to Y") or history sections to capabilities, stories, architecture, development guides, the glossary or proposals.
- Change history belongs in Git, append-only ADRs (replace through `supersedes`) and dated `docs/materials/`. Frontmatter dates and ADR/material dates are metadata, not prose history.
- Temporary checklists and PR task lists belong in `specs/`, never directly in `docs/`.

## Decision Placement and Duplication

- Record decisions and their rationale in ADRs.
- Do not repeat a decision, or keep appending references to individual ADRs, in guidance blocks, constitutions or
  other always-loaded instructions only because it is important; Planning already searches related ADRs.
- Reserve always-loaded guidance for common constraints an agent needs before it can search for task-specific
  decisions. An exception SHOULD identify the concrete failure caused by missing that constraint before discovery;
  include only the minimum operational rule and keep its detailed rationale in the ADR.
- Capabilities describe the affected feature's current contract. Update that contract when behavior changes, but
  do not copy the ADR's reasoning or background into it merely to make the decision more visible.
- Choose placement by when the information is needed. Avoid the pattern "this decision is important, so add it
  everywhere the agent reads"; use relevant ADR discovery instead of accumulating decision-specific context.

## Completed Specs and Traceability

- A spec with `status: completed` remains in place as work history. Editing it is not prohibited; `RULE-spec-lifecycle` keeps its status consistent with its tasks and reconcile record.
- For the current contract, read `docs/capabilities/` and `docs/stories/`; a completed spec is not a default discovery or orientation target.
- Start a later behavior change in a new spec.
- Stories and capabilities form an orthogonal M:N relationship. Link them through YAML `stories:` in capabilities and `capabilities:` in stories, both ways (`RULE-traceability-link`); do not physically nest either inside the other.

## Summaries

- Capabilities, stories, decisions, architecture documents, proposals and specs carry `summary` in their frontmatter: one or two English sentences saying what the document defines (`RULE-document-summary`). Titles and bodies may be written in any language.
- Write the summary for a reader who has never seen the document, because `devkit spec search` embeds the ID and the summary and finds the document by meaning. State the subject and its boundary; skip status, history and boilerplate ("This document describes ...").
- Rewrite the summary whenever the document's contract changes.
- Write it as a double-quoted YAML string (`summary: "..."`): an unquoted value containing `: ` or starting with a backtick breaks the frontmatter, and the document drops out of the index.

## References

- Refer to ID-bearing internal documents with full IDs in prose and exact IDs in relationship fields; omit Markdown paths. IDs are path-derived slugs, never dates or sequence numbers (`RULE-id-convention`, `RULE-document-reference`).
- Keep external URLs, images, code paths and documents without IDs as ordinary links. Code examples, non-ID inline code and H1 self IDs are not reference edges.

## Glossary

- Terms are defined in `docs/glossary.md`. In a monorepo, a package's documents (`docs/packages/<name>/`) may keep `docs/packages/<name>/glossary.md`: read it together with the root glossary. A package redefinition applies to that package's documents only.
- Check the glossary while naming a domain concept or registering a term; registration applies only where a glossary exists. No check enforces the rules below: they inform naming and ask for no approval.

1. Do not name a new domain concept with a bare generic noun (target, resource, scope, context, state, status, revision, data, item). Add a qualifier that shows what it applies to, who owns it, or where it ends. Padding (`target data`) is not a qualifier. Project additions and exceptions live in a section of `docs/glossary.md`.
2. Use the full registered term in titles, headings, table cells and sentences meant to stand alone. A short form is fine inside a paragraph whose subject is already clear.
3. One concept, one term. Record rejected synonyms in the Avoid column and do not alternate. Where `docs/glossary.yaml` exists, also add each Avoid entry as a synonym of the term's cluster.
4. Same spelling, different owner or meaning: register each separately with its owner (approval request version vs. deployment revision). Never bulk-replace a word across contexts.
5. Use established terms and proper nouns (User Story, idempotency, product names) with their standard meaning; describe only the project's scope of use.
6. Keep document terms and code identifiers distinct. Quote existing API fields, types, paths and JSON exactly and map them ("approval subject (`target` field)"). This guidance does not authorize renaming code, APIs or schemas; a rename is its own spec. New identifiers SHOULD follow the registered term.
7. Before registering a term, check overlap with existing rows and record its owner and what it excludes. In Living Spec documents, rename in place without "formerly X" notes.
8. ADRs, `docs/materials/`, completed specs, quotations and generated output keep their original wording and are not reused as the current contract.

A glossary without the `Owner`, `Avoid` and `Code identifiers` columns records owner, exclusions and avoided synonyms in its existing remarks or definition cells; migrating a project-owned glossary is not required.
