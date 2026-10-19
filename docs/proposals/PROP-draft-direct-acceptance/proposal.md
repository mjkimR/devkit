---
id: PROP-draft-direct-acceptance
title: Direct acceptance of drafts that need no Planning
summary: Lets the user accept a draft proposal whose direction is already settled in Backlog without a Planning run, through one validated command that records the user's plan-accept with a Planning-skipped note, so small drafts such as decomposition results go straight to handoff.
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
- **Related**: the lowering rule (depth is lowered only by a proposal's handoff: 01 §2.2, the `spec` skill's
  `references/classification.md` §3), `ADR-task-kind-and-planning-depth` (the axes and gates),
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

A direct acceptance, in which the user gives `plan-accept` on sight for an eligible draft during Backlog and one
validated command records it, removes the Planning run (and, under `pull_request = auto`, the Planning branch) for
drafts that need no Planning, while keeping both human decisions explicit and recorded and keeping the proposal body,
gates and provenance carried by the handoff.

## 2. Technical Spike Questions

- **Q1. Eligibility.** Answered in `PADR-eligibility-for-direct-acceptance`: checked by the tool (draft, accepted
  `plan-intent`, no `needs_decompose`, no `supersedes`, no Planning branch elsewhere, valid `task_kind`, also as a
  read-only pre-check) plus the Host's judgment that the direction leaves nothing to compare, shown to the user with
  the recorded `planning_effort` hint. No size limit.
- **Q2. Gates.** Open for the user (question `gates-in-one-exchange`): whether one request may carry `plan-intent`
  and `plan-accept` together for a draft without a recorded intent. Either way they are two records, each the user's
  explicit answer; neither is inferred from the other.
- **Q3. Policy.** Open for the user (question `acceptance-point`): the recommended A1 follows the PR policy (a Backlog
  commit under `auto`, a one-commit Planning PR under `required`), so 03 §4 stays; A2 drops the PR under `required`
  too and needs an exception to 03 §4.
- **Q4. Reclassification.** Open for the user (question `session-reclassification`). Reclassifying to a `spec` Unit
  is not needed: direct acceptance reaches the same Unit and keeps the body, provenance and the `plan-accept` record
  the closes depend on. The draft listed an `issue` field among the carried values; devkit-spec has none.
- **Q5. Tooling.** Answered in `PADR-direct-acceptance-command-and-handoff-guard`: a command checks eligibility,
  writes the status and records the gate through the engine in one step, with a read-only `--check`; the handoff of
  a bound bundle also requires the gate record; the stage schema stays; `devkit spec proposal check` gets no mode.
- **Q6. Visibility.** Answered in the same PADR: the acceptance request shows "Planning: skipped (direct acceptance)"
  where a Planning acceptance shows its applied effort and support roles (the `sdd-proposal` gate rules), with
  `task_kind`, the `planning_effort` hint, the eligibility reason, the PADRs to be promoted and `dev_effort`.

## 3. Proposed Design & Impact

### 3.1 Direction under review

Four ways were compared ([options](materials/options-comparison.md), revised after the `challenger` pass); the user
chooses (question `acceptance-point`). The recommendation is **A1**.

- **A1. Backlog acceptance under the PR policy** (recommended): in Backlog the Host proposes direct acceptance for an
  eligible draft (read-only `--check` first) with the eligibility reason, `task_kind` and the effort hints. On the
  user's explicit acceptance it sweeps its own session (`collect-feedback`), runs the acceptance command and commits:
  on the base as Backlog work under `pull_request = auto`; under `required` as the only commit of a `plan-<slug>`
  branch merged through its PR, as a Planning acceptance commit is today. Development later starts `dev-<slug>` and
  runs `devkit spec proposal handoff` as for any accepted proposal, in any mode (autohub included).
- **A2. Backlog acceptance on the base, always**: as A1, without the PR under `required` (an exception to 03 §4).
- **B. Acceptance at Development start on `dev-<slug>`**: one PR, but it breaks 01 §4.7 (separate Planning and
  Development PRs) and the 01 §7.4 closes, and needs guards for a draft owned by Development. Not recommended.
- **C. Reclassify to a spec Unit at pickup**: no `plan-accept` record; a conversion command. Not recommended.

Common to every option kept:

- **Record**: the `plan-accept` note states that Planning was skipped, why the draft was eligible and the confirmed
  `task_kind`, as a decision, never the conversation; the handoff carries it by name like any acceptance.
- **Command and guard**: `PADR-direct-acceptance-command-and-handoff-guard`.
- **Eligibility**: `PADR-eligibility-for-direct-acceptance`.
- **Depth**: direct acceptance lowers the effective depth of a queued draft on the user's explicit `plan-accept`;
  01 §2.2 names it as the approved route instead of keeping a wording it no longer matches.

### 3.2 Strategy-layer changes first (ordering dependency)

The strategy layer lives in the workbench repository; this package cannot change it, and its 01 is the SSOT. Before
Development here, the workbench updates (for A1):

- 01 §5.1: replace "accepting without Planning is a follow-up (`PROP-draft-direct-acceptance`)" and "small drafts run
  Planning at `low`" with the direct-acceptance path and its eligibility; Backlog may accept an eligible draft.
- 01 §4.4 table: `accepted` may also be set by the Host at a direct acceptance in Backlog, from `draft`.
- 01 §6.2: the direct path beside Planning (who records, the sweep of the acceptance session, the request contents);
  §3 gate table: `plan-accept` is the Planning branch's merge approval when a Planning branch exists.
- 01 §2.2: depth is lowered only through a handoff after `plan-accept`, which a direct acceptance gives on sight.
- 03 §1: a direct acceptance is Backlog work under `auto`; 03 §4 already covers the acceptance commit under
  `required` (A1); A2 instead adds an exception there.
- 01 §4.7, §7.1, §7.4 and §5.2 need no change under A1 (B would change §4.7 and §7.4).

### 3.3 Impact in this repository

- `devkit-spec` code: the acceptance command with `--check`, the handoff guard for bound bundles; tests for each, and
  existing handoff tests that rely on the status alone.
- `CAP-DLV-proposal-incubation`: the approval rule (rule 2), the Backlog guard (rule 13: Backlog may also accept an
  eligible draft), the command, its codes and output.
- `CAP-DLV-delivery-workflows` and the `sdd-proposal` body: `plan-accept` may be recorded for a draft through a
  direct acceptance, on the base under `auto`; the stage schema is unchanged.
- The `spec` skill: `references/backlog.md` (drop "until direct acceptance exists", add the path),
  `references/classification.md` (§1 routing, §3 lowering rule, §4 "a new draft runs Planning anew" stays for
  supersede and depth-escalation drafts), the proposal row of the routing table, `references/worktree.md` (the
  accepted proposal may come from a direct acceptance); `spec-next` (`references/next-work.md`: offer direct acceptance
  for an eligible draft).
- `PROP-direct-planning-procedure` also edits the `spec` skill; whichever lands second rebases its text.

### 3.4 Non-Goals

- **Scope Excluded**: a `skip` value for `activity-effort`.
- **Scope Excluded**: accepting without the user. Policy delegation (`auto`) never applies to `plan-intent` or
  `plan-accept`, and the command records only after the user's explicit acceptance.
- **Scope Excluded**: lowering depth any other way than a proposal's handoff (unless the user allows the `session`
  reclassification asked in `session-reclassification`).
- **Scope Excluded**: an autohub UI for direct acceptance (Backlog is `direct` only), the plain `accept` form for a
  proposal in review, and the strategy-layer documents themselves.

## 4. Lifecycle & Retirement Criteria

- **Depends on**: `SPEC-backlog-roadmap-and-issues` (completed). The workbench strategy-layer update (§3.2) comes
  first; Development here follows it.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff draft-direct-acceptance`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
