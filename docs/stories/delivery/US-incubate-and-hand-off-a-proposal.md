---
id: US-incubate-and-hand-off-a-proposal
title: Incubate a Proposal and Hand It Off to a Spec
summary: An AI coding agent shapes an idea whose direction must be decided first in a proposal bundle, or accepts a settled draft directly, records the user's acceptance in one step, and hands it off to a bound spec bundle with decisions promoted, materials moved, approvals carried and references rewritten.
area: delivery
actor: AI coding agent
status: active
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundle/workflows/sdd-proposal.md
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/accept.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/feedback.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
created_at: 2026-10-13
capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-spec-bundles
  - CAP-DLV-delivery-workflows
---

# [US-incubate-and-hand-off-a-proposal] Incubate a Proposal and Hand It Off to a Spec

## 1. User Story Narrative

- **As a**: AI coding agent handling a request whose direction is not yet clear
- **I want to**: shape the idea in a proposal, gather evidence and preliminary decisions, and turn the approved
  proposal into a spec bundle without losing anything that pointed at it
- **So that**: the user decides the direction on evidence, and the delivery that follows starts from a consistent
  Living Spec instead of dangling links to a deleted proposal

---

## 2. Background & Context

`proposal`-depth work starts in Backlog with `devkit spec proposal new <slug>`, which binds `proposal.md` to
`sdd-proposal`; the user's confirmation of the draft is `plan-intent`, which includes the Planning `activity-effort`
the agent proposes. Planning runs on `plan-<slug>`: the `spike` stage gathers evidence through the `scout` role and
criticism through the `challenger` role, which the effort requires from `medium` up, `devkit spec proposal padr`
records preliminary decisions and the questions for the user are collected in one round. The user's `plan-accept` is
recorded with `devkit spec proposal accept <slug> --by user`, which writes `status: accepted` and the gate record in
one step; a draft whose direction is settled may instead be accepted directly in Backlog on the base checkout
(`--direct`), without a Planning branch or run. After `plan-accept`, `devkit workflow next` reports the proposal unit
complete, and Development starts with `devkit spec proposal handoff <slug>`, which creates the spec bundle bound to
`sdd-spec-<task_kind>`.

---

## 3. Acceptance Criteria (Given / When / Then)

### Scenario 1: An accepted proposal is handed off
- **Given**: a proposal bundle with `status: accepted` and its recorded `gate:plan-accept`, one PADR and a non-empty
  `materials/`
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` exists with `spec.md` bound to `sdd-spec-feature`, the PADR is an
  accepted ADR under `docs/decisions/<YYYY-MM>/`, the materials are under `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`,
  the proposal directory is gone, and the output lists `[PROMOTED_ADR: ...]`, `[MATERIALS: ...]` and
  `[NEXT_CMD: devkit workflow next --unit <dir>]`

### Scenario 2: Approval is never inferred
- **Given**: a proposal with `status: draft` or `reviewing`: `plan-accept` was not given
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_NOT_APPROVED`, whose `[FIX]` names `devkit spec proposal
  accept`, and writes nothing; a proposal bound to `sdd-proposal` that says `accepted` without its recorded `gate:plan-accept` exits `2`
  with `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` and writes nothing

### Scenario 3: References into the proposal follow it
- **Given**: a story that cites the proposal by ID and links its `proposal.md`
- **When**: the handoff completes
- **Then**: the ID now names the spec and the link points at `spec.md`, each reported as a `[REWRITTEN: ...]` line,
  and a `SPEC_PROPOSAL_REFS_REWRITTEN` notice asks the agent to reread the rewritten sentences

### Scenario 4: A defect proposal hands off to the bugfix workflow
- **Given**: a proposal created with `--task-kind bugfix` and accepted
- **When**: the agent hands it off
- **Then**: the spec bundle holds only `spec.md`, bound to `sdd-spec-bugfix`, and the proposal's target
  area and boundaries appear in its `### Target Area & Boundaries` notes

### Scenario 5: The proposal's approvals carry by name
- **Given**: an accepted proposal whose unit recorded `gate:plan-intent` and `gate:plan-accept` by the user
- **When**: the agent hands it off
- **Then**: the spec holds the same two requests as decision records with note `PROP-<slug>`, followed by the
  proposal record's note when it has one (`PROP-<slug>: direct acceptance, Planning skipped: ...`), each reported as
  `[CARRIED_GATE: ...]`; `plan-intent` is not asked again and `plan-accept` satisfies no spec stage


### Scenario 6: Planning observations follow the outcome
- **Given** a proposal with open and settled feedback, captured inside its own write boundary
- **When** Planning returns to the user and the proposal is later handed off
- **Then** each enabled run sweep has fresh recorded coverage, open feedback enters the spec with unchanged IDs,
  statuses and observation dates, settled feedback is preserved as material, and Development supplies its own sweep

### Scenario 7: Deletion without handoff preserves open work
- **Given** rejected or decomposed proposal feedback, or a queued draft the user decided to do as a `session` task at
  pickup
- **When** the Host deletes the original proposal
- **Then** open feedback is preserved once in the month-level backlog with retrievable historical context and valid
  current references; invalid input, collisions or unresolved live dependencies prevent deletion

### Scenario 8: A settled draft is accepted directly
- **Given**: a draft with its `plan-intent` recorded, no `needs_decompose`, `supersedes` or Planning branch, no
  envelope hold, a swept acceptance session, in the base checkout on its base branch
- **When**: after the user's explicit acceptance the agent runs `devkit spec proposal accept <slug> --by user --direct
  --note "<reason>"`
- **Then**: `proposal.md` says `status: accepted`, `gate:plan-accept` is recorded with the note `direct acceptance,
  Planning skipped: <reason>; task_kind <kind> confirmed`, and the output is one `[ACCEPTED: ... form=direct ...]`
  line; a draft failing a condition exits `2` with `SPEC_PROPOSAL_NOT_ELIGIBLE` listing each one, and writes nothing
