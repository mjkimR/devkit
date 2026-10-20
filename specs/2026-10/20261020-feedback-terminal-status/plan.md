---
id: PLAN-feedback-terminal-status
spec: SPEC-feedback-terminal-status
---

# Technical Plan: `SPEC-feedback-terminal-status`

## 1. Constitution and invariant review

Supersede `ADR-feedback-resolution-lifecycle` with `ADR-feedback-terminal-outcomes`; retain the old body and update
its supersession metadata. No runtime consumer schema changes. Terminal feedback stays discoverable history.

## 2. Components and design

Align the spec bundle's capture, completion, handoff, delegation and hygiene instructions and the four affected
capabilities. Preserve source IDs for traceability but limit resolution obligations to open directly addressed sources.
Filter worker inspection's implicit source-feedback scope by committed status == open. Explicit task boundaries
remain a separate caller-reviewed source of authority. Unknown status fails closed for implicit writes.
No proposal implementation change is needed: existing handoff already separates open files from preserved terminal files.

## 3. Verification

Exercise committed scope derivation with open, promoted, resolved, dismissed, forwarded and missing/unknown statuses,
including actual edits outside implicit scope and explicit-boundary authorization. Run lint, types, affected tests,
existing handoff tests and cumulative governance checks. Independent medium code and reconcile review verify semantics
across the instructions and capabilities. Review the changed-path list to exclude historical feedback migrations.
