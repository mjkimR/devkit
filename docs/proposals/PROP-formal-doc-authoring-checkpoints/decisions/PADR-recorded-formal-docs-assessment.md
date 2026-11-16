---
id: PADR-recorded-formal-docs-assessment
title: Recorded formal-docs assessment and reimplementability review
summary: For reconcile records, we require a formal_docs assessment per design, domain and operations role when a diff newly resolves a record, checked by RULE-reconcile-contract, and give reconcile-reviewer reimplementability findings, accepting one field and more review.
proposal: PROP-formal-doc-authoring-checkpoints
# supersedes: [ADR-<slug>]   # write Supersedes in part `ADR-<slug>`: <the replaced clauses>. in Decision Outcome
status: draft
created_at: 2026-11-16
---

# [PADR-recorded-formal-docs-assessment] Recorded formal-docs assessment and reimplementability review

- **Status**: Draft
- **Date**: 2026-11-16

---

## 1. Context & Problem Statement

`spec-plan`, `spec-review` and `spec-sync` ask for a design, domain and operations assessment in plan, review and
reconcile bodies, but nothing checks that it was made. The reconcile record has only `targets`, `RULE-reconcile-contract`
checks only their form and diff evidence, and `reconcile-reviewer` looks for behavior, capability and constraint
changes, never for persisted formats, identity derivations, orderings or code conditions. A skipped assessment is
invisible, and 260 existing records were written without one.

## 2. Decision Drivers

- A skipped formal-document assessment is visible to a check or an independent reviewer.
- Existing records stay valid without a migration, cutoff date or setting.
- No new blocking mechanism while no ordinary spec has run under the formal-document steps.
- The record keeps the "bounded unaffected reason" model and never requires an empty document.

## 3. Considered Options

- **Keep the body-only assessment**: no cost, but nothing shows when it is skipped.
- **Reviewer questions only**: visible at `medium` and `high`, but `low` and a skipped reviewer call leave no trace.
- **Recorded `formal_docs` field checked by `RULE-reconcile-contract`, plus reviewer classes**: a skip fails the
  commit gate at every effort and the reviewer checks content; costs one frontmatter field.
- **A date cutoff for old records** instead of the newly-resolved condition: needs a constant or setting and still
  re-checks historical records on explicit runs.

## 4. Decision Outcome

Chosen: the recorded `formal_docs` field with reviewer classes, required only when a diff newly resolves the record.

- `reconcile.md` frontmatter carries `formal_docs` with the keys `design`, `domain` and `operations`; each value is a
  nonempty list of affected IDs with the role's prefix or `none: <reason>` of at least 20 non-whitespace characters.
  → RULE-reconcile-contract guide §2 (planned)
- A snapshot run reports a `resolved` record that the diff changes, whose base version is absent or not `resolved`
  and which lacks `formal_docs`; other runs check a present value's form only. → `CAP-GOV-spec-rules` (planned
  update)
- `reconcile-reviewer` reports, for what `diff_scope` adds or changes: a `formal_docs` value the diff contradicts
  (P1); a new persisted format, identity derivation or ordering without a statement in its owner (P2); a new code
  without a documented trigger condition (P2); new capability text that restates mechanism (P3).
  → `CAP-DLV-delivery-workflows` rule 15 (planned update)
- The detailed assessment stays in the reconcile body; the field indexes it. → `CAP-DLV-delivery-workflows` rule 9
  (planned update)

The newly-resolved condition meets the second driver through the rule's existing base comparison; reusing the
existing reconcile severities meets the third.

## 5. Consequences

- Positive: every new spec records an assessment for all three roles, and the reviewer has named questions for
  reimplementability gaps.
- Negative: one more frontmatter field per spec, and P2 findings that need a fix or a waiver reason.
- Risk: `none:` reasons written by rote; the reviewer's contradiction class is the only defence.
- Follow-up: once the reference code table shape has landed and five ordinary specs have completed under these
  checkpoints, evaluate them before proposing a rule that every declared code has a documented condition.

## 6. Confirmation

`RULE-reconcile-contract` and its tests; the `reconcile-reviewer` contract at `medium` and `high` review.
