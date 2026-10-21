---
id: PADR-source-bound-review-reports-and-explicit-lifecycle-approval
title: Source-bound review reports and explicit lifecycle approval
summary: Bind proposal review reports and native approval to an exact committed source, and coordinate explicit acceptance, merge and optional handoff with bounded recovery.
proposal: PROP-proposal-review-and-approval
status: draft
created_at: 2026-10-21
---

# [PADR-source-bound-review-reports-and-explicit-lifecycle-approval] Source-bound review reports and explicit lifecycle approval

- **Status**: Draft
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`PROP-proposal-review-and-approval` needs a readable design briefing without embedding full English source in a
native form. Approval must still bind the actual plan, effects and configured guards. Shared reports expire and
Git/worktree operations cannot form a cross-process transaction.

## 2. Decision Drivers

Exact review identity, explicit user authority, local MCP priority, bounded retry, existing integration ownership,
and a read-only viewer outweigh automatic regeneration or invisible recovery.

## 3. Considered Options

| Option | Benefit | Cost and decision |
| --- | --- | --- |
| Keep raw proposal in every form | No new reader | Repeats full English source, loses PADR focus; rejected. |
| Commit localized reports | Existing Git viewer works | Pollutes tracked English documentation and creates report/source commit recursion; rejected. |
| Immutable shared report plus scoped native composition | Concise review, exact source, one decision | Requires explicit TTL refresh and partial-state recovery; selected. |
| Generic approval token or synthesized confirmation callback | Small apparent integration change | Expands authority across tools and restarts; rejected. |
| Full atomic merge/setup rollback | Appears simple to users | Cannot undo arbitrary setup or safely delete user changes; rejected. |
| Viewer performs approval and regeneration | One interactive surface | Violates read-only and existing approval ownership; rejected. |

## 4. Decision Outcome

Use the proposal's report identity and exact-source validation contract. The agent authors a language-specific
briefing; deterministic services validate its structure and references and store it through the shared adapter.
The Host owns semantic comparison. Storage and presentation confer no approval. Publish after final worker commit
to avoid a report/commit cycle. TTL regeneration occurs outside a pending form and always requires fresh review.

A native `spec_plan_accept` form explicitly authorizes acceptance commit, checked local merge, disclosed cleanup and
optional handoff. `accept_only` and `accept_and_handoff` have distinct effects. Holds are nonmutating, not rejection.
Existing integration owns readiness/policy and exposes only a typed in-process composition seam; no public token,
forged form reply or generic bypass is added. Use exact base equality, narrower than general integration's permitted
moving-target behavior. Required-PR remains on the separately approved existing flow.

Return truthful step progress after partial failure. A partial return/restart grants no remaining authority; fresh
inspection and approval describe only remaining effects. No rollback removes user changes. Standalone handoff uses
an exact accepted-base report and remains explicitly approved.

Promote this PADR with a narrowly scoped supersession of `ADR-read-only-local-server-over-git-refs`: permit only
registered-local-adapter, exact-generation `proposal-review` artifact reads outside Git. Retain Git-only ordinary
endpoints, loopback/Host/no-CORS protections, sanitization, no write/approval endpoints and no server regeneration.
No arbitrary filesystem or remote URL lookup is permitted. The viewer remains optional and never auto-starts.

## 5. Consequences

The shared adapter proposal must be accepted and implemented first. Host-specific URI clickability and native form
rendering need separate live evidence. More modules participate, but responsibilities stay in their domain packages.
Local missing MCP tools pause dependent work and request connection. Cloud CLI and MCP-invisible template work stay
separate. This proposal changes no current authority until accepted, implemented and reconciled.
