---
id: ADR-feedback-lifecycle
title: Feedback closes at promotion or at direct verified resolution
summary: "For the feedback backlog, we make promotion and direct verified resolution terminal outcomes and keep only open feedback actionable, to separate routing from verified repair without duplicate tracking, accepting that a promoted record never shows whether its follow-up work succeeded."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-feedback-resolution-lifecycle
  - ADR-feedback-terminal-outcomes
---

# [ADR-feedback-lifecycle] Feedback closes at promotion or at direct verified resolution

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: not recorded in the members
- **Involved Components/Capabilities**: not recorded in the members

---

## 1. Context & Problem Statement

Capture and hygiene kept direct fixes and routed work under the same promoted status, and an authorized fix outside a
hygiene session could leave its originating feedback open after verification. Task completion needs source
traceability without treating capture as permission to triage unrelated backlog items. Routing an observation to
follow-up work already transfers its tracking responsibility; requiring that work to revisit promoted feedback
duplicates tracking and confuses feedback closure with implementation completion.

---

## 2. Decision Drivers

- Distinguish routing an observation from its verified repair.
- Source traceability for task completion without treating capture as permission to triage unrelated backlog items.
- No duplicate tracking: follow-up work tracks its own progress once it receives an observation.

---

## 3. Considered Options

- **Keep using promoted for fixes** (rejected by `ADR-feedback-resolution-lifecycle`): no extra status, but cannot
  distinguish routing from verified completion; using promotion for direct fixes would erase the distinction between
  routing and verified repair (`ADR-feedback-terminal-outcomes`).
- **Resolve at handoff** (rejected by `ADR-feedback-resolution-lifecycle`): the state update accompanies proposal
  retirement, but claims resolution before implementation and verification.
- **Resolve explicit sources at completion, promoted sources included** (chosen by
  `ADR-feedback-resolution-lifecycle`; rejected by `ADR-feedback-terminal-outcomes`): evidence and source status travel
  with the fix, but keeping promoted-to-resolved transitions duplicates follow-up lifecycle tracking.
- **Separate terminal routes: promotion and direct verified resolution** (chosen by `ADR-feedback-terminal-outcomes`):
  retains the distinction while limiting feedback review to open items.

---

## 4. Decision Outcome

- Only `open` is actionable feedback backlog. `promoted` is terminal once identified follow-up work receives the
  observation; it does not claim that work is implemented. Progress belongs to the destination, and its completion
  MUST NOT change the source to `resolved` merely because the work finishes. (ADR-feedback-terminal-outcomes)
- `resolved` is terminal for an observation directly addressed and verified without promotion. An authorized session
  or spec task may resolve its explicitly linked open sources with outcome and concrete verification evidence.
  Partial, deferred or unverified direct fixes stay open. `dismissed` and `forwarded` retain their terminal meanings.
  (ADR-feedback-terminal-outcomes)
- Source FB IDs remain traceability. Terminal sources require no completion disposition, re-verification or write
  scope. Implicit worker source scope includes only committed open sources; explicit authorized task boundaries remain
  independent. The Host handles open-source dispositions outside a delegated worker's write scope.
  (ADR-feedback-terminal-outcomes)
- Capture and sweep create open observations and never change status. Source resolution of direct fixes does not
  depend on a hygiene invocation, capture settings or the sweep stage. A task rechecks its own new resolution if later
  changes invalidate its evidence before completion; this does not reopen pre-existing terminal sources.
  (ADR-feedback-terminal-outcomes)
- Preserve all existing statuses and handoff/archive handling. Do not migrate historical feedback statuses.
  (ADR-feedback-terminal-outcomes)

---

## 5. Consequences

- **Positive**: feedback review is limited to open items; routing and verified repair keep separate meanings.
- **Negative / Risks**: a promoted record cannot establish implementation success; read its destination for that
  evidence.
- **Follow-ups**: existing status-filtered discovery remains available for all records.

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_feedback.py` covers the feedback states
  (`open`, `promoted`, `resolved`, `dismissed`, `forwarded`) and that only `open` items are carried as actionable.
- Review only for source-feedback resolution at completion; `RULE-document-reference` checks feedback ID resolution.
