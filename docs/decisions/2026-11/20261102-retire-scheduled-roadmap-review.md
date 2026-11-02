---
id: ADR-retire-scheduled-roadmap-review
title: Retire the scheduled roadmap review
summary: "For the roadmap review that ADR-roadmap-and-milestones schedules, we retire the scheduled review and its spec-next reminder, to keep ADRs in step with the shipped guidance, accepting that milestone machinery is reassessed only when feedback shows friction."
status: accepted
created_at: 2026-11-02
supersedes: [ADR-roadmap-and-milestones]
---

# [ADR-retire-scheduled-roadmap-review] Retire the scheduled roadmap review

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: user, agent
- **Involved Components/Capabilities**: `ADR-roadmap-and-milestones`, `CAP-HARN-agent-guidance`

---

## 1. Context & Problem Statement

`ADR-roadmap-and-milestones` (Review) schedules a roadmap review. The review runs when three milestones are `done` or
on 2027-01-31, whichever comes first. It is recorded as a roadmap-review ADR, and `spec-next`'s idle step reports it as
due until that ADR exists.

Commit `e9f589c4` (2026-10-22) removed that idle step from the `spec-next` guidance, and a later commit removed its test
assertion. No shipped guidance or code reports the review any more. Five milestones are `done` in
`docs/roadmap/_archive/`, so the count trigger has already passed with no record. The accepted ADR still states a
review that nothing carries out.

---

## 2. Decision Drivers

- Accepted ADRs agree with the shipped guidance.
- Milestones are loosely managed themes, not delivery commitments.
- A date-based reminder adds guidance that every idle `spec-next` run has to carry.

---

## 3. Considered Options

### Option 1: Retire the scheduled review (Selected)
- **Overview**: Replace the Review clause of `ADR-roadmap-and-milestones`. Milestone machinery is reassessed only
  when feedback reports friction with it.
- **Pros**: The ADR matches the shipped guidance; no reminder text returns.
- **Cons**: No fixed point forces a look at unused milestone machinery.

### Option 2: Restore the `spec-next` reminder
- **Overview**: Bring the idle step and its test back, then hold the review it reports.
- **Pros**: Keeps the original evaluation plan.
- **Cons**: It reverses a deliberate guidance cut, and the count trigger has already fired.

---

## 4. Decision Outcome

We adopt **Option 1**. This ADR replaces only the Review clause of `ADR-roadmap-and-milestones`. Its other decisions
stay in force, and that ADR stays `accepted`.

- The scheduled roadmap review (three `done` milestones or 2027-01-31) is retired, and `spec-next` reports no review
  as due.
- The milestone machinery is reassessed through ordinary feedback when its use shows friction. A proposal to remove
  part of it follows the usual proposal path.
- Nothing is restated in a capability or architecture document, because this decision removes an obligation and adds
  none.

---

## 5. Consequences

- **Positive**: The accepted ADRs no longer describe a review that no guidance runs.
- **Negative / Risks**: Unused milestone machinery stays until someone files feedback about it.
- **Follow-ups**: None.

---

## 6. Confirmation

Review only. `rg "2027-01-31|roadmap.review" packages/ .devkit/managed/` finds no guidance that reports the review.
