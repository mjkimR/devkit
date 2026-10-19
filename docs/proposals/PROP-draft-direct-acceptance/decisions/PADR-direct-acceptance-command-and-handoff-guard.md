---
id: PADR-direct-acceptance-command-and-handoff-guard
title: Direct acceptance command and handoff guard
summary: "The planned devkit spec proposal accept command (01 10) records the user's acceptance in one validated step, also for an eligible draft (--direct), through the engine; a bound proposal's handoff also requires the gate record and keeps its note."
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
handoff checks the status but not the gate record, and the `plan-<slug>` readiness check runs only on the MCP
integration path. Today every executor edits the `status:` line by hand; 01 §10 already plans one writer for it,
`devkit spec proposal accept <slug> --by <actor> [--note]`, shared by the local Host and autohub. Where a direct
acceptance is committed is compared in [options](../materials/options-comparison.md); the user chose A2, Backlog
acceptance on the base under every policy, and allowed one request to ask both gates (`answer-01.yaml`).

## 2. Decision Drivers

- One validated step instead of an order an agent must get right by hand, and one writer for every acceptance.
- Never infer an approval: the user's explicit acceptance is recorded through devkit's `record_answer`, exactly as
  `devkit workflow answer` does.
- Keep the `sdd-proposal` schema: `collect-feedback` is shared with Development and must stay required for Planning.

## 3. Considered Options

- **The planned `accept` command with a direct variant, plus a handoff guard** (chosen).
- **A direct-only command** (`accept --direct` with a fixed `by`): rejected; it ships a second shape beside the
  planned shared writer, which the later general command would have to break.
- **A skill procedure over existing commands** (edit the status, `devkit workflow answer`): no code, but the order is
  easy to get wrong, eligibility is unchecked and a partial state hands off without the gate.
- **Make `collect-feedback` optional in `sdd-proposal`, or add a skip token for direct acceptance**: rejected; the
  first drops the sweep from normal Planning, the second records a sweep that did not happen.
- **A mode of `devkit spec proposal check`**: rejected; `check` is a read-only Backlog guard that refuses any status
  other than `draft`.

## 4. Decision Outcome

- **Command** `devkit spec proposal accept <slug> --by <actor> [--note <text>] [--direct] [--check]`, run only after
  the user's explicit acceptance (`--by user`; autohub records the user's UI acceptance the same way):
  - without `--direct` it accepts a proposal in review (`status: reviewing`) on its `plan-<slug>`: the existing
    Planning acceptance in one step;
  - with `--direct` it accepts a draft: it checks the eligibility (`PADR-eligibility-for-direct-acceptance`),
    including the path's conditions, and refuses a draft without `--direct`;
  - it writes `status: accepted` and records `gate:plan-accept` through `record_answer`, with the note (for a direct
    acceptance "direct acceptance, Planning skipped: <reason>; task_kind <kind> confirmed"), so the engine decides
    whether `collect-feedback` holds, is switched off or is skipped by policy; on refusal it restores the status and
    reports the evaluation's unmet checks and hold reasons, never a guessed cause;
  - with `--direct` it also repairs a proposal already `accepted` that has no effective `gate:plan-accept` and no
    `worker` envelope (no Planning ran), applying every direct-acceptance check except the status; with a `worker`
    envelope the plain form repairs it as a Planning acceptance. A repair, like every acceptance, follows the user's
    explicit acceptance of a full request;
  - `--check` runs every check read-only and writes nothing; the command never records `plan-intent`, never commits,
    merges or runs the handoff.
  `reject` stays the follow-up 01 §10 plans.
- **Where it runs (A2, the user's choice)**: a direct acceptance is Backlog work under every policy, like Backlog's
  other changes (01 §5.1, 03 §1), committed on the base checkout only (another slug's activity branch is refused).
  Before proposing it the Host settles that it can push to the base (or that there is no remote); a protected base means
  Planning instead, and a stranded acceptance commit is undone with `git revert`, never a reset. The Host runs
  `--check`, sweeps its own acceptance session (a new `feedback` envelope at `collect-feedback`; zero observations is a
  valid PASS), runs the command and commits the result on the base. Under `pull_request = required` the request states
  that the direction gets no PR review, and the user may choose Planning for that draft instead.
- **Both gates in one request**: for an eligible draft without a recorded `plan-intent`, one request may ask both
  decisions, each named in full (the intent with goal, scope, verification, `task_kind`, depth and the effort hints;
  the acceptance with "Planning: skipped" and the eligibility reason), and the user answers each explicitly; neither
  is inferred from the other. The Host then records `plan-intent` with `devkit workflow answer --by user`, sweeps,
  runs `accept --direct` and commits all of it in one Backlog commit. If the user accepts only the intent, or the
  command refuses, the commit holds the draft with its intent record, which Planning starts from.
- **No run**: a direct acceptance has no Planning run, no `activity-effort` and no `worker` envelope; its sweep covers
  the acceptance session, and freshness stays an executor procedure as for every Planning run.
- **Handoff guard**: for a bundle bound to `sdd-proposal`, `devkit spec proposal handoff` also requires the effective
  accepted `gate:plan-accept` record (the rule it already uses to carry it), refusing with a code of its own (working
  name `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED`, `INTERACTION`): its directive is to stop and ask the user, never to
  record an acceptance unasked. On the user's explicit acceptance the Host repairs it where the proposal lives with
  `accept` (on the base for a direct acceptance), merges the base into `dev-<slug>` and reruns the handoff; a worker
  or Cloud Agent reports it as a problem instead. A single-file or unbound proposal, which can carry no gate record,
  keeps the status-only rule.
- **The note survives the handoff**: carried gate records keep the proposal's note after `PROP-<slug>`
  (`PROP-<slug>: <note>`) instead of replacing it, so a spec shows that its direction was accepted without Planning.
- **Visibility**: the acceptance request shows "Planning: skipped (direct acceptance)" where a Planning acceptance
  shows the applied effort and support roles, together with `task_kind` (which `plan-accept` confirms) and its
  reason, the recorded `planning_effort` hint, the eligibility reason, the PADRs the handoff will promote and the
  `dev_effort` hint, which the Host reviews against the settled direction as a Planning executor would.
- The `sdd-proposal` stage schema is unchanged; its body and `CAP-DLV-delivery-workflows` describe the direct path.

## 5. Consequences

- A partial direct acceptance cannot be handed off, and a bound Planning acceptance whose gate record is missing is
  caught too and can be repaired.
- Every party that records an acceptance (the Host locally, autohub) stops editing the `status:` line by hand; the
  `sdd-proposal` gate rules and the `spec` skill name the command.
- Tests that hand off a bound proposal with only `status: accepted` must record the gate; tests of the carried note
  change.
- It extends `ADR-roadmap-in-repository`, whose interim rule ("until a direct-acceptance path exists, a small draft
  runs Planning at `low`") it ends; that ADR stays unedited (`docs/decisions/` is outside this proposal), and the ADR
  promoted from this record names it.
