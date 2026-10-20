---
id: ADR-feedback-terminal-outcomes
title: Close feedback at promotion or direct resolution
summary: "Promotion and direct verified resolution are terminal feedback outcomes; only open feedback remains actionable."
status: accepted
created_at: 2026-10-20
supersedes: ADR-feedback-resolution-lifecycle
proposal: SPEC-feedback-terminal-status
---

# [ADR-feedback-terminal-outcomes] Close feedback at promotion or direct resolution

## 1. Context

Routing an observation to follow-up work already transfers its tracking responsibility. Requiring that work to
revisit promoted feedback duplicates tracking and confuses feedback closure with implementation completion.

## 2. Decision

- Only `open` is actionable feedback backlog. `promoted` is terminal once identified follow-up work receives the
  observation; it does not claim that work is implemented. Progress belongs to the destination, and its completion
  MUST NOT change the source to `resolved` merely because the work finishes.
- `resolved` is terminal for an observation directly addressed and verified without promotion. An authorized session
  or spec task may resolve its explicitly linked open sources with outcome and concrete verification evidence.
  Partial, deferred or unverified direct fixes stay open. `dismissed` and `forwarded` retain their terminal meanings.
- Source FB IDs remain traceability. Terminal sources require no completion disposition, re-verification or write
  scope. Implicit worker source scope includes only committed open sources; explicit authorized task boundaries
  remain independent. The Host handles open-source dispositions outside a delegated worker's write scope.
- Capture and sweep create open observations and never change status. Source resolution of direct fixes does not
  depend on a hygiene invocation, capture settings or the sweep stage. A task rechecks its own new resolution if
  later changes invalidate its evidence before completion; this does not reopen pre-existing terminal sources.
- Preserve all existing statuses and handoff/archive handling. Do not migrate historical feedback statuses.

## 3. Alternatives and consequences

Keeping promoted-to-resolved transitions would duplicate follow-up lifecycle tracking. Using promotion for direct
fixes would erase the distinction between routing and verified repair. Separate terminal routes retain that
meaning while limiting feedback review to open items. A promoted record cannot establish implementation success;
read its destination for that evidence. Existing status-filtered discovery remains available for all records.
