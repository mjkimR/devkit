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
    - packages/devkit-docs/tests/
    - packages/devkit-docs/README.md
    - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    - docs/capabilities/documents/CAP-DOCS-document-model.md
    - docs/decisions/2026-11/20261116-linked-domain-relationship-views.md
    - docs/designs/
    - docs/domain/
    - docs/operations/
    - docs/proposals/PROP-formal-document-templates/
    - .devkit/installation.json
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
their sections (inventory: `materials/template-survey.md` §1):

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

External practice agrees (`materials/template-survey.md` §2): KEP, Rust RFC, PEP 12, Go, MADR and arc42 state the
problem once after the summary and keep any question inside it or as an authoring prompt; scope is set by
exclusions plus pointers to the owning document; guidance sits in comments or a separate guide; table skeletons are
placeholder rows; copy-once systems leave old documents alone and check body sections, if at all, warn-only.

`PROP-design-bundle-layout` changes the canonical paths, the `area` field and support placement in the same
templates and instructions. This proposal follows it, so each file is restructured once against the delivered path
grammar.

## 2. Technical Spike Questions

- **Q1**: Does removing the question section satisfy `CAP-DOCS-documentation-ownership` §3.3, which asks authors to
  state the reader question, or does that clause change with the templates? *Settled: the clause changes;
  `PADR-problem-first-formal-document-openings`.*
- **Q2**: Which of the remaining gaps does this proposal fix: section structure, authority boundary section,
  guidance as comments, table skeletons, the pre-seeded empty `related_*` lists and the missing `status` value
  comment? *Settled: all of them; Planning decisions.*
- **Q3**: Do the five delivered documents change to match the templates, or do the templates only govern documents
  written after them? *Decision needed at `plan-accept`.*
- **Q4**: Is `templates/design-template.md`, the compatibility pointer to `design.md`, removed? State whether any
  released version shipped the older name. *Settled: removed; no tag v0.1.0–v0.1.6 contains it.*

## 3. Proposed Design & Impact

### Planning decisions

- **Q1 — Opening.** `PADR-problem-first-formal-document-openings`: each document opens with the problem it answers
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

### Pending decision (Q3)

Recommended: bring each delivered document into line with each clause of the PADR, keeping its topic headings and
tables:

| PADR clause | `DESIGN-distribution-transactions` | `DESIGN-distribution-file-directory-replacement` | both `DOMAIN-*` documents | `OPS-distribution-sync` |
| --- | --- | --- | --- | --- |
| Problem opening, no question | remove the label; make the lead state the problem | remove the label; add a problem lead | replace `## Question` with a problem lead | already met |
| Authority boundary | add the heading over the existing prose | add the heading over the existing prose | already met | already met |
| Maintenance and next action | already met | already met | add a maintenance trigger to the closing section | add a maintenance and next-action close |

Alternatives: full alignment to the template headings, or no change (the external copy-once practice, which leaves
four documents against the revised SHOULD).

### Assets

Edit the docs bundle sources under `packages/devkit-docs/src/devkit_docs/bundles/docs/` and project them with
`devkit sync`. Start from the templates and instructions as `PROP-design-bundle-layout` delivers them.

### Non-Goals

- No change to paths, identity, frontmatter schema, the `area` field, support placement, status vocabulary or
  relation fields; `PROP-design-bundle-layout` and `ADR-formal-role-document-identities` own those.
- No rule that checks template sections or leftover guidance.
- No per-document template version marker, template variants or separate guide files.

### Expected acceptance evidence

- **T1 — Templates**: The three templates carry no question section, open and close with the headings above, carry
  guidance in HTML comments, ship the domain and operations table skeletons and the `status` and `related_*`
  comments; the docs bundle distribution test passes.
- **T2 — Instructions**: Each writing instruction states the scoping step and agrees with its template and with
  `CAP-DOCS-documentation-ownership` §3.3.
- **T3 — Documents**: The delivered documents agree with the Q3 outcome and pass `devkit rules check`;
  `rg -n '^\*\*Reader question|^## Question' docs/designs docs/domain docs/operations` returns no hit.
- **T4 — Pointer**: `templates/design-template.md` is gone from the bundle and the installed copy;
  `rg -n design-template docs/capabilities docs/architecture docs/development packages` returns no hit, while
  materials, completed specs and other proposals keep their mentions as history. `test_installed_consumer.py`
  instantiates the revised templates.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1–Q4. This stays one S feature proposal and starts Development after
`PROP-design-bundle-layout` delivers its path grammar. If that proposal is rejected, remove `depends_on` and start
from the current templates: the two touch disjoint concerns (paths and `area` against sections and guidance).
Acceptance and handoff follow the existing gates; handoff promotes `PADR-problem-first-formal-document-openings`.
Retirement requires T1–T4.
