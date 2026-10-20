---
id: SPEC-draft-direct-acceptance
title: Direct acceptance of drafts that need no Planning
summary: Lets the user accept a settled draft in Backlog on the base, without a Planning branch or run, through the planned accept command recording plan-accept with a Planning-skipped note; a session-depth draft may instead be deleted at pickup and done as a session on the user's decision.
status: in-progress
created: 2026-10-20
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-delivery-workflows
  - CAP-HARN-agent-guidance
  - CAP-HARN-command-mount
related_stories:
  - US-incubate-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-draft-direct-acceptance] Direct acceptance of drafts that need no Planning

## 1. Problem Statement & Motivation

Handed off from proposal PROP-draft-direct-acceptance on 2026-10-20.
- **Preserved Materials**: `docs/materials/2026-10/20261020-draft-direct-acceptance`
- **Planning material**: [options](../../../docs/materials/2026-10/20261020-draft-direct-acceptance/options-comparison.md),
  [engine evidence](../../../docs/materials/2026-10/20261020-draft-direct-acceptance/engine-evidence.md).
- **Decisions** (promoted at handoff, the contract this spec implements):
  `ADR-direct-acceptance-command-and-handoff-guard`, `ADR-eligibility-for-direct-acceptance`,
  `ADR-session-reclassification-of-a-queued-draft`. They extend `ADR-roadmap-in-repository` (its interim "small
  drafts run Planning at `low`" rule ends) and qualify `ADR-run-records-and-activity-branches` (a direct acceptance is
  Backlog work, with no Planning activity); both stay unedited.

### 1.1 Problem

- **Small drafts pay for a Planning they do not need.** Every request not started now is a draft proposal
  (`SPEC-backlog-roadmap-and-issues`). Many carry a settled direction, yet Planning at `low` still starts
  `plan-<slug>`, commits `status: reviewing`, records `plan-accept` and merges the branch: two branches, and two PRs
  under `pull_request = required`, for one decision the user could make on sight.
- **Queued session work pays for a Unit.** A `session`-depth request that waits in the queue becomes a draft, and
  every path to accepting it ends in a spec Unit; the lowering rule forbids doing it as the session it would have
  been if started at once.
- **Nothing may accept a draft today, and nothing checks a hand-set acceptance.** Backlog changes only a `draft`, the
  `sdd-proposal` body records `plan-accept` only on `plan-<slug>`, every executor edits the `status:` line by hand,
  and the handoff checks the status but not the gate record, so a hand-set `status: accepted` hands off without the
  user's acceptance ([engine evidence](../../../docs/materials/2026-10/20261020-draft-direct-acceptance/engine-evidence.md)).

### 1.2 Outcome

`devkit spec proposal accept` becomes the one writer of every acceptance: the Planning form in one validated step,
`--direct` for an eligible draft on the base checkout (Backlog work, no Planning run), a read-only `--check`, and a
`--direct` repair of an accepted proposal that has no gate record and no Planning run. The handoff of a bound
proposal requires the recorded acceptance and carries its note. The guidance describes the direct path and the
session reclassification of a queued draft, the one stated exception to lowering depth only through a handoff.

### 1.3 Assumptions

- **Strategy-layer ordering**: the proposal makes the workbench strategy-layer update (its §3.2, workbench
  `docs/strategy-layer/01-master-flow.md` and `03-policy.md`) come first. At this Development's base the workbench
  text still names this work as a follow-up. The promoted ADRs are the contract here; the difference is reported to
  the Host so the workbench update lands before or with `dev-integration`, and nothing in this repository depends on
  the workbench text.
- **Actor**: `--by` takes `user` only. `plan-accept` is always the user's (policy `ask` only) and records name the
  authority (`user` or `policy`); autohub records the user's UI acceptance the same way (`--by user`).
- **Note of a direct acceptance**: `--note` carries the eligibility reason and is required with `--direct`; the
  command writes the recorded note as `direct acceptance, Planning skipped: <reason>; task_kind <kind> confirmed`, the
  repair included. The Planning form records `--note` as given (empty allowed).
- **Missing `task_kind`** counts as `feature`, as the handoff reads it.
- **Outside Git** the checkout conditions (the base checkout, `plan-<slug>`) are not checked, as for every
  activity-branch check of devkit-spec; there is no Planning branch to find either.
- **Unbound or single-file proposals** carry no gate records: the command refuses them, and their acceptance stays
  the status line alone, which the handoff keeps accepting (`ADR-direct-acceptance-command-and-handoff-guard`).
- **Codes**: the working name `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` is kept; the command adds
  `SPEC_PROPOSAL_ACCEPT_REFUSED` (a form or status the command does not accept), `SPEC_PROPOSAL_NOT_ELIGIBLE`
  (failed direct-acceptance conditions, all listed) and `SPEC_PROPOSAL_GATE_NOT_OPEN` (the engine did not open
  `gate:plan-accept`); the Planning form on another branch reuses `SPEC_PROPOSAL_WRONG_WORKTREE`.
- **Refusal exit**: a refusal, `--check` included, is an advisory error (exit `2`), like `devkit spec proposal check`.

## 2. User Stories

- **US-1**: As the user, I want to accept a draft whose direction is settled on sight in Backlog, so that it skips the
  Planning branch, its PR and its run while my acceptance stays explicit and recorded (`US-incubate-and-hand-off-a-proposal`).
- **US-2**: As an agent recording an acceptance, I want one validated command instead of a hand-edited status and a
  separate answer, so that a partial acceptance can neither be written nor handed off.
- **US-3**: As the user picking a queued `session`-depth draft, I want to do it as the session it is, on my explicit
  decision, without a spec Unit.

## 3. Non-Goals

1. **Scope Excluded**: a `skip` value for `activity-effort`; skipping Planning is routing, not thoroughness.
2. **Scope Excluded**: accepting without the user. Policy delegation never applies to `plan-intent` or `plan-accept`.
3. **Scope Excluded**: a command or tool check for the session reclassification; it stays a Backlog deletion on the
   user's decision, through the existing `devkit spec proposal check`.
4. **Scope Excluded**: recording `plan-intent`, committing, merging or running the handoff from `accept`.
5. **Scope Excluded**: a repair of a Planning acceptance whose gate record is missing (a `worker` envelope exists);
   its recovery is reverting the Planning merge, on the user's decision.
6. **Scope Excluded**: the `reject` command, an autohub UI, a mode of `devkit spec proposal check`, any change of the
   `sdd-proposal` stages, checks or gates, and the workbench strategy-layer documents.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Direct acceptance of an eligible draft
- **Given** a draft bundle bound to `sdd-proposal` with an accepted `gate:plan-intent`, a passing `collect-feedback`
  sweep, no `needs_decompose`, no `supersedes`, no `plan-<slug>`, a valid `task_kind`, no envelope hold, in the main
  worktree on its base branch
- **When** `devkit spec proposal accept <slug> --by user --direct --note "<reason>"` runs
- **Then** it exits `0`, `proposal.md` says `status: accepted`, a decision record `gate:plan-accept` with `action:
  accept`, `by: user` and note `direct acceptance, Planning skipped: <reason>; task_kind <kind> confirmed` exists, and
  stdout is one line `[ACCEPTED: PROP-<slug> form=direct path=<proposal.md> status=accepted decision=<record path>]`

### [AC-02] Every failed eligibility condition is listed and nothing is written
- **Given** a draft that fails one or more of: an accepted `gate:plan-intent`, `needs_decompose: true`, `supersedes`,
  a local or fetched `plan-<slug>`, `task_kind` outside `feature|bugfix`, an envelope hold (problem, pending question,
  malformed `worker` envelope)
- **When** `accept --direct` runs
- **Then** it exits `2` with `SPEC_PROPOSAL_NOT_ELIGIBLE` (`INTERACTION`), one `[DETAIL]` line per failed condition,
  and `proposal.md` and the unit's `decisions/` are unchanged

### [AC-03] Direct acceptance runs only on the base checkout
- **Given** an otherwise eligible draft in a linked worktree, on a detached `HEAD`, on a `plan-*` or `dev-*` branch, or
  on a branch other than the `origin/HEAD` target when that resolves
- **When** `accept --direct` runs
- **Then** it exits `2` with `SPEC_PROPOSAL_NOT_ELIGIBLE` naming the checkout condition, and nothing is written; in
  the main worktree with no `origin/HEAD`, on a branch that is neither `plan-*` nor `dev-*`, the condition holds

### [AC-04] Read-only check with a pending intent
- **Given** a draft eligible except that `gate:plan-intent` is not recorded
- **When** `accept --direct --check --by user` runs
- **Then** it exits `0` with `[ACCEPT_CHECK: PROP-<slug> form=direct path=<proposal.md> eligible=yes
  pending=gate:plan-intent]` and writes nothing; with a blocking condition as well it exits `2` with
  `SPEC_PROPOSAL_NOT_ELIGIBLE`, whose details list the blocking condition and the pending intent separately, and
  writes nothing

### [AC-05] The engine decides the sweep; a refusal restores the status
- **Given** an eligible draft without a passing `collect-feedback` sweep
- **When** `accept --direct` runs
- **Then** it exits `2` with `SPEC_PROPOSAL_GATE_NOT_OPEN`, whose details name the unmet check
  `envelope-check-pass(feedback swept)`, `proposal.md` is byte-for-byte as before and no `gate:plan-accept` record
  exists; with `[workflow.stages] collect-feedback = "off"` the same draft is accepted

### [AC-06] The Planning form
- **Given** a proposal `status: reviewing` whose sweep passed, in a checkout on `plan-<slug>`
- **When** `accept <slug> --by user --note "<text>"` runs
- **Then** it exits `0`, writes `status: accepted` and records `gate:plan-accept` with the note as given
  (`form=planning`); the same command on another branch is `SPEC_PROPOSAL_WRONG_WORKTREE`, a draft without `--direct`,
  a proposal in review with `--direct`, a `rejected` proposal, a single-file or unbound proposal are
  `SPEC_PROPOSAL_ACCEPT_REFUSED`, each with nothing written

### [AC-07] Repair of a direct acceptance without its record
- **Given** a bound proposal `status: accepted` with no effective `gate:plan-accept` and no `worker` envelope, on the
  base checkout
- **When** `accept --direct --note "<reason>"` runs
- **Then** it records `gate:plan-accept` (`form=repair`) and leaves `proposal.md` unchanged; with a `worker` envelope
  it is `SPEC_PROPOSAL_NOT_ELIGIBLE` naming it, and with an effective `gate:plan-accept` `SPEC_PROPOSAL_ACCEPT_REFUSED`

### [AC-08] Arguments
- **Given** any proposal
- **When** `accept` runs with `--by` other than `user`, or `--direct` without a non-blank `--note`
- **Then** it exits `2` before reading or writing the proposal (a usage error for `--by`, `ARGUMENT_INVALID` targeting
  `--note`)

### [AC-09] The handoff guard
- **Given** a bundle bound to a workflow with `status: accepted` but no effective accepted `gate:plan-accept` (the
  rule that carries it), on `dev-<slug>`
- **When** `devkit spec proposal handoff <slug>` runs
- **Then** it exits `2` with `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` (`INTERACTION`) and nothing is written or removed;
  an unbound or single-file proposal with `status: accepted` still hands off on the status alone

### [AC-10] The carried note survives
- **Given** a proposal whose effective `gate:plan-accept` note is `direct acceptance, Planning skipped: X; task_kind
  feature confirmed`
- **When** it is handed off
- **Then** the spec's carried record has note `PROP-<slug>: direct acceptance, Planning skipped: X; task_kind feature
  confirmed`; a gate with an empty note carries `PROP-<slug>`

### [AC-11] The not-approved directive names the command
- **Given** a proposal whose status is not `accepted`
- **When** the handoff refuses it with `SPEC_PROPOSAL_NOT_APPROVED`
- **Then** its `[FIX]` names `devkit spec proposal accept` (a direct acceptance on the base, or the Planning
  acceptance on `plan-<slug>`) and no longer tells the agent to set `status: accepted` by hand

### [AC-12] Guidance states the direct path and the session reclassification
- **Given** the bundled guidance (`sdd-proposal` body, the `spec` skill and its Backlog, classification, effort,
  feedback-retirement and worktree references, `spec-next`, `spec-orchestrate`, the bundle `AGENTS.md`) and the
  proposal scaffold
- **When** the package tests read them
- **Then** acceptances are recorded with `devkit spec proposal accept`, Backlog may accept an eligible draft directly
  on the base after `--check`, the user's acceptance and the Host's sweep, a direct acceptance has no run, effort or
  `worker` envelope, the lowering rule names the session reclassification as its one exception besides a handoff,
  the Backlog reference no longer says small drafts run Planning until direct acceptance exists, and the scaffold's
  lifecycle line holds for a direct acceptance
