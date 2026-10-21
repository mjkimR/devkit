---
id: ADR-policy-delegated-decision-boundaries
title: Policy-delegated delivery decision boundaries
summary: "Proposal acceptance, Development handoff and Development result acceptance are separate decision boundaries, each delegated by ask or auto policy without redundant task-intent consent."
status: accepted
created_at: 2026-10-21
---

# [ADR-policy-delegated-decision-boundaries] Policy-delegated delivery decision boundaries

## 1. Context & Problem Statement

A decision boundary identifies which effects are authorized. It does not require a human interruption in every
execution. Human-only acceptance rules create duplicate consent requests and conflate internal worker sequencing
with user decisions. Direction acceptance and starting Development also need to remain independently schedulable.

## 2. Decision Drivers

- Retain the three main scope decisions while allowing deliberate policy delegation.
- Permit an accepted proposal to wait in Backlog, or accept and start it in one user decision.
- Preserve exact source, report, readiness, host permission and recovery guards under automatic execution.

## 3. Considered Options

- Always ask at every boundary. This repeats authorization even when the owning project delegates it.
- Remove decision boundaries. This loses the distinction between accepted direction and scheduled Development.
- Keep independent boundaries with ask or auto policy. Selected.

## 4. Decision Outcome & Rationale

The main boundaries are `plan-accept`, `proposal-handoff`, and `dev-integration`, each defaulting to `ask` and
allowing `auto`. `plan-intent` remains an authorization record rather than a fourth mandatory interruption: an
explicit task instruction already supplies intent. It also permits policy satisfaction. No unrequested task is
implicitly scheduled. This decision replaces the human-only policy restriction described in
`ADR-direct-acceptance-command-and-handoff-guard`; its validated acceptance writer and carry guards remain in force.

Planning acceptance includes its checked merge; it does not consume Development result approval. A native form can
approve acceptance and handoff together. Auto authority must originate in the owning base configuration and remain
in the prospective source. A branch cannot grant itself authority or silently revoke it during execution. Policy
records name policy, never user. Local delegation grants no publication rights or host permission bypass.

The Host decides sequential or parallel internal tasks, reviews and fixes within the authorized scope. Splitting
workers creates no extra user approval requirement. Changes to authorized goals, scope or constraints require fresh
authority. Completion checks and partial-effect recovery remain mandatory under both ask and auto.

## 5. Consequences

Policy introspection exposes all three boundaries. Native services evaluate each independently; acceptance may
finish while handoff waits. Tests cover mixed policies, declines, stale state, source-only auto and revocation.
