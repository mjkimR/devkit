---
id: FB-code-condition-rule-deferred
title: Evaluate a rule that every declared code has a documented trigger condition
scope: repo
kind: change-request
category: missing-capability
target: docs/development/reference/
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-11-17
---

# [FB-code-condition-rule-deferred] Evaluate a rule that every declared code has a documented trigger condition

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `SPEC-formal-doc-authoring-checkpoints` gives new reference code tables the columns
  `Code | Level | Condition | Fix` (docs bundle `templates/reference.md`) and has `reconcile-reviewer` report a new
  code without a documented trigger condition as P2. No deterministic check compares declared codes with documented
  conditions; existing reference pages keep at least eight column sets.
- **Proposed Procedure**: once the reference code table shape has landed and five ordinary specs have completed under
  the formal-document checkpoints, measure how many new codes those specs documented with a condition. If the
  reviewer class alone leaves gaps, propose a rule that every declared code has a row with a nonempty Condition in a
  reference code table.
- **Expected Benefit**: missing code conditions fail a check instead of depending on review.
- **Cost & Risk**: the rule needs a uniform table shape that only new pages have; enforcing it on old pages would
  force a migration that `SPEC-formal-doc-authoring-checkpoints` ruled out.
- **Attempted**: hypothesis; deferred by Planning decision Q7 and `ADR-recorded-formal-docs-assessment` §5.

Restart condition: five ordinary specs completed after `SPEC-formal-doc-authoring-checkpoints`. Expected acceptance
checks: rule tests over a fixture of declared codes and reference tables, and `uv run devkit rules check` reporting
no violation on the pages written after the template landed.

## Evidence

```text
spec.md §3 Non-Goal 2 and §5 "Deferred work"; ADR-recorded-formal-docs-assessment §5 "Follow-up".
```

## Disposition

- **Disposition**: Dismissed: an open item whose only trigger is "after five specs" has no owner that rechecks it, and
  `reconcile-reviewer` already reports a new code without a documented condition as P2 on every change. Raise a new
  feedback item when a review misses an undocumented code condition; that miss is the evidence this rule needs.
