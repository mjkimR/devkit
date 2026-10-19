---
id: PADR-direct-acceptance-command-and-handoff-guard
title: Direct acceptance command and handoff guard
summary: "A devkit spec proposal accept command checks eligibility and the executor's own feedback sweep, then sets status accepted and records the user's gate:plan-accept in one step; handoff also requires that gate record, and the sdd-proposal schema stays."
proposal: PROP-draft-direct-acceptance
status: draft
created_at: 2026-10-19
---

# [PADR-direct-acceptance-command-and-handoff-guard] Direct acceptance command and handoff guard

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

A direct acceptance must reach the same end state a Planning acceptance reaches: `status: accepted` and an accepted
`gate:plan-accept` given by the user, which the handoff carries. The engine fixes the order
([engine evidence](../materials/engine-evidence.md)): `plan-intent` while the proposal is a draft, a passing
`collect-feedback` sweep, `status: accepted` on disk, then `plan-accept`; anything else is `REQUEST_UNKNOWN`. The
handoff checks the status but not the gate record, and the only check of a complete Planning outcome is the
`plan-<slug>` integration check, which a direct acceptance never reaches. A hand edit that sets the status and then
fails to record the gate would hand off silently without the user's acceptance.

## 2. Decision Drivers

- One validated step instead of an order an agent must get right by hand.
- Never infer an approval: the user's explicit acceptance is recorded with `--by user` exactly as
  `devkit workflow answer` does.
- Keep the `sdd-proposal` schema: `collect-feedback` is shared with Development and must stay required for normal
  Planning.

## 3. Considered Options

- **A command plus a handoff guard** (chosen).
- **A skill procedure over existing commands** (edit the status, `devkit workflow answer`): no code, but the order is
  easy to get wrong, eligibility is unchecked and a partial state hands off without the gate.
- **Make `collect-feedback` optional in `sdd-proposal`, or add a skip token for direct acceptance**: rejected; the
  first drops the sweep from normal Planning (an optional unmet stage is passed over), the second records a sweep
  that did not happen.
- **A mode of `devkit spec proposal check`**: rejected; `check` is a read-only Backlog guard and refuses any status
  other than `draft`, so it cannot also write the acceptance.

## 4. Decision Outcome

- **Command** (working name `devkit spec proposal accept <slug> --direct --reason "<why it is eligible>"`): checks the
  mechanical eligibility (`PADR-eligibility-for-direct-acceptance`) and the branch the chosen path requires; requires
  that `collect-feedback` holds through the executor's own sweep of the acceptance session (a new feedback envelope,
  zero observations being a valid PASS) and otherwise refuses with a stable code naming the sweep; then writes
  `status: accepted` and records `gate:plan-accept` (`by: user`, note "direct acceptance, Planning skipped: <reason>"),
  restoring the status when the record fails. It never records `plan-intent`, never commits and never runs the
  handoff; the agent runs it only after the user's explicit acceptance and commits the result.
- **Handoff guard**: `devkit spec proposal handoff` also requires the effective accepted `gate:plan-accept` record
  (the same rule it uses to carry it), refusing with `SPEC_PROPOSAL_NOT_APPROVED` otherwise, for every proposal.
- **Visibility**: the acceptance request shows "Planning: skipped (direct acceptance)" where a Planning acceptance
  shows the applied effort and support roles, together with the eligibility reason, the PADRs the handoff will
  promote and the `dev_effort` hint for Development.
- The `sdd-proposal` stage schema is unchanged; its body and `CAP-DLV-delivery-workflows` describe the direct path.

## 5. Consequences

- A partial direct acceptance cannot be handed off, and a Planning acceptance whose gate record is missing is caught
  too.
- Tests that hand off a proposal with only `status: accepted` must record the gate.
- The plain `accept` form for a proposal in review (one validated step for Planning acceptance as well) is a possible
  follow-up, outside this proposal.
