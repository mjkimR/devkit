---
id: PLAN-delete-resolved-feedback
spec: SPEC-delete-resolved-feedback
---

# Technical Plan: `SPEC-delete-resolved-feedback`

## 1. Constitution & Invariant Review

The resolved-feedback portions of `ADR-closed-feedback-compacts-into-per-area-records-with-aliases` and `ADR-recording-looks-up-existing-feedback-of-every-status-first` require a superseding decision. Active references remain strict; historical unresolved feedback references are deliberately exempt.

## 2. Architecture Overview & Impact

The spec bundle owns compaction and recording guidance. The docs package owns reference validation. No new feature dependencies are needed. Reconcile capability contracts and decision records after implementation.

## 6. Verification & Test Plan

Test guidance for both deletion and retained outcomes, and test the reference rule against historical and active documents. Run relevant tests, `just lint-check`, `just check`, `just test-affected`, and governance checks.
