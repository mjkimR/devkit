---
id: PADR-recorded-formal-docs-assessment
title: Recorded formal-docs assessment and reimplementability review
summary: "For reconcile records, we require design, domain and operations coverage (related_* IDs or a formal_docs none reason) when a commit newly resolves a record, checked by RULE-reconcile-contract, plus reviewer reimplementability findings, accepting one field and more review."
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

`ADR-formal-document-delivery-integration` keeps the formal assessment in existing records under explicit semantic
review and rejected a runtime impact manifest as a second registry that cannot prove source agreement. A new check
has to stay inside that decision: it may make a skipped role visible, never claim the impact is right.

## 2. Decision Drivers

- A skipped formal-document assessment is visible to a check or an independent reviewer.
- Existing records stay valid without a migration, cutoff date or setting.
- No new blocking mechanism while no ordinary spec has run under the formal-document steps.
- The record keeps the "bounded unaffected reason" model and never requires an empty document.

## 3. Considered Options

- **Keep the body-only assessment**: no cost, but nothing shows when it is skipped.
- **Reviewer questions only**: visible at `medium` and `high`, but `low` and a skipped reviewer call leave no trace.
- **A new `formal_docs` field holding IDs or reasons per role**: visible, but its IDs would get no existence check,
  alias repair or incoming references.
- **Role coverage in the existing `related_*` fields plus a `formal_docs` reason field, checked by
  `RULE-reconcile-contract`, with reviewer classes**: a skip fails the commit gate at every effort, IDs reuse
  existing reference checks and the reviewer checks content; costs one frontmatter field for reasons.
- **A date cutoff for old records** instead of the newly-resolved condition: needs a constant or setting and still
  re-checks historical records on explicit runs.

## 4. Decision Outcome

Chosen: role coverage through `related_*` IDs or `formal_docs` reasons, with reviewer classes, required only when a
commit newly resolves the record.

- Each of the design, domain and operations roles of a `reconcile.md` is covered by a nonempty `related_designs`,
  `related_domains` or `related_operations` list, or by `formal_docs.<role>: "none: <reason>"` with at least 20
  non-whitespace characters, never both. → RULE-reconcile-contract guide §2 (planned update)
- A snapshot run reports an uncovered role on a `resolved` record that the diff changes and that no parent of the
  commit has `resolved` (the base, and in a staged run any `MERGE_HEAD`, `CHERRY_PICK_HEAD` or `REVERT_HEAD`); other
  runs check a present `formal_docs` for form only. → `CAP-GOV-spec-rules` (planned update)
- `reconcile-reviewer` reports, for what `diff_scope` adds or changes: recorded coverage the diff contradicts (P1);
  a new persisted format, identity derivation or ordering without a statement in its owner (P2); a new code without
  a documented trigger condition (P2); new capability text that restates mechanism (P3).
  → `CAP-DLV-delivery-workflows` rule 15 (planned update)
- The detailed assessment stays in the reconcile body; the frontmatter indexes it. → `CAP-DLV-delivery-workflows`
  rule 9 (planned update)

This is compatible with `ADR-formal-document-delivery-integration`: the coverage lives in the existing record and
existing relation fields, adds no registry, and leaves semantic agreement with the author and the reviewer.
The newly-resolved condition meets the second driver through the rule's existing base comparison, extended to merge parents; reusing the
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
