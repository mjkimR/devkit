---
id: PROP-formal-doc-authoring-checkpoints
title: 'Formal documentation checkpoints: route facts, review reimplementability, record assessments'
summary: Make formal documentation get filled during ordinary delivery by adding fact-type routing, a reconcile formal-docs assessment field, reimplementability questions for the reconcile reviewer, a capability observable-contract rule and a reference template.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
  excludes:
    - handbook/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-doc-authoring-checkpoints] Formal documentation checkpoints: route facts, review reimplementability, record assessments

## 1. Background & Hypothesis

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
- 6 of 258 `reconcile.md` files name a formal document, all from the dedicated coverage specs;
- routing exists per responsibility (`CAP-DOCS-documentation-ownership` §3.1 rule 5), not per fact type;
- nothing says what stays out of a capability;
- reference pages have no template.

Hypothesis: guidance that routes each fact type to its owner, plus two checkpoints that make a skipped assessment
visible, gets formal documents written during ordinary delivery without a periodic sweep. The checkpoints are a
recorded assessment and an independent reviewer question.

The formal-document steps in plan, review and sync landed on 2026-11-16, so no ordinary spec has run under them yet.
Planning should keep the change proportionate to that.

## 2. Technical Spike Questions

- **Q1**: Where does the fact-type routing table live? Keep `CAP-DOCS-documentation-ownership` §3.1 canonical and
  project it into `living-spec-writing.md`, or the reverse? Which fact types and owners belong in it?
- **Q2**: What shape does a `formal_docs` assessment in `reconcile.md` take? Options are one entry per role with
  targets or `none: <reason>`. Which rule or check validates it, and how do existing records stay valid
  (`spec_progress` or the reconcile frontmatter owner)?
- **Q3**: Which reconcile-reviewer finding classes carry severity? Candidates are: a missing assessment; a new
  persisted format, identity derivation or ordering without a DESIGN statement; a new code without a documented
  condition; capability text that restates mechanism. Do they block `resolved`?
- **Q4**: What does the capability "observable contract only" rule say, and does it enter the capability template
  as guidance only?
- **Q5**: Add a reference page template (Code / Level / Condition / Fix) and its writing section. Does it apply to
  existing reference pages, or only to new and edited ones?
- **Q6**: Should the DESIGN datasheet section become required when the mechanism persists data, and how is
  "persists data" stated?
- **Q7**: A deterministic rule that every declared advisory code has a documented condition is deferred to a
  follow-up once the reference table shape exists. Confirm the deferral and record the follow-up.

## 3. Proposed Design & Impact

- Docs bundle: fact-type routing in the writing instructions; a capability observable-contract rule; a reference
  template and writing guidance; DESIGN datasheet guidance.
- Spec bundle: a `formal_docs` assessment in the reconcile record schema (spec-sync) with its check;
  reimplementability finding classes in `reconcile-reviewer`; matching wording in spec-plan and spec-review where
  needed.
- `CAP-DOCS-documentation-ownership` and the delivery capabilities that own the reconcile record and reviewer are
  updated to match.
- Bundle sources change, so `devkit sync` and rules and tests for any schema check apply. No change to existing
  formal documents or reference pages beyond what a new check requires.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1-Q7 and the spec boundaries; acceptance hands off to Development and integrates locally under
  `dev-integration=auto`.
- Retire when the guidance and checkpoints land. Evaluate the effect after a few ordinary specs, before adding the
  deferred deterministic code-condition rule.
