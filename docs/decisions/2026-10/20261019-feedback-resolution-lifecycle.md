---
id: ADR-feedback-resolution-lifecycle
title: Separate feedback routing from verified resolution
summary: "Feedback promotion hands an observation to follow-up work; resolution records an implemented and verified fix through spec or session completion."
status: superseded
superseded_by: ADR-feedback-terminal-outcomes
created_at: 2026-10-19
proposal: SPEC-feedback-resolution
---

# [ADR-feedback-resolution-lifecycle] Separate feedback routing from verified resolution

## 1. Context

Capture and hygiene currently keep direct fixes and routed work under the same promoted status. An authorized fix
outside a hygiene session can leave its originating feedback open after verification. Task completion needs source
traceability without treating capture as permission to triage unrelated backlog items.

## 2. Decision

- `open` records an unhandled observation; `promoted` hands it to identified follow-up work; `resolved` means its
  observation was fully addressed and verified; `dismissed` records a reasoned decline; `forwarded` records an
  authorized external submission. Promotion is not proof of a fix.
- Named source FB IDs and the scope received belong in the proposal/spec's `Source feedback` body section, or the
  agreed scope of a session. Handoff carries those references, preserving source statuses. Drafting retains them.
- An authorized implementer resolves fully addressed `open` or `promoted` sources during spec reconciliation or
  session completion, with an outcome and concrete verification evidence in their disposition. No separate hygiene
  invocation is needed. Partial/deferred/unverified sources retain their state and have remaining scope reported.
- Capture and sweep record new observations as open; they cannot resolve unrelated backlog items. Capture settings
  and switching the sweep stage off do not disable source resolution at completion.
- Resolution is verified on the task branch, before normal integration. Handoff alone cannot resolve anything.
  Later changes invalidating evidence require rechecking the task's own resolutions before completion.
- Extend the known statuses in `ADR-planning-feedback-in-proposal`: resolved feedback follows the existing preserved
  materials path at handoff, like other non-open files. Open-file preservation and deletion authority stay intact.

## 3. Alternatives

| Option | Benefit | Cost |
| --- | --- | --- |
| Keep using promoted for fixes | No extra status | Cannot distinguish routing from verified completion |
| Resolve at handoff | State update accompanies proposal retirement | Claims resolution before implementation and verification |
| Resolve explicit sources at completion | Evidence and source status travel with the fix | Requires recording sources at entry and checking them at completion |

Choose the third option. Historical promoted records are not migrated; only explicitly verified items are updated.

## 4. Consequences

The five-status lifecycle is accepted without changing schema versions. Source references use existing Markdown
reference discovery. Session work creates no Unit or new record. Delegated source-file writes require explicit scope;
the Host applies any out-of-boundary updates from verified results. Integration remains a separate approval.
