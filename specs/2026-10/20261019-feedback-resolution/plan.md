---
id: PLAN-feedback-resolution
spec: SPEC-feedback-resolution
---

# Technical Plan: `SPEC-feedback-resolution`

## 1. Constitution & Invariant Review

Package layering is unchanged; no devkit-advisory API changes. Record the lifecycle policy in a new ADR, keeping
accepted storage/roadmap decisions intact. Capture remains separate from task-authorized resolution and hygiene.

## 2. Architecture Overview & Impact

- Add resolved to proposal feedback validation; use existing generic document status discovery and handoff routing.
- Keep source feedback as full-ID Markdown references, retained by existing proposal-body carry and spec drafting.
- Clarify capture/template/sweep and hygiene semantics; add task entry and common completion procedures, with spec
  reconciliation and session workflow/role guidance explicitly invoking them. Add source paths to task boundaries.
- Reflect semantics in harness, document model, delivery workflows and proposal-incubation contracts.
- Update only the motivating stale summary-length feedback after confirming its implementation and boundary tests.

## 3. Failure Modes

Handoff must accept resolved without dropping its record or mutating its state. Partial work cannot claim resolution;
failed verification retains the original state. A later code change invalidating the resolution requires rechecking it
before completion. No repository-wide search may silently close unrelated observations.

## 4. Verification & Test Plan

Extend existing mixed-state handoff tests and add source-reference preservation and explicit list filter coverage.
Run the summary-length regression tests as evidence for the motivating feedback. Run just lint-check devkit-spec,
just check devkit-spec, just test-affected and a package build, plus cumulative governance checks. Review instruction
consistency and preserve budgets; medium independent code review and reconcile verification validate the actual diff.
