---
id: PADR-milestone-closure-confirmations
title: Milestone closure through two current confirmations
summary: Milestone closure uses two current user confirmations in its body and the existing Backlog status edit, without a delivery graph or new evaluator.
proposal: PROP-deterministic-milestone-completion
status: draft
created_at: 2026-10-21
---

# [PADR-milestone-closure-confirmations] Milestone closure through two current confirmations

- **Status**: Draft
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`ADR-milestone-documents` uses user-owned Backlog status edits, while its member/branch review assumes SPEC
membership. `PROP-unit-dependencies-and-milestone-scope` establishes direct PROP-only membership. Closure must
fit that model without retaining delivery lineage after handoff. Proposal disappearance cannot certify completion.

## 2. Decision Drivers

- Keep the high-level milestone a collaborative scope document.
- Confirm both decomposition and settlement without duplicating work records.
- Preserve the user's authority over scope and transitions.
- Make stale confirmations unusable without building an automatic evaluator.

## 3. Considered Options

| Option | Cost and limitation | Decision |
| --- | --- | --- |
| Conversation only | No new representation, but the milestone does not retain its closure assertions | Not selected |
| Two plain body assertions and fresh Backlog decision | Small durable record; semantic correctness remains a user/agent review | Selected |
| Typed frontmatter plus close command and scope fingerprint | Adds parsing, invalidation and command contracts; still cannot prove missing work delivered | Excluded without demonstrated need |

## 4. Decision Outcome

Use the milestone body section `Completion review` with plain `Decomposition: pending` and
`Direct proposal work: pending` statements. Record both as `confirmed` with `status: done` in the same Backlog
commit after the user confirms the concrete current close candidate. These are durable assertions rather than
work items. No separate approval, per-item checklist, new schema, command or stored evidence ledger is introduced.

The first confirmation says the intended scope has been sufficiently decomposed; the second says directly associated
work is delivered or explicitly removed from the agreed scope. Both depend on the milestone's exit condition being
met for that scope. Focused implementation/Git inspection resolves uncertainty; unknown evidence remains open.
A missing PROP, rejection, handoff or reassignment never proves implementation. No milestone identity travels to SPEC.

A goal, exit condition, non-goal or direct membership change clears both assertions. Stored assertions are not
standing authorization: every close requires a concrete approved candidate. If material scope, membership or relevant evidence changes
before writing, review and confirmation repeat. After interruption, establish the approved candidate and recheck
those facts; unchanged authorization persists. Ask again only if facts changed or the approved candidate/evidence
cannot be established. A pause or context compaction alone is not an invalidation event. A scope
extension to done requires a user-owned reopen to active with pending assertions, or a separate milestone.
Pure formatting changes do not invalidate; unchanged done is a no-op; existing done records need no migration.

Development promotes this as the follow-on decision to the prerequisite's actual milestone ADR, preserving its
unit ordering and PROP-only membership. It replaces the old exhaustive branch review with focused evidence and
adds the explicit planned-to-done and user-owned reopen cases; activation/drop authority and lookup/history remain.

## 5. Consequences

Shipped milestone template, Backlog and orientation instructions and their contracts describe the procedure.
Guidance tests cover both positive and blocked cases. There is no automatic delivery guarantee and no claim that
body text validates implementation. Optional future automation requires a demonstrated failure beyond this procedure.
