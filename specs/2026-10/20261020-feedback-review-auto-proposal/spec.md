---
id: SPEC-feedback-review-auto-proposal
title: Clarify recurring findings versus defects introduced by fixes
summary: "Classify recurrence by the same failure condition while preserving review escalation for incomplete fixes."
status: completed
created: 2026-10-20
related_capabilities: [CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-review-auto-proposal] Clarify recurring findings versus defects introduced by fixes

## 1. Problem Statement

Reviewers lack a concrete distinction between recurrence of an earlier defect and a different defect introduced
by its fix. Classification must preserve the bounded loop's escalation without treating causal connection alone
as recurrence. This clarifies `ADR-bounded-high-effort-review-loop` without changing its marker or stop conditions.

## Source feedback

- `FB-recurs-marker-on-fix-introduced-findings`: directly clarify recurrence criteria and examples.

## 2. User Stories

- As a reviewer, I want to compare failure conditions so I apply recurrence consistently after a fix.

## 3. Non-Goals

- Scope Excluded: new markers, parser/schema changes, altered severity, round limits or waiver rules.
- Scope Excluded: implementing automatic integration. `PROP-policy-authorized-integration` is a separately drafted
  follow-up on this branch and remains unaccepted.

## 4. Acceptance Criteria

### [AC-01] The same defect persists or returns

- Given an earlier finding and an attempted fix,
- When the same failure condition remains, including an incomplete fix, or returns,
- Then guidance requires the existing `recurs:` marker with the earlier finding reference and retains escalation.

### [AC-02] A fix introduces a distinct failure

- Given the earlier failure condition is resolved and a fix introduces a different failure condition,
- When the reviewer reports that separate defect,
- Then guidance treats it as a new finding, not recurrence solely because the fix caused it or touched the same place.

### [AC-03] Evidence and existing exclusions

- Given a later-round finding,
- When the reviewer assigns recurrence,
- Then guidance requires the shared failure condition to be explained, preserves the out-of-round-scope exclusion,
  and leaves all existing minor-fix conditions, severity and round-cap rules intact.
