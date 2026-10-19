---
id: PADR-direct-acceptance-command-and-handoff-guard
title: Direct acceptance command and handoff guard
summary: "On a one-commit plan-<slug> branch merged like any Planning branch, a devkit spec proposal accept command checks eligibility, sets status accepted and records the user's gate:plan-accept through the engine; a bound proposal's handoff also requires that gate record."
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
fails to record the gate would hand off silently without the user's acceptance. Where the acceptance is committed is
compared in [options](../materials/options-comparison.md); this record assumes the recommended A3 and changes only in
its first bullet if the user chooses A2.

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

- **Where it runs**: a direct acceptance is a Planning acceptance without a Planning run. After the read-only
  `--check` passes on the base, the Host starts `plan-<slug>`, sweeps its own acceptance session there (a new
  `feedback` envelope at `collect-feedback`; zero observations is a valid PASS), runs the command and commits; that is
  the branch's only commit. The branch merges like any Planning branch: locally under `pull_request = auto`, where
  the existing `plan-<slug>` readiness check validates status, both gates and the sweep, and through its PR under
  `required`. The command refuses in any other checkout than the slug's own `plan-<slug>`.
- **Command** (working name `devkit spec proposal accept <slug> --direct --reason "<why it is eligible>"`), run only
  after the user's explicit acceptance:
  - checks the mechanical eligibility (`PADR-eligibility-for-direct-acceptance`); `--check` runs the same checks
    read-only on the base and writes nothing;
  - writes `status: accepted` (from `draft`, without `reviewing`) and records `gate:plan-accept` through devkit's
    `record_answer` (`by: user`, note "direct acceptance, Planning skipped: <reason>; task_kind <kind> confirmed"), so
    the engine decides whether `collect-feedback` holds, is switched off or is skipped by policy; a `REQUEST_UNKNOWN`
    refusal is reported under a stable code naming the missing sweep, and the status is restored;
  - never records `plan-intent`, never commits, merges or runs the handoff.
  Freshness of the sweep stays an executor procedure, as for every Planning run.
- **Refusal or objection**: when the command refuses after the branch started, or a reviewer of the `required` PR
  objects, the user decides; on that decision the Host closes the PR and drops the branch with
  `devkit worktree finish plan-<slug> --discard`. The base draft is untouched and may run Planning.
- **Handoff guard**: for a bundle bound to `sdd-proposal`, `devkit spec proposal handoff` also requires the effective
  accepted `gate:plan-accept` record (the rule it already uses to carry it), refusing with a code of its own (working
  name `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED`) whose fix returns to the base: discard `dev-<slug>` and accept through
  Planning or a direct acceptance. A single-file or unbound proposal, which can carry no gate record, keeps the
  status-only rule.
- **The note survives the handoff**: carried gate records keep the proposal's note after `PROP-<slug>`
  (`PROP-<slug>: <note>`) instead of replacing it, so a spec shows that its direction was accepted without Planning.
- **Visibility**: the acceptance request shows "Planning: skipped (direct acceptance)" where a Planning acceptance
  shows the applied effort and support roles, together with `task_kind` (which `plan-accept` confirms) and its
  reason, the recorded `planning_effort` hint, the eligibility reason, the PADRs the handoff will promote and the
  `dev_effort` hint, which the Host reviews against the settled direction as a Planning executor would.
- The `sdd-proposal` stage schema is unchanged; its body and `CAP-DLV-delivery-workflows` describe the direct path.

## 5. Consequences

- A partial direct acceptance cannot be handed off, and a bound Planning acceptance whose gate record is missing is
  caught too.
- Tests that hand off a bound proposal with only `status: accepted` must record the gate; tests of the carried note
  change.
- The plain `accept` form for a proposal in review (one validated step for Planning acceptance as well) is a possible
  follow-up, outside this proposal.
