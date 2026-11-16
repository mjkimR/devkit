---
id: PROP-formal-document-templates
title: Template alignment for formal design, domain and operations documents
summary: "Aligns the design, domain and operations templates and writing instructions with the documents authors write, starting with removal of the question section that restates the summary."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-documentation-system-evolution
depends_on:
  - PROP-design-bundle-layout
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/
    - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    - docs/designs/
    - docs/domain/
    - docs/operations/
    - docs/proposals/PROP-formal-document-templates/
  excludes:
    - packages/devkit-viewer/
    - packages/devkit-spec/
    - packages/devkit-adaptive/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-document-templates] Template alignment for formal design, domain and operations documents

## 1. Background & Hypothesis

`SPEC-formal-document-kinds` shipped `templates/{design,domain,operations}.md` and the matching writing
instructions in the docs bundle. The five delivered documents diverge from those templates, and no rule checks
their sections:

- **Question section.** The design template opens with `## 1. Reader question and mechanism` and the domain
  template with `## 1. Conceptual question`; the operations template has none. In the delivered documents the
  question restates the frontmatter `summary` as an interrogative: `DOMAIN-bundle-selection-and-installation` has
  the summary "Relates available bundles, requested selection, conceptual assets, projected paths and receipt
  evidence." and the question "How do available bundles, requested selection, conceptual assets, projected paths
  and receipt evidence relate?". A reader arriving from `devkit docs list` or search has already read the summary.
- **Section structure.** No delivered document uses the templates' three numbered sections. Each uses topic
  headings and closes with an authority boundary and a maintenance note.
- **Authority boundary.** `CAP-DOCS-documentation-ownership` §3.3 asks authors to state the authority boundary.
  Every delivered document has that section; no template does.
- **Guidance form.** Template guidance is body prose, so a copied template leaves authoring directions in the
  document. The capability and UX templates carry guidance in comments.
- **Tables.** `OPS-distribution-sync` and both domain documents centre on a table (symptom, evidence and owner;
  relationship, question and owner). The templates describe those tables in prose only.

Hypothesis: a template that matches the shape authors already produce, without a section that repeats the summary,
yields documents that need no restructuring after authoring.

`PROP-design-bundle-layout` changes the canonical paths the same templates and instructions name. This proposal
follows it, so each file is restructured once against the delivered path grammar.

## 2. Technical Spike Questions

- **Q1**: Does removing the question section satisfy `CAP-DOCS-documentation-ownership` §3.3, which asks authors to
  state the reader question, or does that clause change with the templates?
- **Q2**: Which of the remaining gaps does this proposal fix: section structure, authority boundary section,
  guidance as comments, table skeletons, the pre-seeded empty `related_*` lists and the missing `status` value
  comment?
- **Q3**: Do the five delivered documents change to match the templates, or do the templates only govern documents
  written after them?
- **Q4**: Is `templates/design-template.md`, the compatibility pointer to `design.md`, removed? State whether any
  released version shipped the older name.

## 3. Proposed Design & Impact

- **Question section.** Remove the question section and label from the design and domain templates. Open each
  document with a problem statement per kind: the problem the mechanism solves for design, the concepts readers
  confuse for domain, the observed symptom for operations.
- **Scoping step.** Move the scoping function to the writing instructions as an authoring step: settle the one
  question the document answers before writing, and split or drop a document that has none.
- **Remaining gaps.** Apply the outcome of Q2 to the three templates and instructions.
- **Assets.** Edit the docs bundle sources under `packages/devkit-docs/src/devkit_docs/bundles/docs/` and project
  them with `devkit sync`; apply `agent-asset-writing` to the instruction edits.

### Non-Goals

- No change to paths, identity, frontmatter schema, status vocabulary or relation fields; `PROP-design-bundle-layout`
  and `ADR-formal-role-document-identities` own those.
- No rule that checks template sections.

### Expected acceptance evidence

- **T1 — Templates**: The three templates carry no question section, open with the per-kind problem statement and
  reflect the Q2 outcome; the docs bundle distribution test passes.
- **T2 — Instructions**: Each writing instruction states the scoping step and agrees with its template and with
  `CAP-DOCS-documentation-ownership` §3.3.
- **T3 — Documents**: The delivered documents agree with the Q3 outcome and pass `devkit rules check`.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q4. This stays one S feature proposal and starts Development after
`PROP-design-bundle-layout` delivers its path grammar. Acceptance and handoff follow the existing gates.
Retirement requires T1–T3.
