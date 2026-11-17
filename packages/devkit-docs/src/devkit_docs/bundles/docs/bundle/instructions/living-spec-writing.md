---
name: living-spec-writing
description: Read before authoring, editing or reviewing docs/ or specs/ documents. Defines current-state writing, decision placement, fact-type ownership, the steps formal design, domain and operations documents share, traceability, summaries, ID references, steering documents, terminology and the glossary.
---

# Living Spec Writing

## Current State and History

- When behavior or a decision changes, rewrite the affected statements in `docs/` in place, citing the source ID
  (ADR, MAT, SPEC) where the reason matters. Add no dated headings, correction notes ("changed from X to Y") or
  history sections.
- Keep temporary checklists and task lists in the selected approach's work records, not `docs/`.

## Decision Placement

- Record decisions and their rationale in ADRs; other documents link the ADR by ID instead of repeating its reasoning.
- Keep decisions and ADR references out of always-loaded guidance (constitutions, guidance blocks), because document work
  searches related decisions. Exception: a minimum operational rule an agent needs before it can search, when its absence
  causes a named failure.

## Responsibility and design navigation

- Assign each normative statement one owner. Route each fact by its type to the owner in this table; a fact with two
  parts splits between the owners named:

  | Fact type | Owner |
  | --- | --- |
  | Behavior, validity, safety, limit, output order or tie-break a consumer can observe | Capability |
  | That a code is raised, and when, as a guarantee | Capability rule; trigger condition, level and fix in a reference code table |
  | Command, flag, API, configuration key or payload field syntax | Reference; the capability lists the interface |
  | Data that a later run, another process or another tool reads back: location pattern, encoding, fields, example | Design datasheet; a format consumers author or parse is also a capability interface |
  | How an ID, key, hash, token or name is derived | Design; what the identity means belongs to the domain model |
  | Local mechanism, internal processing order, algorithm, pseudocode or worked example | Design, or the source alone |
  | Concept meaning, identity, relationships and lifecycle | Domain model; glossary for terms |
  | Enduring choice, rationale and rejected options | ADR |
  | Measurement, experiment or assumption | Materials |
  | Actor goal, scenario and success contract | Use case |
  | Human interface element and interaction | UX |
  | System structure, interactions, deployment and architectural constraints | Architecture |
  | Symptom and evidence routed to an existing action owner, and normal-state observation | Operations |
  | Executable recovery steps and permissions | The existing instruction, playbook, advisory or executable owner |
  | Contributor development activity | Development guide |

- Keep domain meaning, implementation design and operational composition distinct without a fixed authoring order.
- If transferring a normative statement, replace its previous normative restatement in the same change and name
  the receiving owner; otherwise use a concise non-normative summary citing the owner.
- Choose content by responsibility, never by length or numerical detail.

For a design, domain or operations document, read `design-writing.md`, `domain-writing.md` or
`operations-writing.md` and start from the matching template in `../templates/`; all three share these steps:

1. Before writing, settle the one reader question the document answers; if the content answers none, drop it, and
   if it answers several, split it into documents that each answer one.
2. Open with an unheaded lead paragraph under the H1, with at most one sentence phrased as a question and no
   question section or label.
3. Link related documents by full ID in the body or in typed `related_*` lists, only where useful; require no
   reciprocal links, whole-layer reading or reading order. Keep `aliases` for same-prefix identity, never relations.
4. Give independently maintained Markdown detail its own formal peer ID; give parent-owned support no ID, link it
   from the parent and name the parent in it.
5. On a rename or root move, move the document with its support, keep the old ID in `aliases` and repair ordinary
   links. On an area move, keep the ID and update `area`. On a split or reclassification, give each artifact one
   canonical parent and keep a cross-kind predecessor retired with its successor named.
6. To fold a document into another of the same kind, move the sentences only it holds into the receiving document,
   delete the folded document and add its ID to the receiving document's `aliases`.
7. Run `devkit rules check` and fix what it reports; review owner uniqueness, source agreement and link
   destinations yourself, since no check proves them.

## Completed Specs and Traceability

- Link use cases and capabilities both ways through YAML `usecases:` and `capabilities:`; never nest one inside the
  other.

## Summaries

- Write `summary` as one or two English sentences that state the subject and its boundary for a reader who has never
  seen the document, because `devkit docs search` finds documents by it. Skip status, history and boilerplate
  ("This document describes ..."). Titles and bodies may use any language.
- Rewrite the summary whenever the document's contract changes.
- Write it as a double-quoted YAML string (`summary: "..."`): an unquoted value containing `: ` or starting with a
  backtick breaks the frontmatter, and the document drops out of the index.

## References

- Refer to ID-bearing documents by full ID in prose and exact ID in relationship fields, without Markdown paths; keep
  ordinary links for URLs, images, code paths and documents without IDs.
- To rename a document whose ID derives from its path, move the file, set the new ID and keep the old ID in `aliases`
  on every file whose ID derives from the moved path; follow the selected approach
  when renaming accepted decisions. Then run `devkit rules fix` to move current references to the new ID.

## Steering documents

- `docs/steering/` holds project-wide background that is neither a contract nor evidence: the glossary, the
  product's purpose, a tone or style guide, a domain overview. One Markdown file per topic, directly in the
  directory, with only `title` and a one-sentence English `summary` saying when an agent reads it; no `id`, so it
  stays outside the document index and search. Cite documents in it by full ID in backticks; they must resolve.
- `devkit get-context docs` lists every steering file's `title` and `summary`; keep each body short enough to read
  whole (`RULE-steering-documents` caps the count and size). Put behavior in capabilities and evidence in materials,
  never in a steering document.
- Put package background in `docs/packages/<name>/steering/` of a registered namespace (`[[tool.docs.namespaces]]`),
  under the same rules and caps; the context lists it when the working directory is inside that package. Keep the
  package glossary and optional search synonyms at `docs/packages/<name>/steering/glossary.md` and
  `docs/packages/<name>/steering/glossary.yaml`, beside the other package background.

## Glossary

- Terms are defined in `docs/steering/glossary.md`. A package's documents (`docs/packages/<name>/`) may keep
  `docs/packages/<name>/steering/glossary.md`, read together with the root glossary. A package redefinition applies
  to that package's documents only; keep shared definitions in the root glossary.
- If the package still has `docs/packages/<name>/glossary.md`, move its content into `steering/glossary.md` before
  using it; merge with an existing canonical file and preserve `title` and an English `summary` frontmatter.
- Keep registers optional: create a package glossary only when it has local terms; never copy the global glossary.
- Search reads global plus selected namespace `steering/glossary.yaml` files; `--namespace global` reads only global,
  while all-namespace selection adds registered namespaces in name order. Shared token clusters are merged.
- Check the glossary while naming a domain concept or registering a term. No check enforces the rules below.

1. Do not name a new domain concept with a bare generic noun (target, resource, scope, context, state, status,
   revision, data, item); add a qualifier that shows what it applies to, who owns it or where it ends. Project
   additions and exceptions live in a section of `docs/steering/glossary.md`.
2. Use the full registered term in titles, headings, table cells and sentences meant to stand alone.
3. One concept, one term. Record rejected synonyms in the Avoid column; where the owning synonyms file (`docs/steering/glossary.yaml` or the namespace's
   `steering/glossary.yaml`) exists, also add each Avoid entry as a synonym of the term's cluster.
4. Register the same spelling with a different owner or meaning separately, with its owner; never bulk-replace a word
   across contexts.
5. Quote existing API fields, types, paths and JSON exactly and map them to the term ("approval subject (`target`
   field)"). This guidance does not authorize renaming code, APIs or schemas; a rename is its own spec.
6. Before registering a term, check overlap with existing rows and record its owner and what it excludes.

A glossary without the `Owner`, `Avoid` and `Code identifiers` columns records them in its existing remarks or
definition cells.
