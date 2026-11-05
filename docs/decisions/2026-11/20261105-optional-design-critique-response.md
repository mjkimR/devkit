---
id: ADR-optional-design-critique-response
title: Make optional design critique responses explicit
summary: "For consequential design objections, we reuse the optional critique pass for one author response and coordinator disposition, to clarify the choice, accepting a small coordination cost."
proposal: SPEC-design-explore-counterarguments
status: accepted
created_at: 2026-11-05
---

# [ADR-optional-design-critique-response] Make optional design critique responses explicit

## 1. Context & Problem Statement

`CAP-DLV-design-exploration` already permits an optional critic and normally one refinement pass. Its role packet
names no author response or per-objection coordinator disposition. A coordinator can therefore adopt a mistaken
objection without the author explaining a surviving mechanism, or imply that an absent reply concedes the point.
`ADR-explicit-solution-exploration` owns explicit invocation, local roles and output authority; those decisions hold.

## 2. Decision Drivers

- Expose evidence and revisions that change the actual design choice.
- Keep small questions and zero-findings criticism free of extra coordination.
- Preserve independent first passes, honest fallback and useful unconventional mechanisms.
- Add no role registry, runtime, consensus or mandatory retained artifact.

## 3. Considered Options

- Keep the existing general critique/refinement wording: smallest text surface, but leaves the response and
  missing-return treatment unspecified.
- Clarify an optional author response inside that pass: fills the concrete gap with existing roles and one
  bounded exchange, while adding a short packet and disposition to coordination.
- Add permanent red/blue teams and iterative debate: separates advocates visibly, but introduces a cast and
  repeated rounds without a demonstrated responsibility the explorer and critic cannot cover.

## 4. Decision Outcome

Choose the optional author response within the existing pass because it clarifies evidence without a new cast.

- A supported objection that can change feasibility, tradeoffs or recommendation can receive one author response
  before coordinator disposition, within the normal critique/refinement pass.
  → `CAP-DLV-design-exploration` bounded uncertainty rule (SHOULD).
- The response accepts/revises, rebuts with evidence or labeled inference, or identifies a bounded unknown; the
  coordinator judges the actual response and retains material uncertainty.
  → `CAP-DLV-design-exploration` bounded uncertainty rule (SHOULD).
- Missing responses remain missing coverage; inline analysis is labeled without inventing an author's return.
  → `CAP-DLV-design-exploration` honest fallback rule (MUST).
- Further passes name a decision-changing question and a finite bound before work starts; otherwise synthesis
  returns the unresolved disagreement without consensus or implementation.
  → `CAP-DLV-design-exploration` bounded uncertainty rule (SHOULD).

This decision refines the capability without superseding `ADR-explicit-solution-exploration` or changing its
invocation, local role and output authority clauses.

## 5. Consequences

A consequential objection has an inspectable response and coordinator judgment. Routine work uses no extra role.
The response packet costs coordination when selected; a bound can leave a useful disagreement unresolved. Neither
fresh contexts nor role instructions provide native isolation. Reconsider another role only if a concrete task
requires a responsibility these existing roles cannot perform.

## 6. Confirmation

Review the five proposal ACs against the entry, orchestration reference and role text. Catalog integration and
built-wheel consumer tests check deployed response, fallback and stopping instructions. No automated check proves
model obedience, design quality or team superiority. The capability and `UC-explore-a-design-problem` restate the
observable rules and scenarios during Development reconciliation.
