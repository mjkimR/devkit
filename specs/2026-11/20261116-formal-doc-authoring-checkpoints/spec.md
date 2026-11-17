---
id: SPEC-formal-doc-authoring-checkpoints
title: 'Formal documentation checkpoints: route facts, review reimplementability, record assessments'
summary: Make formal documentation get filled during ordinary delivery by adding fact-type routing, a reconcile formal-docs assessment field, reimplementability questions for the reconcile reviewer, a capability observable-contract rule and a reference template.
status: completed
created: 2026-11-16
related_capabilities:
  - CAP-DOCS-documentation-ownership
  - CAP-DOCS-document-model
  - CAP-GOV-spec-rules
  - CAP-DLV-delivery-workflows
related_usecases:
  - UC-keep-the-living-spec-consistent
workflow: sdd-spec-feature
---

# [SPEC-formal-doc-authoring-checkpoints] Formal documentation checkpoints: route facts, review reimplementability, record assessments

## 1. Problem Statement & Motivation

Handed off from proposal PROP-formal-doc-authoring-checkpoints on 2026-11-16. Planning evidence is preserved at
`docs/materials/2026-11/20261116-formal-doc-authoring-checkpoints/planning-evidence.md`; the record-field decision is
`ADR-recorded-formal-docs-assessment`.

A reimplementability review of 17 capability areas found that the documentation layers are sufficient. The gaps are
content nobody wrote, not missing layers:

- on-disk byte formats and identity derivations (MCP registration entries, host hook groups, shared-artifact files,
  scope-registry tokens, the distribution journal) appear nowhere, although the DESIGN template has an optional
  "Example or datasheet" section;
- ordering and tie-break contracts (rule violation order, search ties, generated topological order) are unstated;
- reference code tables often lack a trigger condition, and their columns differ page by page;
- capability documents carry implementation pseudocode, private formats and duplicated paragraphs that belong in
  DESIGN or nowhere.

The existing guidance already asks for most of this. `spec-plan`, `spec-review` and `spec-sync` ask for a
design/domain/operations assessment, and `design-writing.md` mentions datasheets. Authors still skip it, because the
only reliably present content is what something checks:

- the reconcile record schema has `targets` only;
- `reconcile-reviewer` checks behavior, capability and constraint changes, never formal documents;
- 10 of 260 `reconcile.md` files mention a formal document, all from the 2026-11-16 formal-document specs;
- routing exists per responsibility (`CAP-DOCS-documentation-ownership` §3.1 rule 5), not per fact type;
- nothing says what stays out of a capability;
- reference pages have no template.

Hypothesis: guidance that routes each fact type to its owner, plus two checkpoints that make a skipped assessment
visible, gets formal documents written during ordinary delivery without a periodic sweep. The checkpoints are a
recorded assessment in `reconcile.md` and an independent reviewer question.

## 2. User Stories

- **US-1**: As a developer agent writing documentation, I want each fact type routed to one owner so that formats,
  identity derivations, orderings and code conditions land in the document that owns them.
- **US-2**: As a Host or reviewer, I want a newly resolved reconcile record to show a design, domain and operations
  assessment so that a skipped assessment fails the commit gate instead of passing silently.
- **US-3**: As a reconcile reviewer, I want named reimplementability finding classes so that new persisted formats,
  identity derivations, orderings and codes without a documented owner statement are reported.

## 3. Non-Goals

1. **Scope Excluded**: migrating existing reference pages, capability text or formal documents, or sweeping older
   gaps. Existing `docs/development/reference/` pages keep their tables.
2. **Scope Excluded**: a rule that every declared code has a documented condition. It is handed to Backlog as
   deferred work (§5).
   - **When to Reconsider**: once the reference code table shape has landed and five ordinary specs have completed
     under these checkpoints.
3. **Scope Excluded**: a required DESIGN datasheet section; no check can tell a datasheet from prose.
4. **Scope Excluded**: requiring the coverage on a record the commit does not newly resolve, or in a plain
   (non-snapshot) run. Existing records stay valid without migration, date cutoff or setting.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1 [AC-01]: Fact-type routing and capability guidance in the docs bundle
- **Given** the docs bundle sources
- **When** `living-spec-writing`, `capability-writing`, `design-writing`, `document-writing` and the `capability` and
  `design` templates are read
- **Then** `living-spec-writing` carries the nine-row fact-type routing table, `capability-writing` has a "What stays
  out" section, the capability template §3 comment names the observable-contract-only clause, `design-writing` and the
  design template say a design SHOULD carry a datasheet WHEN its mechanism writes data a later run, another process or
  another tool reads back, and `document-writing` has a "Reference pages" section
- **And** no new docs bundle text cites a document ID of this repository (agent-asset self-containment).

### Scenario 2 [AC-02]: Reference template and its pins
- **Given** the docs bundle
- **When** `devkit sync` projects it
- **Then** `.devkit/managed/docs/templates/reference.md` exists, has no frontmatter, and holds a code table with the
  header `| Code | Level | Condition | Fix |`
- **And** both bundle constitutions list
  `templates/{capability,usecase,ux,decision,milestone,design,domain,operations,reference}.md`, and
  `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` and
  `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py` assert that list and pass.

### Scenario 3 [AC-03]: `formal_docs` form is checked in every run
- **Given** a targeted `reconcile.md` of a current bundle with a `formal_docs` value
- **When** `devkit rules check` runs (plain, `--staged` or `--ci`)
- **Then** `RULE-reconcile-contract` reports one violation at line 1 for each of: `formal_docs` not a mapping; a key
  other than `design`, `domain` or `operations`; a value that is not a string starting `none: `; a reason with fewer
  than 20 non-whitespace characters; a role with both a nonempty `related_designs`, `related_domains` or
  `related_operations` list and a `none:` reason
- **And** a record without `formal_docs` passes the form check.

### Scenario 4 [AC-04]: Coverage is required on a newly resolved record in a snapshot run
- **Given** a staged or ci snapshot whose diff changes a `reconcile.md` with `status: resolved`
- **When** no parent of the commit has that record `resolved` (the snapshot base; in a staged run also each commit in
  `MERGE_HEAD`, `CHERRY_PICK_HEAD` or `REVERT_HEAD` when present)
- **Then** `RULE-reconcile-contract` reports each role covered neither by a nonempty `related_*` list nor by a
  `formal_docs.<role>` reason, and the check exits `1`
- **And** full coverage through `related_*` lists, `none:` reasons or a mix passes.

### Scenario 5 [AC-05]: Coverage is not required elsewhere
- **Given** a record without coverage
- **When** it is `pending`; or it is `resolved` at the base and edited; or a `MERGE_HEAD` commit has it `resolved` in
  a staged run; or it is a completed bundle's record named as an explicit target in a plain run
- **Then** `RULE-reconcile-contract` reports no coverage violation for it.

### Scenario 6 [AC-06]: Existing records stay valid
- **Given** the 260 existing `reconcile.md` records
- **When** `uv run devkit rules check specs/` runs (every record an explicit target)
- **Then** it reports no `RULE-reconcile-contract` violation that the accepted base did not report
- **And** this spec's own `reconcile.md` covers every role and passes
  `uv run devkit rules check --ci --base a7d96154e`.

### Scenario 7 [AC-07]: Spec bundle wording
- **Given** the spec bundle sources
- **When** `spec-sync`, `reconcile-reviewer`, `spec-plan` and `spec-review` are read
- **Then** `spec-sync` step 2's schema shows `related_designs` and `formal_docs` with `none:` reasons and step 1 says
  the frontmatter indexes the body assessment; `reconcile-reviewer` step 2 names the four classes with severities P1,
  P2, P2 and P3, limited to what `diff_scope` adds or changes; `spec-plan` step 3 and `spec-review` step 4 each name
  the persisted formats, identity derivations, orderings and codes the change introduces, routed by the fact-type
  table.

### Scenario 8 [AC-08]: Living Spec agreement
- **Given** the Living Spec after this change
- **When** `CAP-DOCS-documentation-ownership`, `CAP-DOCS-document-model`, `CAP-GOV-spec-rules` and
  `CAP-DLV-delivery-workflows` are read
- **Then** `CAP-DOCS-documentation-ownership` §3.1 has the fact-type table with the same nine rows as
  `living-spec-writing` and an "Observable contract" SHOULD rule; `CAP-DOCS-document-model` counts the reference
  template beside eight formal templates; `CAP-GOV-spec-rules` §3.10 states the coverage check; and
  `CAP-DLV-delivery-workflows` rules 9 and 15 state the frontmatter index and the reviewer classes, citing
  `ADR-recorded-formal-docs-assessment`.

## 5. Design Notes

Planning settled these choices; the reasons are in the preserved Planning evidence and
`ADR-recorded-formal-docs-assessment`.

- **Routing owner**: `CAP-DOCS-documentation-ownership` §3.1 stays canonical with a fact-type table beside the
  responsibility table; `living-spec-writing` carries the same rows without citing the capability, because the bundle
  ships to projects that lack it. An order a consumer sees is a capability rule; internal order is design.
- **Record shape**: role coverage reuses the typed `related_designs`, `related_domains` and `related_operations`
  lists, which already get existence checks and alias repair from `RULE-document-reference`; `formal_docs` holds only
  the per-role `none: <reason>`. The detailed assessment stays in the record body.
- **Merge parents**: the commit gate runs when a conflicted merge is concluded with the HEAD tree as its base;
  checking each in-progress operation head keeps a record resolved on the base branch from refusing that merge.
- **Reviewer severity** reuses the reconcile meanings: contradicted recorded coverage P1, a new persisted format,
  identity derivation or ordering without an owner statement P2, a new code without a documented trigger condition
  P2, new capability text restating mechanism P3. Severity changes no check.
- **Reference template**: `templates/reference.md` has no frontmatter or ID; reference pages are not formal
  documents. It applies to new reference pages and new code tables; a row added to an existing table states its
  condition.
- **Deferred work**: the deterministic code-condition rule goes to Backlog as feedback recorded in this bundle and
  cited from `reconcile.md`.

### Assumptions

- The handoff rewrote the proposal's own ID references to this spec's ID; the ADR's `proposal:` field naming this
  spec is the promoted-ADR form other ADRs use and needs no rewording.
- `PROP-handoff-rewrite-overlap-scheduling` (draft) owns `packages/devkit-spec/tests/`; this spec changes only the
  named test files there, and no sequencing decision is needed while that proposal is a draft.
