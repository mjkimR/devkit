---
id: SPEC-formal-document-templates
title: Template alignment for formal design, domain and operations documents
summary: Aligns the design, domain and operations templates and writing instructions with the documents authors write, starting with removal of the question section that restates the summary.
status: planned
created: 2026-11-16
depends_on:
  - SPEC-design-bundle-layout
related_capabilities:
  - CAP-DOCS-documentation-ownership
  - CAP-DOCS-document-model
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-formal-document-templates] Template alignment for formal design, domain and operations documents

## 1. Problem Statement & Motivation

Handed off from proposal PROP-formal-document-templates on 2026-11-16.
- **Preserved Materials**: `docs/materials/2026-11/20261116-formal-document-templates`

### 1. Background & Hypothesis

`SPEC-formal-document-kinds` shipped `templates/{design,domain,operations}.md` and the matching writing
instructions in the docs bundle. The five delivered documents diverge from those templates, and no rule checks
their sections (inventory: `docs/materials/2026-11/20261116-formal-document-templates/template-survey.md` §1):

- **Question section.** The design template opens with `## 1. Reader question and mechanism` and the domain
  template with `## 1. Conceptual question`; the operations template has none. The two designs carry a bold
  `**Reader question:**` label and the two domain documents a `## Question` section, each restating the frontmatter
  `summary` as an interrogative: `DOMAIN-bundle-selection-and-installation` has the summary "Relates available
  bundles, requested selection, conceptual assets, projected paths and receipt evidence." and the question "How do
  available bundles, requested selection, conceptual assets, projected paths and receipt evidence relate?". A reader
  arriving from `devkit docs list` or search has already read the summary.
- **Section structure.** No delivered document uses the templates' numbered sections; all five use topic headings.
- **Authority boundary.** `CAP-DOCS-documentation-ownership` §3.3 asks authors to state the authority boundary. The
  domain and operations documents have a heading for it; the designs state it as prose; no template has it.
- **Maintenance.** The designs close with a maintenance note; the domain and operations documents have none.
- **Guidance form.** Template guidance is body prose, so a copied template leaves authoring directions in the
  document. The capability and UX templates carry guidance in HTML comments and show the `status` values.
- **Tables.** `OPS-distribution-sync` and both domain documents centre on a table that routes each row to an owner
  (symptom, discriminating evidence, next useful owner; concept or relationship, distinction, owner). The templates
  describe those tables in prose only.
- **Instructions.** No writing instruction mentions a question, authority boundary or maintenance note;
  `operations-writing.md` omits the normal-state observation its template and `CAP-DOCS-documentation-ownership`
  §3.1 require.

Hypothesis: a template that matches the shape authors already produce, without a section that repeats the summary,
yields documents that need no restructuring after authoring.

External practice agrees (`docs/materials/2026-11/20261116-formal-document-templates/template-survey.md` §2): KEP, Rust RFC, PEP 12, Go, MADR and arc42 state the
problem once after the summary and keep any question inside it or as an authoring prompt; scope is set by
exclusions plus pointers to the owning document; guidance sits in comments or a separate guide; table skeletons are
placeholder rows; copy-once systems leave old documents alone and check body sections, if at all, warn-only.

`SPEC-design-bundle-layout` changes the canonical paths, the `area` field and support placement in the same
templates and instructions. This proposal follows it, so each file is restructured once against the delivered path
grammar.

## 2. User Stories

- **US-1**: As an author or agent writing a formal design, domain or operations document, I want a template whose
  opening, body and closing match the documents this repository already writes, so that the copied template needs
  no restructuring and adds no section that repeats the frontmatter `summary`.
- **US-2**: As an author, I want the writing instruction of each kind to state the scoping step, the opening and the
  closing in the same terms as its template, so that the instruction and the template never disagree.
- **US-3**: As a reader of the five delivered documents, I want each to follow its kind's revised template with its
  statements, owners and links unchanged, so that every formal document reads the same way.

## 3. Non-Goals

1. **Scope Excluded**: paths, identity, frontmatter schema, the `area` field, support placement, status vocabulary
   and relation fields; `SPEC-design-bundle-layout` and `ADR-formal-role-document-identities` own them.
2. **Scope Excluded**: a rule that checks template sections or leftover template guidance.
   **When to Reconsider**: when authored documents repeatedly ship with leftover guidance; a warn-only check is the
   cheapest start (`docs/materials/2026-11/20261116-formal-document-templates/template-survey.md` §2 item 6).
3. **Scope Excluded**: a per-document template version marker, template variants and separate guide files.
4. **Scope Excluded**: rewriting the content of the delivered documents; they are reorganized, and their statements,
   owners and links keep their meaning.
5. **Scope Excluded**: retargeting the historical `§3.4` traces of `ADR-linked-domain-relationship-views`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Templates open with the problem and close with the authority boundary and maintenance

- **Given** the docs bundle sources `templates/design.md`, `templates/domain.md` and `templates/operations.md`
- **When** each template body is read
- **Then** none has a heading or bold label containing "question", none has a numbered `## <digit>.` heading, the
  line after the H1 is an HTML comment that asks for the kind's problem (design: the problem the mechanism solves;
  domain: the concepts readers confuse; operations: the observed symptom), and the last two H2 headings are exactly
  `## Authority boundary` and `## Maintenance and next action`
- **And** every guidance line in the body sits inside an HTML comment of at most two lines; the only body text
  outside comments is headings and table skeleton rows

### [AC-02] Kind body headings, table skeletons and frontmatter comments

- **Given** the three revised templates
- **When** their bodies and frontmatter are read
- **Then** `domain.md` has `## Relationship overview` holding the table header
  `| Concept or relationship | Distinction | Authoritative owner |` with placeholder rows, `operations.md` has
  `## Routing` holding `| Symptom or state | Discriminating evidence | Next useful owner |` with placeholder rows
  followed by `## Normal-state observation`, and `design.md` has no table skeleton
- **And** each frontmatter carries `status: draft  # draft | active | retired`, a double-quoted `title`, and the
  `related_*` fields (plus `entrypoints` for design) only as YAML comments, with no pre-seeded empty list
- **And** the docs bundle distribution test passes:
  `uv run pytest packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` exits `0`

### [AC-03] Writing instructions state the scoping step, opening and closing

- **Given** `instructions/design-writing.md`, `instructions/domain-writing.md` and `instructions/operations-writing.md`
- **When** each is read beside its template
- **Then** each states the scoping step (settle the one reader question before writing; split or drop a document
  without one), the kind's opening, its body headings, the `## Authority boundary` and
  `## Maintenance and next action` closing, and a final step to delete the template's HTML comments before
  `devkit rules check`
- **And** `operations-writing.md` requires the normal-state observation and `domain-writing.md` the distinguishing
  example and the glossary pointer
- **And** `uv run devkit rules check --phase hygiene <instruction>` reports no `RULE-agent-asset-wording` warning
  for any of the three, and the forbidden-marker scan in `test_distribution.py` passes

### [AC-04] The capability clause agrees with the decision

- **Given** `CAP-DOCS-documentation-ownership` §3.3 item 2 and `ADR-problem-first-formal-document-openings`
- **When** both are read
- **Then** §3.3 item 2 asks for the problem opening, the authority boundary and the maintenance trigger with next
  useful action, and carries the reader question only as an authoring scoping step; it no longer asks authors to
  state the reader question in the document

### [AC-05] The five delivered documents follow their kind's revised template

- **Given** `DESIGN-distribution-transactions`, `DESIGN-distribution-file-directory-replacement`,
  `DOMAIN-bundle-selection-and-installation`, `DOMAIN-delivery-relationships` and `OPS-distribution-sync`
- **When** each is compared with its kind's template
- **Then** each opens with an unheaded problem paragraph, uses its kind's body headings (topic headings for design,
  `## Relationship overview` for domain, `## Routing` and `## Normal-state observation` for operations), centres
  domain and operations tables on the skeleton columns, and closes with `## Authority boundary` then
  `## Maintenance and next action`
- **And** `rg -n '^\*\*Reader question|^## Question' docs/designs docs/domain docs/operations` returns no hit (exit `1`)
- **And** every full ID and link present before the change is still present, and
  `uv run devkit rules check docs/designs docs/domain docs/operations` reports no violation

### [AC-06] The design-template compatibility pointer is gone

- **Given** the docs bundle after this change and a synchronized workspace
- **When** the bundle templates and the installed copy are listed
- **Then** `templates/design-template.md` exists in neither the bundle source nor `.devkit/managed/docs/templates/`,
  `.devkit/installation.json` no longer records it, and
  `rg -n design-template docs/capabilities docs/architecture docs/development packages` returns no hit (exit `1`)
- **And** `uv run devkit sync --check` exits `0`

### [AC-07] The installed consumer instantiates the revised templates

- **Given** the built-wheel consumer of `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`
- **When** it instantiates the installed design, domain and operations templates
- **Then** it fails with an assertion if an expected placeholder or the H1 cut point is missing, and otherwise the
  sample documents resolve, list, search and pass `devkit rules check`

## 5. Assumptions

- The superseded-in-part pointer on `ADR-linked-domain-relationship-views` already landed with the handoff commit;
  Development verifies it and does not duplicate it.
- `docs/proposals/PROP-formal-document-templates/` no longer exists after handoff, so it leaves the planned
  boundaries.
- The bundle templates are the docs bundle's own assets; they name no repository document ID
  (`agent-asset-writing` self-containment).

## 6. Source feedback

- `FB-scout-lacks-web-search` (scope: repo), recorded during Planning; not addressed by this spec.

## 7. Carried Proposal Notes

### 2. Technical Spike Questions

- **Q1**: Does removing the question section satisfy `CAP-DOCS-documentation-ownership` §3.3, which asks authors to
  state the reader question, or does that clause change with the templates? *Settled: the clause changes;
  `ADR-problem-first-formal-document-openings`.*
- **Q2**: Which of the remaining gaps does this proposal fix: section structure, authority boundary section,
  guidance as comments, table skeletons, the pre-seeded empty `related_*` lists and the missing `status` value
  comment? *Settled: all of them; Planning decisions.*
- **Q3**: Do the five delivered documents change to match the templates, or do the templates only govern documents
  written after them? *Settled: full alignment; Planning decisions.*
- **Q4**: Is `templates/design-template.md`, the compatibility pointer to `design.md`, removed? State whether any
  released version shipped the older name. *Settled: removed; no tag v0.1.0–v0.1.6 contains it.*

### 3. Proposed Design & Impact

#### Planning decisions

- **Q1 — Opening.** `ADR-problem-first-formal-document-openings`: each document opens with the problem it answers
  per kind, with no question section or label; at most one sentence of it is a question. Settling the one reader
  question becomes an authoring step in each writing instruction (split or drop a document that has none). It
  rewords `CAP-DOCS-documentation-ownership` §3.3 item 2 and supersedes in part the question clause of
  `ADR-linked-domain-relationship-views` §4, whose cited §3.4 no longer exists.
- **Q2 — Template shape.** An unheaded opening paragraph, kind-specific body headings and fixed closing headings;
  no numbered sections. Every template:
  - opens with a lead paragraph directly under the H1 stating the per-kind problem, as the two designs and
    `OPS-distribution-sync` already do, and closes with `## Authority boundary` (what the document does not settle
    and the owner that does, by full ID) and `## Maintenance and next action` (the change that requires an update and
    the next useful reader action);
  - carries guidance as one- or two-line HTML comments, keeping reasoning in the writing instruction;
  - shows `status: draft  # draft | active | retired`, quotes `title` and lists the `related_*` fields (and design
    `entrypoints`) as a YAML comment instead of pre-seeded empty lists, as `decision.md` does for `supersedes`.

  | Kind | Lead paragraph | Body | Table skeleton |
  | --- | --- | --- | --- |
  | design | the problem the mechanism solves | topic headings for mechanism, examples and datasheets | none: delivered designs are not table-centred |
  | domain | the concepts readers confuse | `## Relationship overview`, optional worked example | `Concept or relationship \| Distinction \| Authoritative owner` |
  | operations | the observed symptom | `## Routing`, `## Normal-state observation` | `Symptom or state \| Discriminating evidence \| Next useful owner` |

  Table skeletons are placeholder rows outside the comments. The operations authority boundary states that the
  document routes and owns no recovery, and what the evidence cannot conclude.
- **Instructions.** Each writing instruction states the scoping step, the opening and closing above and agrees with
  its template; `operations-writing.md` adds the normal-state observation and `domain-writing.md` the
  distinguishing example and glossary pointer. Each adds a closing step: delete the template's HTML comments before
  `devkit rules check`, since agents read the raw Markdown where comments stay visible. Apply `agent-asset-writing`;
  new text avoids the forbidden markers `test_distribution.py` scans for.
- **Q4 — Compatibility pointer.** Remove `templates/design-template.md` without an alias; update
  `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py`, the template count in
  `packages/devkit-docs/README.md`, `CAP-DOCS-documentation-ownership` §4 and `CAP-DOCS-document-model`, and the
  receipt through `devkit sync`.
- **Tests.** `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py` truncates instantiated templates
  at `## 1.` and replaces exact placeholders; Development updates both with the templates so the sample keeps
  failing loudly on drift.
- **Superseded ADR.** Add only the "Superseded in part" pointer, copied from the PADR statement, to
  `ADR-linked-domain-relationship-views`. Its `§3.4` traces stay as history: two of them belong to clauses
  `ADR-formal-role-document-identities` already superseded, and retargeting them to §3.3 would misstate them.

- **Q3 — Delivered documents.** The five delivered documents are pilots of the new kinds, so they are restructured
  in full to the revised templates once the shape is settled here, rather than left for a later cleanup. Each gets
  the problem lead paragraph without a question section or label, its kind's body headings (`## Relationship
  overview` for domain; `## Routing` and `## Normal-state observation` for operations; topic headings for design), its
  central table in the skeleton's columns, and the `## Authority boundary` and `## Maintenance and next action`
  closing sections. Content is reorganized, not rewritten: statements, owners and links keep their meaning.

  | Document | Main changes |
  | --- | --- |
  | `DESIGN-distribution-transactions` | label removed; lead states the problem; authority prose under `## Authority boundary`; `Maintenance touchpoints` becomes `## Maintenance and next action` |
  | `DESIGN-distribution-file-directory-replacement` | label removed; new problem lead; authority prose under `## Authority boundary`; `Maintenance seam` becomes `## Maintenance and next action` |
  | `DOMAIN-bundle-selection-and-installation`, `DOMAIN-delivery-relationships` | `## Question` replaced by a problem lead; table moved to the `Concept or relationship \| Distinction \| Authoritative owner` columns; closing section split into authority boundary and maintenance |
  | `OPS-distribution-sync` | lead states the symptom; `## Routing` with the skeleton columns; `## Normal-state observation`; boundary section renamed; maintenance close added |

#### Assets

Edit the docs bundle sources under `packages/devkit-docs/src/devkit_docs/bundles/docs/` and project them with
`devkit sync`. Start from the templates and instructions as `SPEC-design-bundle-layout` delivers them.

#### Non-Goals

- No change to paths, identity, frontmatter schema, the `area` field, support placement, status vocabulary or
  relation fields; `SPEC-design-bundle-layout` and `ADR-formal-role-document-identities` own those.
- No rule that checks template sections or leftover guidance.
- No per-document template version marker, template variants or separate guide files.

#### Expected acceptance evidence

- **T1 — Templates**: The three templates carry no question section, open and close with the headings above, carry
  guidance in HTML comments, ship the domain and operations table skeletons and the `status` and `related_*`
  comments; the docs bundle distribution test passes.
- **T2 — Instructions**: Each writing instruction states the scoping step and agrees with its template and with
  `CAP-DOCS-documentation-ownership` §3.3.
- **T3 — Documents**: The five delivered documents follow their kind's revised template (opening, body headings,
  table columns, closing sections) with their statements, owners and links preserved, and pass `devkit rules check`;
  `rg -n '^\*\*Reader question|^## Question' docs/designs docs/domain docs/operations` returns no hit.
- **T4 — Pointer**: `templates/design-template.md` is gone from the bundle and the installed copy;
  `rg -n design-template docs/capabilities docs/architecture docs/development packages` returns no hit, while
  materials, completed specs and other proposals keep their mentions as history. `test_installed_consumer.py`
  instantiates the revised templates.

### 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q4. This stays one S feature proposal and starts Development after
`SPEC-design-bundle-layout` delivers its path grammar. Acceptance and handoff follow the existing gates; handoff
promotes `ADR-problem-first-formal-document-openings`. Retirement requires T1–T4.

