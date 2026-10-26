---
id: UC-incubate-and-hand-off-a-proposal
title: Incubate a Proposal and Hand It Off to a Spec
summary: "An AI coding agent develops a proposal, reviews its committed Planning source before acceptance under project policy, obtains Host approval against those findings, then accepts or hands it off while preserving materials, approvals and references."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - User (confirms plan-intent, answers Planning questions, gives plan-accept)
  - scout
  - challenger
  - planning-worker (local-orchestrated mode only)
status: active
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/SKILL.md.jinja
  - packages/devkit-spec/src/devkit_spec/features/policy/cli/commands.py
created_at: 2026-10-13
capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-spec-bundles
  - CAP-DLV-delivery-workflows
---

# [UC-incubate-and-hand-off-a-proposal] Incubate a Proposal and Hand It Off to a Spec

## 1. Goal

- **Goal**: The agent turns a request whose direction is open into a direction the user accepted on evidence and a
  spec bundle that carries it, so that the delivery that follows starts from a consistent Living Spec instead of
  dangling links to a deleted proposal.
- **Scope**: the `sdd-proposal` workflow, `devkit spec proposal new|padr|check|accept|handoff` and the `spec`
  skill's Planning and Backlog procedures.
- **Trigger**: The agent classifies a request as `proposal` depth (`UC-route-development-intent`, extension 3b), or
  the user picks a queued draft.
- **Preconditions**: The repository has `devkit-spec` installed with the `sdd-proposal` and `sdd-spec-<task_kind>`
  workflows available.

---

## 2. Main Success Scenario

1. The agent creates a draft proposal bound to `sdd-proposal` in Backlog, and records the user's confirmation of the
   draft, with its proposed Planning effort, as `plan-intent` (`CAP-DLV-proposal-incubation`,
   `CAP-DLV-delivery-workflows`).
2. The agent starts Planning on `plan-<slug>` and sets the proposal in review (`CAP-DLV-delivery-workflows`).
3. The agent gathers evidence through `scout` and criticism through `challenger` as the Planning effort requires,
   records their returns, and records preliminary decisions as PADRs (`CAP-DLV-delivery-workflows`,
   `CAP-DLV-proposal-incubation`).
4. The agent puts every open question to the user in one round, folds the answers into the proposal and its PADRs,
   refines the Development effort hint, and records fresh feedback-sweep coverage before each return to the user
   (`CAP-DLV-delivery-workflows`).
5. After the final Planning commit, the agent reviews the proposal, PADRs and envelopes, and presents findings to the user
   (`CAP-DLV-proposal-incubation`).
6. The user accepts the direction; the agent records the acceptance and the accepted status in one step
   (`CAP-DLV-proposal-incubation`).
7. The agent integrates the Planning branch under `plan-accept`'s authority; the workflow reports the proposal unit
   complete (`CAP-DLV-delivery-workflows`).
8. With `proposal-handoff` authority, the agent starts `dev-<slug>` and hands the proposal off: the system creates the
   spec bundle bound to `sdd-spec-<task_kind>`, promotes the PADRs to accepted ADRs, moves materials and open
   feedback, carries the `plan-intent` and `plan-accept` records by name, rewrites what pointed into the proposal and
   removes it (`CAP-DLV-proposal-incubation`, `CAP-DLV-spec-bundles`).
9. The agent rereads the rewritten references, fixes unresolved links in the same change and follows the spec
   workflow's next stage (`CAP-DLV-proposal-incubation`).

---

## 3. Extensions

- **1a.** The draft's `size` is not absent or exactly `S`, `M` or `L` (an `XL` draft, whose work would need two or
  more specs or a different `task_kind`): the workflow shows the `intent-proposal` size check unmet
  (`detail="size=XL"`) and opens no `plan-intent` request, and recording it is refused with `REQUEST_UNKNOWN`
  (`CAP-DLV-proposal-incubation`); the agent decomposes the draft in Backlog, splitting it with `--decomposed-from` or
  promoting it to a milestone on the user's decision, optionally through the read-only `decomposer` role
  (`CAP-DLV-delivery-workflows`), and never edits the size to pass; the use case ends for the parent.
- **2a.** The draft's direction is settled and nothing needs Planning: on the user's explicit acceptance the agent
  checks eligibility read-only on the base checkout, sweeps the acceptance session and records a direct acceptance,
  with no Planning branch, run, effort or `worker` envelope (`CAP-DLV-proposal-incubation`); resumes at step 7.
- **2b.** A direct acceptance fails a condition (no `plan-intent`, `needs_decompose`, a `size` such as `XL`, `supersedes`, a
  Planning branch, an envelope hold, a checkout other than the base): the system refuses with `SPEC_PROPOSAL_NOT_ELIGIBLE`,
  listing every failed condition, and writes nothing (`CAP-DLV-proposal-incubation`); resumes at step 2 or the use
  case ends.
- **2c.** At pickup the user decides that a queued draft without PADRs is `session` work: the agent deletes the
  draft in one base commit that preserves its open feedback, and does the work as a session under a new slug
  (`CAP-DLV-proposal-incubation`); the use case ends.
- **2d.** Planning finds that the proposal must be split: the run returns it as a draft marked for decomposition and
  closes its open questions; the agent integrates the return, removes the Planning branch, and Backlog creates the
  child drafts once the proposal check passes on the base (`CAP-DLV-proposal-incubation`); while the Planning branch
  exists, Backlog changes are refused with `SPEC_PROPOSAL_IN_PLANNING`; the use case ends.
- **5a.** The user rejects the direction: the agent sets `status: rejected` with the user's reason in the commit
  message, closes the open questions and merges the Planning branch per policy; a later hygiene pass, warned by
  `SPEC_PROPOSAL_REJECTED_PENDING`, writes the rejection ADR, preserves open feedback and deletes the proposal
  (`CAP-DLV-proposal-incubation`); the use case ends.
- **5b.** The workflow does not open `plan-accept` (a missing feedback sweep, an envelope hold): the system refuses
  with `SPEC_PROPOSAL_GATE_NOT_OPEN`, restores the status and lists the unmet checks (`CAP-DLV-proposal-incubation`);
  resumes at step 4.
- **5c.** The owning base and the prospective source both set `plan-accept` to `auto`: the agent records the
  acceptance by policy, reported as policy, never as the user's consent (`CAP-DLV-proposal-incubation`); resumes at
  step 6.
- **7a.** The Host starts Development from the retained base checkout: under `proposal-handoff=ask` it presents the
  accepted plan, the setup and worktree effects and the Development effort defaulting to the `dev_effort` hint, and
  only after the user's conversational approval runs `devkit spec proposal handoff <slug> --effort <level>`; under
  `auto` it runs the same command with `--effort` equal to `dev_effort`. A prerequisite that does not hold refuses
  with `SPEC_HANDOFF_NOT_READY`, and a base, plan or policy change since its check with `SPEC_HANDOFF_STALE`, before
  any effect (exit `2`). When the new worktree no longer holds the reviewed base
  commit or setup changed its files, the command keeps the worktree and reports `status=needs_recovery` with
  `SPEC_HANDOFF_STALE` (exit `1`) for inspection (`CAP-DLV-proposal-incubation`); resumes at step 8.
- **7b.** The proposal is not `accepted`: the system refuses with `SPEC_PROPOSAL_NOT_APPROVED` and writes nothing
  (`CAP-DLV-proposal-incubation`); the agent asks the user; resumes at step 5.
- **7c.** The proposal says `accepted` without its recorded `plan-accept`: the system refuses with
  `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` and writes nothing; without a `worker` envelope the user's acceptance is
  repaired with a direct acceptance on the base, with one the user decides on reverting the Planning merge
  (`CAP-DLV-proposal-incubation`); the use case ends.
- **7d.** The checkout is not on `dev-<slug>`: the system refuses with `SPEC_PROPOSAL_WRONG_WORKTREE` before reading or
  writing (`CAP-DLV-proposal-incubation`); the agent starts or continues `dev-<slug>`; resumes at step 7.
- **7e.** The proposal's `task_kind` is `bugfix`: the spec bundle holds only `spec.md`, bound to `sdd-spec-bugfix`,
  with the target area and boundaries in its carried notes (`CAP-DLV-proposal-incubation`, `CAP-DLV-spec-bundles`);
  resumes at step 8.
- **7f.** A write fails during the handoff: the system rolls back what it wrote and moved, keeps the proposal and
  reports `SPEC_PROPOSAL_HANDOFF_FAILED` (`CAP-DLV-proposal-incubation`); resumes at step 7.

## 4. Postconditions

- **Success guarantee**: A Planning proposal is reviewed at its final committed source before its acceptance. One spec bundle `SPEC-<slug>` replaces the proposal and is bound to `sdd-spec-<task_kind>`.
  Its PADRs are accepted ADRs, its materials and settled feedback live under `docs/materials/`, its open feedback
  sits in the spec with unchanged IDs, statuses and observation dates, and its `plan-intent` and `plan-accept` records
  are carried by name. Live references name the spec and the ADRs. After a direct acceptance the same holds without a
  Planning run.
- **Minimal guarantee**: Approval is never inferred. A refused acceptance or handoff writes nothing, and a failed
  handoff write rolls back and keeps the proposal for a rerun. A rejected or deleted proposal keeps its open feedback
  until it is preserved in the month-level backlog.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: An accepted proposal is handed off
- **Covers**: main success scenario
- **Given**: a proposal bundle with `status: accepted` and its recorded `gate:plan-accept`, one PADR and a non-empty
  `materials/`, in a checkout on `dev-<slug>`
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` exists with `spec.md` bound to `sdd-spec-feature`, the PADR is an
  accepted ADR under `docs/decisions/<YYYY-MM>/`, the materials are under `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`,
  the proposal directory is gone, and the output lists `[PROMOTED_ADR: ...]`, `[MATERIALS: ...]` and
  `[NEXT_CMD: devkit workflow next --unit <dir>]`

### Scenario 2: The proposal's approvals carry by name
- **Covers**: main success scenario
- **Given**: an accepted proposal whose unit recorded `gate:plan-intent` and `gate:plan-accept` by the user
- **When**: the agent hands it off
- **Then**: the spec holds the same two requests as decision records with note `PROP-<slug>: <the record's note>`
  (`PROP-<slug>` when the record has none), each reported as `[CARRIED_GATE: ...]`; `plan-intent` is not asked again
  and `plan-accept` satisfies no spec stage

### Scenario 3: References into the proposal follow it
- **Covers**: main success scenario
- **Given**: a use case that cites the proposal by ID and links its `proposal.md`
- **When**: the handoff completes
- **Then**: the ID now names the spec and the link points at `spec.md`, each reported as a `[REWRITTEN: ...]` line,
  and a `SPEC_PROPOSAL_REFS_REWRITTEN` notice asks the agent to reread the rewritten sentences

### Scenario 4: Planning observations follow the outcome
- **Covers**: main success scenario
- **Given**: a proposal with open and settled feedback, captured inside its own write boundary
- **When**: Planning returns to the user and the proposal is later handed off
- **Then**: each enabled run sweep has fresh recorded coverage, open feedback enters the spec with unchanged IDs,
  statuses and observation dates, settled feedback is preserved as material, and Development supplies its own sweep

### Scenario 5: A settled draft is accepted directly
- **Covers**: 2a
- **Given**: a draft with its `plan-intent` recorded, no `needs_decompose`, `supersedes` or Planning branch, no
  envelope hold, a swept acceptance session, in the base checkout on its base branch
- **When**: after the user's explicit acceptance the agent runs `devkit spec proposal accept <slug> --by user --direct
  --note "<reason>"`
- **Then**: `proposal.md` says `status: accepted`, `gate:plan-accept` is recorded with the note `direct acceptance,
  Planning skipped: <reason>; task_kind <kind> confirmed`, and the output is one `[ACCEPTED: ... form=direct ...]`
  line

### Scenario 6: An ineligible draft is not accepted directly
- **Covers**: 2b
- **Given**: a draft that carries `needs_decompose: true` or `size: XL`
- **When**: the agent runs `devkit spec proposal accept <slug> --by user --direct --note "<reason>"`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_NOT_ELIGIBLE` listing each failed condition as a `blocking:` or
  `pending:` detail, and writes nothing

### Scenario 7: Deletion without handoff preserves open work
- **Covers**: 2c, 2d, 5a
- **Given**: rejected or decomposed proposal feedback, or a queued draft the user decided to do as a `session` task at
  pickup
- **When**: the Host deletes the original proposal
- **Then**: open feedback is preserved once in the month-level backlog with retrievable historical context and valid
  current references; invalid input, collisions or unresolved live dependencies prevent deletion

### Scenario 8: Backlog leaves a proposal in Planning alone
- **Covers**: 2d
- **Given**: a draft whose `plan-<slug>` branch exists locally or as a fetched remote branch
- **When**: the agent runs `devkit spec proposal check <slug>` before splitting it
- **Then**: the command refuses with `SPEC_PROPOSAL_IN_PLANNING`, and the draft is left to its Planning branch

### Scenario 9: A rejected proposal waits for its cleanup
- **Covers**: 5a
- **Given**: a proposal whose direction the user rejected in Planning, its Planning branch merged per policy with
  `status: rejected` and the user's reason in the commit message, and still in the base
- **When**: the agent runs `devkit rules check -p hygiene` on the whole workspace
- **Then**: a `SPEC_PROPOSAL_REJECTED_PENDING` warning names it, and its `[FIX]` writes the rejection ADR and deletes
  the proposal in one commit

### Scenario 10: An unopened acceptance gate restores the proposal
- **Covers**: 5b
- **Given**: a proposal in review on `plan-<slug>` whose `collect-feedback` sweep is missing
- **When**: the agent runs `devkit spec proposal accept <slug> --by user`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_GATE_NOT_OPEN`, `proposal.md` is restored byte for byte, and
  `[DETAIL]` lists the unmet checks

### Scenario 11: Policy accepts the direction
- **Covers**: 5c
- **Given**: the owning base and the proposal's branch both set `[workflow.approvals] plan-accept = "auto"`
- **When**: the agent runs `devkit spec proposal accept <slug> --by policy`
- **Then**: the proposal is `accepted` with `gate:plan-accept` recorded by `policy`, and the report names the policy,
  never a user approval

### Scenario 12: Host-authorized CLI handoff starts Development with a chosen effort
- **Covers**: 7a
- **Given**: an accepted proposal on a clean base checkout under `proposal-handoff=ask`
- **When**: the Host presents the findings and setup/worktree effects, receives the user's conversational approval, then
  runs `devkit spec proposal handoff <slug> --effort high`
- **Then**: `dev-<slug>` and its worktree exist, the handoff ran there, and the result returns `status=handed_off`
  with effort `high`; without the user's decision, the Host does not invoke the command

### Scenario 13: Approval is never inferred
- **Covers**: 7b
- **Given**: a proposal with `status: draft` or `reviewing`: `plan-accept` was not given
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_NOT_APPROVED`, whose `[FIX]` names `devkit spec proposal
  accept`, and writes nothing

### Scenario 14: An unrecorded acceptance is refused
- **Covers**: 7c
- **Given**: a proposal bound to `sdd-proposal` that says `accepted` without its recorded `gate:plan-accept`
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` and writes nothing

### Scenario 15: Handoff refuses another branch
- **Covers**: 7d
- **Given**: an accepted proposal in a checkout on its base branch
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_WRONG_WORKTREE`, whose `[FIX]` starts or continues `dev-<slug>`,
  and nothing is read or written

### Scenario 16: A defect proposal hands off to the bugfix workflow
- **Covers**: 7e
- **Given**: a proposal created with `--task-kind bugfix` and accepted
- **When**: the agent hands it off
- **Then**: the spec bundle holds only `spec.md`, bound to `sdd-spec-bugfix`, and the proposal's target area and
  boundaries appear in its `### Target Area & Boundaries` notes

### Scenario 17: A failed handoff write keeps the proposal
- **Covers**: 7f
- **Given**: an accepted proposal whose materials move fails partway (for example, a read-only destination
  directory)
- **When**: the agent runs `devkit spec proposal handoff <slug>`
- **Then**: the command exits `2` with `SPEC_PROPOSAL_HANDOFF_FAILED`, what was written is removed, what was moved is
  moved back, and the proposal stays for a rerun


### Scenario 18: Proposal review briefing can be viewed before acceptance
- **Covers**: main success scenario, step 5
- **Given**: a Planning proposal ready for `plan-accept`
- **When**: the agent or user runs `devkit spec proposal report <slug>`
- **Then**: the briefing template is rendered for that source SHA without requiring shared artifact publication
