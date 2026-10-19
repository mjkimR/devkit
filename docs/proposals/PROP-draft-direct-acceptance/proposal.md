---
id: PROP-draft-direct-acceptance
title: Direct acceptance of drafts that need no Planning
summary: Lets the user accept a draft proposal whose direction is already settled without a Planning branch, through one validated command that records the user's plan-accept with a Planning-skipped note, so small drafts such as decomposition results go straight to handoff.
status: reviewing                      # draft | reviewing | accepted | rejected
created_at: 2026-10-16
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
    - capabilities/harness/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
workflow_hash: sha256:90918c632715461d07f99f683b8381bdbe6381ad6689a7575a72c002c18c1399
---

# [PROP-draft-direct-acceptance] Direct acceptance of drafts that need no Planning

- **Parent design**: the strategy layer's master flow (workbench `docs/strategy-layer/01-master-flow.md`, §5.1 Backlog
  edits drafts only and names this proposal as the follow-up, §6.2 proposal Planning, §4.4 proposal states) and policy
  (`03-policy.md` §1 Backlog is outside the policies, §4 Planning acceptance commits go through the Planning PR under
  `required`).
- **Origin**: `SPEC-backlog-roadmap-and-issues` (completed) makes every request not yet started a draft proposal and
  has a decomposition yield drafts only; until this path exists, small drafts run Planning at `low` effort
  (the `spec` skill's `references/backlog.md`, `ADR-roadmap-in-repository`).
- **Related**: `ADR-task-kind-and-planning-depth` (depth is lowered only by a proposal's handoff),
  `CAP-DLV-proposal-incubation`, `CAP-DLV-delivery-workflows`, `PROP-direct-planning-procedure` (Planning steps for
  any executor; independent, both edit the `spec` skill).
- **Planning material**: [options](materials/options-comparison.md), [engine evidence](materials/engine-evidence.md).

## 1. Background & Hypothesis

### 1.1 Problem

- **Small drafts pay for a Planning they do not need.** Once every request not yet started is a draft, many drafts
  carry a settled direction: a piece split off a larger request, a follow-up promoted from feedback, a request whose
  contract is clear. Planning at `low` still starts `plan-<slug>`, commits `status: reviewing`, records `plan-accept`
  and merges the branch, then Development starts `dev-<slug>`: two branches, and two PRs under
  `pull_request = required`, for one decision the user could make on sight.
- **Effort cannot express it.** `activity-effort` sets how thoroughly an activity is done; skipping the activity is a
  routing decision, not a lower thoroughness, so an effort value such as `skip` would blur the axis.
- **Nothing may accept a draft today.** Backlog changes only a `draft` (01 §5.1, `devkit spec proposal check`), and the
  `sdd-proposal` body records `plan-accept` only for a proposal in review, on `plan-<slug>`, never on the base.
- **The engine allows it with one condition.** `gate:plan-accept` opens once `collect-feedback` passes and
  `proposal.md` says `reviewing` or `accepted`; the handoff needs only `status: accepted`. So the stage schema can
  stay, provided the executor of a direct acceptance sweeps its own session first. The handoff does not check the
  gate record itself, so a hand-set status would hand off without the user's acceptance
  ([engine evidence](materials/engine-evidence.md)).

### 1.2 Hypothesis

A direct acceptance, in which the user gives `plan-accept` on sight for an eligible draft and one validated command
records it, removes the Planning branch for drafts that need no Planning while keeping both human decisions explicit
and recorded, and keeps the proposal body, gates and provenance carried by the handoff.

## 2. Technical Spike Questions

- **Q1. Eligibility.** Answered in `PADR-eligibility-for-direct-acceptance`: checked by the tool (draft, accepted
  `plan-intent`, no `needs_decompose`, no `supersedes`, no `plan-<slug>`, valid `task_kind`) plus the Host's judgment
  that the direction leaves nothing to compare, shown to the user. No size limit.
- **Q2. Gates.** Open for the user (question `gates-in-one-exchange`): whether one request may carry `plan-intent`
  and `plan-accept` together for a draft without a recorded intent. Either way they are two records, each the user's
  explicit answer; neither is inferred from the other.
- **Q3. Policy.** Depends on where the acceptance is committed (question `acceptance-point`): on the base it needs an
  exception to 03 §4; on `dev-<slug>` it is reviewed in the Development PR and needs none.
- **Q4. Reclassification.** Open for the user (question `session-reclassification`). Reclassifying to a `spec` Unit
  is not needed: direct acceptance reaches the same Unit and keeps the body and provenance. The draft listed an
  `issue` field among the carried values; devkit-spec has none (tracker fields were removed).
- **Q5. Tooling.** Answered in `PADR-direct-acceptance-command-and-handoff-guard`: a command checks eligibility and
  the sweep, writes the status and records the gate in one step; the handoff also requires the gate record; the stage
  schema stays; `check` gets no mode.
- **Q6. Visibility.** Answered in the same PADR: the acceptance request shows "Planning: skipped (direct acceptance)"
  where a Planning acceptance shows its applied effort and support roles (the `sdd-proposal` gate rules, not a
  follow-up of `SPEC-backlog-roadmap-and-issues`), with the eligibility reason, the PADRs to be promoted and
  `dev_effort`.

## 3. Proposed Design & Impact

### 3.1 Direction under review

Three ways were compared ([options](materials/options-comparison.md)); the user chooses (question
`acceptance-point`). The recommendation is **B**.

- **B. Acceptance at Development start** (recommended): when Development of an eligible draft starts, the Host
  proposes direct acceptance with the eligibility reason and the `dev_effort` hint. On the user's explicit acceptance
  it starts `dev-<slug>`, sweeps its own session (`collect-feedback`), runs the acceptance command there and commits,
  then runs `devkit spec proposal handoff` and continues Development; a worker or Cloud Agent may take over from the
  committed branch, as after inline Planning of a `spec` task. One branch, one PR; the acceptance is reviewed in it.
  `devkit spec proposal check` also refuses while `dev-<slug>` exists, because the base still shows the draft until
  the Development PR is merged.
- **A. Acceptance in Backlog on the base** (the draft's working direction): the same command on the base as Backlog
  work; the draft becomes `accepted` and waits for any later Development. Needs an exception to 03 §4 under
  `required` and makes every directly accepted draft an in-progress Unit at once.
- **C. Reclassify to a spec Unit at pickup**: no acceptance; a conversion command and a second way of lowering depth.
  Not recommended.

Common to A and B:

- **Record**: the `plan-accept` note states that Planning was skipped and why the draft was eligible, as a decision,
  never the conversation; the handoff carries it by name like any acceptance.
- **Command and guard**: `PADR-direct-acceptance-command-and-handoff-guard`.
- **Eligibility**: `PADR-eligibility-for-direct-acceptance`.

### 3.2 Strategy-layer changes first (ordering dependency)

The strategy layer lives in the workbench repository; this package cannot change it, and its 01 is the SSOT. Before
Development here, the workbench updates (for B; A adds the items marked A):

- 01 §5.1: replace "Planning without acceptance is a follow-up" with the direct-acceptance path and its eligibility;
  small drafts no longer default to Planning at `low`.
- 01 §4.4 table: `accepted` may also be set by the Host at a direct acceptance (on `dev-<slug>`; A: on the base).
- 01 §3 gate table: `plan-accept` is the Planning branch's merge approval only when a Planning branch exists; a direct
  acceptance has none.
- 01 §6.2 or §7: the direct path (B: as the first step of Development, before handoff); §2.2 unchanged (depth is still
  lowered only through a handoff after `plan-accept`).
- 01 §4.7 / §5.1 Backlog guard: a draft with a `dev-<slug>` branch is not editable (B).
- A only: 03 §1 and §4, the acceptance commit as Backlog work outside the PR policy.
- 01 §5.2 needs no change: decomposition children are drafts like any other.

### 3.3 Impact in this repository

- `devkit-spec` code: the acceptance command, the handoff guard, and (B) the `dev-<slug>` branch in the Backlog guard;
  tests for each.
- `CAP-DLV-proposal-incubation`: the approval rule (rule 2), the Backlog guard (rule 13), the command and codes.
- `CAP-DLV-delivery-workflows` and the `sdd-proposal` body: where `plan-accept` may be recorded and for which status;
  the stage schema is unchanged.
- The `spec` skill: `references/backlog.md` (drop "until direct acceptance exists"), `references/classification.md`
  (§1 routing, §4 "a new draft runs Planning anew" stays for supersede and depth-escalation drafts), the proposal row
  of the routing table; `spec-next` (the acceptance proposal at Development start, `references/next-work.md`).

### 3.4 Non-Goals

- **Scope Excluded**: a `skip` value for `activity-effort`.
- **Scope Excluded**: accepting without the user. Policy delegation (`auto`) never applies to `plan-intent` or
  `plan-accept`, and the command records only after the user's explicit acceptance.
- **Scope Excluded**: lowering depth any other way than a proposal's handoff (unless the user allows the
  `session` reclassification asked in `session-reclassification`).
- **Scope Excluded**: the plain `accept` form for a proposal in review, and changes to the strategy-layer documents
  themselves.

## 4. Lifecycle & Retirement Criteria

- **Depends on**: `SPEC-backlog-roadmap-and-issues` (completed). The workbench strategy-layer update (§3.2) comes
  first; Development here follows it.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff draft-direct-acceptance`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
