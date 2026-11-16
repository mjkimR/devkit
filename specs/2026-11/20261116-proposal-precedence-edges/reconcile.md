---
reconcile_id: REC-proposal-precedence-edges
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Proposal precedence edges reconciliation

## Contracts changed

- `CAP-HARN-agent-guidance`, section "Repository Backlog and next work": a new paragraph owns the two checks. A
  draft claiming its handoff precedes another proposal's, or whose cost depends on another proposal's or spec's
  state, is checked before it is committed and again on its first Planning turn as part of the head-pinned recheck, which
  now runs on the first turn as well as after each Host refresh (reconcile-check-01 finding 1):
  each named unit's base `status` and any local or already fetched `dev-<slug>` branch, fetching only within existing
  network authorization. A handoff (a `dev-<slug>` branch or a `SPEC-<slug>`) makes the premise stale and it is
  rewritten; an ordering against a still-accepted proposal with no branch is the user's sequencing decision stated
  in the draft, and a first Planning turn that finds none asks it in its question round. No ordering field, edge onto an accepted proposal or CLI notice is added (AC-04). Sources:
  `references/backlog.md.jinja` (Requests and decomposition) and `references/planning.md` (Steps) of the spec
  bundle's `spec` skill, asserted by `test_ordering_claim_guidance.py` (AC-01 to AC-03).

Agent-facing bundle text (not Living Spec, changed under Task 2): the two references above; `devkit sync` updated the
tracked `.devkit/installation.json` and the ignored projected and managed copies.

## Unaffected layers

- Use cases: `UC-plan-and-hand-off-a-proposal` covers drafting in Backlog (step 1) and starting Planning (step 2)
  at the level of commands and gates; it states the Backlog editability check only by its refusal (Scenario 8)
  and not the head-pinned recheck, and the new check adds no command, code, gate or actor-visible outcome, so no step or
  extension changes. `devkit docs search "precedes"` and `"head-pinned"` list no other use case on these flows.
- `CAP-DLV-proposal-planning`: its lifecycle rules (rule 13, accepted proposals unedited; `devkit spec proposal check`
  as the Backlog editability guard) are kept unchanged and are not restated by the new step.
- Architecture: no package, feature, layer or feature edge changes; `git diff --stat` of the range lists nothing
  under `packages/devkit-spec/src/devkit_spec/features/` or `packages/devkit-docs/` (AC-05).
- Design: no `DESIGN-` document owns Backlog or Planning guidance text; no component or interface changes.
- Domain: `DOMAIN-delivery-relationships` is unaffected; prerequisite, membership and provenance semantics are
  unchanged and no edge is added.
- Operations: no `OPS-` document or runbook reads proposal ordering.
- Decisions: the successor-declared edge of `ADR-roadmap-and-milestones-ledger` and the immutability of an accepted
  proposal in `ADR-proposal-acceptance` are kept; the steps restate no lasting policy beyond them, so no ADR.

## Entrypoints

`devkit spec entrypoints derive --spec specs/2026-11/20261116-proposal-precedence-edges` proposed only
`test_ordering_claim_guidance.py` for `CAP-HARN-agent-guidance`; rejected, because a test is not a capability
doorway and the declared bundle sources are already in the capability's reach. No `entrypoints` changed.

## Source feedback

- `FB-draft-precedence-claim-unenforced`: resolved by `SPEC-proposal-precedence-edges` through the feedback's
  second suggestion (a stale ordering premise surfaces before the first Planning decision), extended to the moment
  the claim is written; its first suggestion (an edge checked at handoff) is declined by the accepted design. Verified
  by `test_ordering_claim_guidance.py` (rendered guidance, local and cloud, and the branch check against a Git
  fixture whose base lists a handed-off proposal as `accepted`) and the code review of this range (review-01,
  reverify-01).
