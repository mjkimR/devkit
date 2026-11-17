---
id: PROP-formal-doc-padding-trim
title: Trim padding from formal document guidance and documents
summary: Remove guidance and template elements that duplicate rules, frontmatter or other owners, narrow the Maintenance section to update triggers, and apply the same standard to the existing design, domain and operations documents.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-17
target_area: documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/
    - packages/devkit-spec/tests/integration/bundles/spec/test_formal_doc_checkpoints_guidance.py
    - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    - docs/designs/
    - docs/domain/
    - docs/operations/
  excludes:
    - handbook/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-doc-padding-trim] Trim padding from formal document guidance and documents

## 1. Background & Hypothesis

Two read-only audits of the formal documentation, one of the authoring assets and one of the 13 existing design,
domain and operations documents (1,063 lines), found that most padding in the documents is induced by the
templates and writing instructions:

- `## Authority boundary` requires a stock disclaimer ("transfers no normative statement", "routes and owns no
  recovery") that is true of every document of the kind, and documents fill it by re-listing the owners already in
  their domain or operations table.
- `## Maintenance and next action` mixes the one fact nothing else holds (which source change makes the document
  stale) with "next read" pointers that repeat frontmatter `related_*` and the authority boundary; the broad name
  also attracts misplaced body content (`OPS-distribution-sync` keeps a `RECOVERY_BLOCKED` routing rule there, two
  DOMAIN documents keep their per-question owner lines there).
- The design, domain and operations writing instructions repeat path, ID and frontmatter steps that
  `RULE-spec-format`, `RULE-id-convention` and `RULE-code-entrypoints` already enforce, and copy about six identical
  steps across the three files that `living-spec-writing.md` and `CAP-DOCS-documentation-ownership` §3.3 state again.
- `CAP-DOCS-documentation-ownership` has two overlapping routing tables (§3.1 rules 5 and 7) plus a prose copy in
  `living-spec-writing.md`, and §4 restates the template layout, so every template edit forces a capability edit.
- Smaller items: an unused capability template §4 scaffold (0 of 59 capabilities use it), a capability Summary comment
  that asks to repeat the frontmatter `summary`, a YAML-parser install note in `document-writing.md` that the advisory
  already carries, several "the selected development approach defines …" sentences that give no action, the lead and
  datasheet rules restated in template and instruction, a domain worked example that the template calls optional and
  the instruction requires, file-path comments restating `RULE-id-convention`, and `---` separators in the use case and
  UX templates.

In the documents, about 130–150 lines (13%) are padding beyond the Maintenance sections: generic authority
boundaries, repeated "non-normative" and "example executes nothing" disclaimers, lead paragraphs ending in a "This
entry …" restatement of the summary, prose duplicating a table in the same document, a capability table re-stated in
`DESIGN-proposal-handoff`, about 20 private helper names that churn, and `DESIGN-distribution-transactions`, which is
almost entirely a wrapper around `DESIGN-distribution-file-directory-replacement`.

Hypothesis: removing the elements that induce padding, then applying the same standard once to the existing
documents, makes formal documents shorter to write and read without losing any fact a reader acts on.

Checked and kept: use case sections (parsed by rules), operations "Normal-state observation", the problem-first lead,
the domain relationship table, the reference template, ADR drivers and confirmation.

## 2. Technical Spike Questions

- **Q1**: What does the narrowed section say? Rename `## Maintenance and next action` to `## Maintenance` (or
  `## Update triggers`) holding only the source change that makes the document stale, naming public entry points or
  codes; keep a "next read" only when frontmatter and the authority boundary lack it, or drop it?
- **Q2**: What does `## Authority boundary` keep? Proposal: only what the evidence or document cannot conclude beyond
  its table (domain, operations) or what the design does not settle (design), with no stock disclaimer.
- **Q3**: Merge the two `CAP-DOCS-documentation-ownership` routing tables into one fact-type table and keep the
  equality test on that single table; which rows move?
- **Q4**: How far do the per-kind writing instructions shrink: path line, lead focus, body sections, closing, and a
  pointer to `living-spec-writing` plus `devkit rules check` for the shared steps?
- **Q5**: Domain worked example: optional or required? Pick one and align template and instruction.
- **Q6**: Retire `DESIGN-distribution-transactions` by folding its two useful lines into
  `DESIGN-distribution-file-directory-replacement`; which inbound references need repointing (`devkit docs refs`)?
- **Q7**: Private helper names in design documents: keep public entry points, use cases and advisory codes, describe
  private steps in words. Is any private name load-bearing for a reader (e.g. a worked example)?

## 3. Proposed Design & Impact

- Docs bundle: templates (design, domain, operations, capability, usecase, ux) and instructions (design, domain,
  operations, living-spec, document, capability, usecase, ux, milestone writing) lose the duplicated and inactive
  elements above; the narrowed Maintenance and Authority boundary sections replace the current ones.
- `CAP-DOCS-documentation-ownership`: one routing table, §4 reduced to "the docs bundle supplies templates and writing
  instructions", §3.2 closing prose cut to its rules, §3.3 updated to the new section contracts.
- The 13 existing design, domain and operations documents follow the new standard; `DESIGN-distribution-transactions`
  is retired with references repointed.
- Tests pinning the changed phrases (`test_formal_doc_checkpoints_guidance.py`, template pins) are updated; bundle
  sources change, so `devkit sync` and the generated check apply.
- Out of scope: the ADR template and decision-writing (`PROP-adr-body-metadata-removal`), capability and use case
  documents themselves, and any rule change.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1–Q7 and the spec boundaries; acceptance hands off to Development and integrates locally under
  `dev-integration=auto`.
- `PROP-adr-body-metadata-removal` touches the same docs bundle; the two units are integrated sequentially.
- Retire when the guidance and the document cleanup land.
