---
id: PADR-remove-plan-intent-gate
title: Remove the task intent approval gate
summary: "For instructed SDD work, we remove the plan-intent gate and its records, to avoid duplicate authorization bookkeeping, accepting that task authorization is enforced by agent guidance."
proposal: PROP-remove-plan-intent-gate
supersedes: [ADR-delivery-approval-and-lifecycle-authority, ADR-proposal-acceptance, ADR-delivery-classification, ADR-roadmap-and-milestones-ledger, ADR-ux-screens]
status: draft
created_at: 2026-11-10
---

# [PADR-remove-plan-intent-gate] Remove the task intent approval gate

## 1. Context & Problem Statement

An explicit task instruction already authorizes its stated intent. The SDD `plan-intent` gate adds a record and
special handling in proposal acceptance, handoff and policy reporting without deciding an unresolved question.

## 2. Decision Drivers

- Preserve explicit authorization and the three later approval boundaries.
- Remove duplicate bookkeeping and its lifecycle-specific code.
- Keep historical Units readable without migration.

## 3. Considered Options

- Keep the gate: preserves compatibility but retains duplicate records and special cases.
- Default the gate to `auto`: avoids waiting but retains gate definitions, policy handling and carry logic.
- Remove the SDD gate: removes those costs while agent guidance continues enforcing explicit task authorization.

## 4. Decision Outcome

- SDD workflows do not declare or request `plan-intent`, and new work creates no intent approval record.
  → `CAP-DLV-delivery-workflows` rule 6 (MUST).
- Explicit task instructions authorize only their stated scope; queued Backlog work is never implicitly started.
  → `CAP-DLV-project-policy` rule 4 (MUST).
- The three boundaries `plan-accept`, `proposal-handoff` and `dev-integration` retain their existing policies.
  → `CAP-DLV-project-policy` rule 4 (MUST).
- Intent stage IDs remain stable, and existing valid intent decisions remain inert history without migration.
  → `CAP-DLV-delivery-workflows` rule 6 (MUST).
- Proposal handoff carries `plan-accept` but does not require or carry `plan-intent`.
  → `CAP-DLV-proposal-planning` rule 12 (MUST).
- Configured `plan-intent` is reported as an ignored retired SDD key, without changing generic custom gate semantics.
  → `CAP-DLV-project-policy` rule 4 (MUST).
### Replaced clauses

This decision replaces only the following gate-dependent clauses. Each earlier ADR remains accepted with a
partial-supersession pointer; its unrelated decisions remain in force.

- `ADR-delivery-approval-and-lifecycle-authority`: Task intent's gate/record requirement is removed; explicit task
  authorization and all later boundary policies remain.
- `ADR-proposal-acceptance`: Both gates in one request and Eligibility checked by the tool lose their intent gate,
  intent-record prerequisite and pending-intent special case. Explicit `plan-accept`, direct-acceptance eligibility,
  visibility, sweep, acceptance audit and handoff guard remain; effort hints are stated at intake.
- `ADR-delivery-classification`: Gates, Overall refactor workflow and Handoff target lose `plan-intent` and its
  carry. Classification axes, workflow/stage IDs, `plan-accept`, `dev-integration` and target workflow remain.
- `ADR-roadmap-and-milestones-ledger`: Next work no longer selects confirm-the-intent from an absent gate record.
  It recommends starting the eligible requested draft's Planning; ordering and explicit task instruction remain.
- `ADR-ux-screens`: the inline Planning boundary is before implementation rather than before `plan-intent`.
  Comparing screen candidates during Planning and retaining the recommended candidate during Development remain.

## 5. Consequences

- New Units need no intent-record commit or special carry handling.
- Task authorization still depends on the agent following the explicit-instruction rule.
- Old configuration emits an actionable ignored-key warning until the owner removes it.
- Retaining stage IDs leaves small ungated stages, preserving compatibility with envelopes and return paths.

## 6. Confirmation

Development tests workflow definitions, direct acceptance, handoff, legacy records, size checks and policy output.
Review compares guidance and Living Spec restatements with this outcome. Generic gate engine behavior is unchanged.
