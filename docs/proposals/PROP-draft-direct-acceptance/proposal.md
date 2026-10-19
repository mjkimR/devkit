---
id: PROP-draft-direct-acceptance
title: Direct acceptance of drafts that need no Planning
summary: Lets the user accept a draft proposal whose direction is already settled in Backlog, without a Planning branch or run, through the planned accept command recording the user's plan-accept with a Planning-skipped note, so small drafts go straight to handoff.
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
validated command records it on the base as Backlog work, removes the Planning branch, its PR and the Planning run for
drafts that need no Planning, while keeping both human decisions explicit and recorded and keeping the proposal body,
gates and provenance carried by the handoff.

## 2. Technical Spike Questions

- **Q1. Eligibility.** Answered in `PADR-eligibility-for-direct-acceptance`: checked by the tool (draft, accepted
  `plan-intent`, no `needs_decompose`, no `supersedes`, no Planning branch, no envelope hold, valid `task_kind`, the
  path's conditions; also as a read-only check) plus the Host's judgment that the direction leaves nothing to compare,
  shown to the user with the recorded `planning_effort` hint. No size limit.
- **Q2. Gates.** Open for the user (question `gates-in-one-exchange`): whether one request may carry `plan-intent`
  and `plan-accept` together for a draft without a recorded intent. Either way they are two records, each the user's
  explicit answer; neither is inferred from the other.
- **Q3. Policy.** Open for the user (question `acceptance-point`). The recommended A2 is Backlog work on the base
  under every policy, inside the existing Backlog exemption (01 §5.1, 03 §1); under `required` the request says the
  direction gets no PR review and the user may choose Planning for that draft. A2a would offer it only under `auto`,
  which needs its own rule and makes a policy key decide the flow structure (03 §1).
- **Q4. Reclassification.** Open for the user (question `session-reclassification`). Reclassifying to a `spec` Unit
  is not needed: direct acceptance reaches the same Unit and keeps the body, provenance and the `plan-accept` record
  the closes depend on. The draft listed an `issue` field among the carried values; devkit-spec has none.
- **Q5. Tooling.** Answered in `PADR-direct-acceptance-command-and-handoff-guard`: the `accept` command 01 §10
  already plans, with a `--direct` variant for an eligible draft, a read-only `--check` and a repair of an acceptance
  without its gate record (after the user's explicit acceptance), records the acceptance through the engine in one
  step; the handoff of a bound bundle also requires the gate record and keeps its note; the stage schema stays;
  `devkit spec proposal check` gets no mode.
- **Q6. Visibility.** Answered in the same PADR: the acceptance request shows "Planning: skipped (direct acceptance)"
  where a Planning acceptance shows its applied effort and support roles (the `sdd-proposal` gate rules), with
  `task_kind`, the `planning_effort` hint, the eligibility reason, the PADRs to be promoted and `dev_effort`.

## 3. Proposed Design & Impact

### 3.1 Direction under review

Seven ways, the status quo included, were compared ([options](materials/options-comparison.md), revised after four
`challenger` passes); the user chooses (question `acceptance-point`). The recommendation is **A2**.

- **A2. Backlog acceptance on the base** (recommended): in Backlog the Host proposes direct acceptance for an eligible
  draft (read-only `--check` first; a missing `plan-intent` shows as pending when the request asks for both) with the
  eligibility reason, `task_kind` and the effort hints, and under `pull_request = required` the note that the
  direction gets no PR review. On the user's explicit acceptance it sweeps its own session (`collect-feedback`), runs
  `devkit spec proposal accept <slug> --by user --direct --note "<reason>"` on the base checkout and commits the result
  as Backlog work, under every policy like Backlog's other changes. Development later starts `dev-<slug>` and runs
  `devkit spec proposal handoff` as for any accepted proposal, in any mode (autohub included). It saves the branch,
  its merge or PR, the `reviewing` commit, the worker record and the question round; the saving per configuration is
  in the comparison.
- **A2a. A2 under `pull_request = auto` only**: keeps the Planning PR under `required`, but needs a rule of its own and
  amendments of the Backlog exemption, because a policy key would decide whether a proposal gets a Planning branch.
- **A3. A one-commit Planning branch**: no structural change, but against today's Planning at `low` it saves only a
  commit, a record and a question round; dominated by D.
- **D. No new path**: keep Planning at `low` for small drafts; ship only the handoff guard and the planned `accept`
  command. The alternative to A2 if its saving does not justify the strategy edits.
- **B** (acceptance on `dev-<slug>`) and **C** (reclassify to a spec Unit) are not recommended: B breaks 01 §4.7 and
  §7.4 and needs four guards, C loses the `plan-accept` record the closes depend on.

Common to the direct-acceptance options:

- **Record**: the `plan-accept` note states that Planning was skipped, why the draft was eligible and the confirmed
  `task_kind`, as a decision, never the conversation; the handoff carries the gate with its note
  (`PROP-<slug>: <note>`), so the spec shows how its direction was accepted.
- **No run**: a direct acceptance has no Planning run, no `activity-effort` and no `worker` envelope; its sweep covers
  the acceptance session.
- **Command and guard**: `PADR-direct-acceptance-command-and-handoff-guard`.
- **Eligibility**: `PADR-eligibility-for-direct-acceptance`.
- **Depth**: direct acceptance lowers the effective depth of a queued draft on the user's explicit `plan-accept`;
  01 §2.2 names it as the approved route instead of keeping a wording it no longer matches.

### 3.2 Strategy-layer changes first (ordering dependency)

The strategy layer lives in the workbench repository; this package cannot change it, and its 01 is the SSOT. Before
Development here, the workbench updates (for A2):

- 01 §5.1 and Q55: replace "accepting without Planning is a follow-up (`PROP-draft-direct-acceptance`)" and "small
  drafts run Planning at `low`" with the direct acceptance: Backlog may accept an eligible draft, on the base checkout,
  outside the worktree and PR policies like its other work.
- 01 §4.7: a direct acceptance is the one proposal status change Backlog makes on the base without a merge, beside the
  draft edits it already makes; Planning and Development keep their own branches.
- 01 §1 (activity table and diagram) and §4.4 table: Backlog may give `plan-accept` for an eligible draft; `accepted`
  may be set from `draft` by the Host at a direct acceptance.
- 01 §6.2 (or §5): the direct acceptance: eligibility, the read-only check, base push access settled first, the sweep
  of the acceptance session, the request contents (Planning skipped, `task_kind`, `planning_effort`, `dev_effort`
  reviewed by the Host as a Planning executor would, 01 §2.3, and under `required` the missing PR review), no run, no
  worker envelope (the §8 `worker` row), no `activity-effort`.
- 01 §3 gate table and §2.2: `plan-accept` may be given on sight for an eligible draft, and it is the Planning
  branch's merge approval only when there is one; depth is still lowered only through a handoff after `plan-accept`,
  and this is the approved route for a queued draft.
- 01 §4.2: acceptances are recorded with `devkit spec proposal accept`, other gates with `devkit workflow answer`.
- 01 §5.5: `spec-next` may recommend direct acceptance for an eligible draft beside Planning.
- 01 §10 (devkit-spec rows): the planned proposal status-transition CLI gains `--direct`, `--check` and the repair;
  new rows for the handoff guard and the carried note.
- 03 §3 (Backlog row): a direct acceptance commits on the base checkout, not on another activity branch; 03 §4 (last
  bullet): a direct acceptance is Backlog work and takes no PR, also under `required`.
- No change to 01 §5.2, §7.1, §7.4 or 03 §1.

### 3.3 Impact in this repository

- `devkit-spec` code: `devkit spec proposal accept` (the Planning form, `--direct`, `--check`, the repair) and its
  library function; the handoff guard for bound bundles with its own code (`errors.py`); the carried gate note; tests
  for each, and existing handoff tests that rely on the status alone.
- `CAP-DLV-proposal-incubation`: the approval rule (rule 2), rule 12 (the carried note), rule 13 (Backlog may accept
  an eligible draft), the command, its codes in the code table and its output.
- `CAP-DLV-delivery-workflows` and the `sdd-proposal` body: the gate rules (a direct acceptance records `plan-accept`
  for a draft on the base, without `reviewing`; acceptances use the command) and the Planning feedback section (a
  direct acceptance has no run or worker record; its sweep covers the acceptance session); in the schema only the
  `direction-handoff` comment ("never for a draft") changes, while stages, checks and gates stay.
- The `spec` skill: `references/backlog.md` (drop "until direct acceptance exists", add the path and its base-checkout
  rule beside the Backlog commit rule),
  `references/classification.md` (§1 routing, §3 lowering rule; §4 "a new draft runs Planning anew" stays for
  supersede and depth-escalation drafts), `references/effort.md` (a direct acceptance has no activity-effort), the
  proposal row of the routing table, `references/worktree.md` (the accepted proposal may come from a direct
  acceptance); `spec-next` (`SKILL.md` stage rows, `references/next-work.md` and `references/workflow-signals.md`:
  an eligible draft may be offered for direct acceptance).
- The proposal template's lifecycle line (`proposals/scaffold.py`): it says acceptance merges the Planning branch;
  make it hold for a direct acceptance.
- `PROP-direct-planning-procedure` also edits the `spec` skill; whichever lands second rebases its text.

### 3.4 Non-Goals

- **Scope Excluded**: a `skip` value for `activity-effort`.
- **Scope Excluded**: accepting without the user. Policy delegation (`auto`) never applies to `plan-intent` or
  `plan-accept`, and the command records only after the user's explicit acceptance.
- **Scope Excluded**: lowering depth any other way than a proposal's handoff (unless the user allows the `session`
  reclassification asked in `session-reclassification`).
- **Scope Excluded**: an autohub UI for direct acceptance (Backlog is `direct` only), the `reject` command 01 §10
  plans, and the strategy-layer documents themselves.

## 4. Lifecycle & Retirement Criteria

- **Depends on**: `SPEC-backlog-roadmap-and-issues` (completed). The workbench strategy-layer update (§3.2) comes
  first; Development here follows it.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff draft-direct-acceptance`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
