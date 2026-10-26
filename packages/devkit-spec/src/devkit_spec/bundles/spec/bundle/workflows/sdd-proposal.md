---
id: sdd-proposal
title: "Proposal (planning-depth proposal: plan-intent, review, plan-accept, handoff)"
status: active
schema_version: 1
gates:
  plan-intent: { policies: [ask, auto] }  # task intent; explicit user instructions need no repeated prompt
  plan-accept: { policies: [ask, auto] }  # direction decision, user or owning policy
# Shared stages must match across workflows (`devkit workflow validate`); returns are this workflow's own.
# No `next` list: devkit's handoff cannot move a unit across layouts; `devkit spec proposal handoff` does.
layout:
  work_dir: docs/proposals
  unit_path: "PROP-{slug}"
  anchor: proposal.md
checks:
  - { name: exception-raised, class: human, description: "a retry cap, tool failure or unresolved semantic conflict was raised" }
  - { name: exception-handled, class: human, description: "the cause of the exception was handled by the user" }
stages:
  - id: intent-proposal
    name: Plan intent
    human_gate: plan-intent
    entry: []
    exit: [anchor-exists]
    artifacts: [docs/proposals/PROP-<slug>/proposal.md]
    skills: [spec]
    role: developer
    isolation: none
    returns: []
  - id: spike
    name: Spike (optional)
    optional: true
    human_gate: false
    entry: [anchor-exists]
    exit: []
    artifacts: [docs/proposals/PROP-<slug>/materials/]
    skills: [spec-delegate]
    role: scout
    isolation: preferred
    returns:
      - { to: intent-proposal, when: the goal itself is unclear }
  - id: collect-feedback
    name: Collect feedback
    human_gate: false
    entry: [anchor-exists]
    exit: [envelope-check-pass(feedback swept)]
    artifacts: [feedback/*.md, envelopes/feedback-NN.yaml]
    skills: [spec-feedback]
    role: developer
    isolation: none
    returns: []
  - id: direction-handoff
    name: Plan accept
    human_gate: plan-accept
    entry: [anchor-exists]
    # Asked for a proposal in review, or for an eligible draft once `devkit spec proposal accept --direct` wrote
    # accepted (a direct acceptance); never again for a rejected one (01 §4.4, §6.2). For a rejected proposal this
    # exit stays unmet for good: Planning has ended, and the proposal waits for hygiene.
    exit: [frontmatter(proposal.md status reviewing|accepted)]
    artifacts: ["proposal.md with status accepted and the recorded gate:plan-accept"]
    skills: [spec]
    role: developer
    isolation: none
    returns:
      - { to: spike, when: the choice needs more evidence }
  - id: handoff
    name: Handoff
    human_gate: false
    entry: [anchor-exists]
    exit: []
    artifacts: [specs/<YYYY-MM>/<YYYYMMDD>-<slug>/ bound to sdd-spec-<task_kind>]
    skills: [spec, spec-next]
    role: developer
    isolation: none
    # No return to direction-handoff: Development never returns to Planning (01 §4.7). A premise of the accepted
    # proposal that no longer holds is a problem, then a close (01 §7.3, §7.4), never a change of the proposal.
    returns: []
  - id: exception
    name: Exception
    exception: true
    human_gate: false
    entry: [exception-raised]
    exit: [exception-handled]
    artifacts: [exception report]
    skills: [spec]
    role: developer
    isolation: none
    returns:
      - { to: handoff, when: "the stage that raised it, after the cause is handled" }
---

# Proposal (`planning-depth` proposal)

The direction must be decided first: options are explored and compared in a proposal bundle `docs/proposals/PROP-<slug>/` (anchor `proposal.md`, created in Backlog with `devkit spec proposal new <slug>`, which binds it to this workflow) before any spec exists. The criterion is what must be decided before implementation, not size. The workflow ends at handoff: `devkit spec proposal handoff <slug>` moves the accepted proposal into a new spec bundle `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` bound to `sdd-spec-<task_kind>` (the proposal's `task_kind`, `feature` or `bugfix`, confirmed at `plan-accept`), after which that workflow's stages and gates apply. A team review (a PR on the Planning branch with assigned reviewers) is this depth plus PR policy, not a separate workflow.

The frontmatter is the only stage definition (`devkit workflow show --unit <dir>`); `devkit workflow next --unit docs/proposals/PROP-<slug>` names the current stage. This document keeps only the rules the schema cannot express.

| proposal `status` | stage | who changes it |
| --- | --- | --- |
| `draft` | `intent-proposal` | whoever adds the draft, in any activity; `plan-intent` is the user's confirmation of the draft in Backlog |
| `reviewing` | `spike`, `collect-feedback`, `direction-handoff` | the executor that starts Planning, on the `plan-<slug>` branch |
| `accepted` | `plan-accept` passed | `devkit spec proposal accept` after the user's acceptance (Host locally, autohub in `cloud-pr`); from `draft` at a direct acceptance in Backlog |
| `rejected` | Planning ends | the Host or autohub that received the rejection, status only |

- **Planning starts** only from a draft with `plan-intent` recorded and without `needs_decompose: true`, on its own branch `plan-<slug>`. A draft found to need splitting during Planning goes back to Backlog: set `status: draft` and `needs_decompose: true`, keep what the review learned in `materials/`, close every question still open with an `answer` envelope (`choice: null`, the return to Backlog as the decision), and merge the Planning branch.
- **Spike** never becomes the current stage on its own: run it whenever the Planning `activity-effort` requires a `challenger` or `scout` (the `spec` skill's `references/effort.md`: at `low` questions only, at `medium` one `challenger` pass and a `scout` when the direction needs evidence, at `high` both required, in the bounded rounds of its `references/review-loop.md`). The Planning effort (`planning_effort` hint in `proposal.md`) is proposed with `plan-intent`. Its materials go under the proposal's `materials/` and move to `docs/materials/` at handoff. Zero findings is a valid spike result.
- **Handoff** has no exit check: once `plan-accept` holds, `next` reports the unit complete (`[STAGE: - complete=true]`). Merge the Planning branch (a direct acceptance has none), then run `devkit spec proposal handoff <slug>` as Development's first step on `dev-<slug>` (the `spec` skill's `references/worktree.md` §1).

## Gate rules

- `plan-intent` records authorized task intent without repeating consent. `plan-accept` decides direction and `proposal-handoff` authorizes Development; each main boundary permits `ask` or `auto`. Everything after handoff belongs to the bound workflow, which carries both records under their own names.
- **Questions are collected in one round** in the run's `worker` envelope (`questions`, status `needs_input`). They hold `plan-accept` and the Planning branch's merge until an `answer` envelope answers each (`[PENDING_QUESTION]`); `plan-intent`, passed before, stays passed. Asking, rewriting and recording the answers: the `spec` skill's `references/worker-records.md`.
- **`plan-accept` is the acceptance of the direction** and, when there is a Planning branch, the approval to merge it. Ask and record it for a proposal in review (`status: reviewing`) on its `plan-<slug>` branch, in the Planning's own checkout, or for an eligible draft at a direct acceptance (below); never for a `rejected` one (its Planning has ended). Before requesting it, the Planning executor reviews `dev_effort` in `proposal.md` against the settled design and boundaries and updates it when the expected Development thoroughness changed, and runs `devkit rules check` on `proposal.md` and clears every `RULE-proposal-boundaries` report. The acceptance request shows the proposal's change summary, the decisions made in this Planning, the recommended `dev_effort` for Development, and the effort record: the `activity-effort` of each Planning run (its `worker` envelope, noting any difference from `planning_effort`) and the support-role envelopes present (`challenger`, `scout`, `ux-review`, or none, from `devkit workflow envelope check --unit <dir>`), each `challenger` round with the `reverify` that closes it (`review=` on its line), and each `ux-review` round with its open findings, which the user decides at this gate. When a run's effort required a `challenger` that left no envelope, or a `scout` at `high` that left none, the request names the gap; the user may send the proposal back to `spike`. The gate passes with `devkit spec proposal accept <slug> --by user [--note <text>]`, run after explicit acceptance or owning `plan-accept=auto` delegation (`--by policy`): it writes `status: accepted` and records the gate in one validated step, committed together; never edit the status or the record by hand.
- **Direct acceptance** (Backlog, no Planning): for an eligible draft (the `spec` skill's `references/backlog.md`, Direct acceptance) the user may give `plan-accept` on sight; the Host records it on the base checkout with `accept --direct`, without `reviewing` (the `spec` skill's `references/backlog.md`). It has no Planning run, no `activity-effort` and no `worker` envelope, and the request shows "Planning: skipped (direct acceptance)" where a Planning acceptance shows its effort record. The handoff carries its note (`PROP-<slug>: <note>`); a bound proposal without its recorded acceptance is refused at handoff (`SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED`).
- **Rejection changes the status only.** The executor that received it sets `status: rejected` with the user's reason, unrewritten, in the commit message (and in the final merge commit when commits are squashed), closes the last run's open questions in the same commit (`worker-records.md`), and merges per policy. No worker runs, no ADR is written and nothing is deleted then; the later cleanup is what the `[FIX]` of `SPEC_PROPOSAL_REJECTED_PENDING` (listed by `devkit rules check -p hygiene` until then) says: the rejection ADR, then the deletion; the user may invoke the `feedback-hygiene` playbook for it. A `rejected` proposal is never resumed, accepted or started: never answer its `plan-accept`, start another sweep or set it back to `reviewing`, even when `next` shows unmet `collect-feedback` or `direction-handoff` checks.

## Project policy

Read `devkit spec policy` before Planning: `[workflow.stages]` switches stages, and `[tool.spec] worktree` decides whether a `direct`-mode Planning branch runs in its own worktree (`local-orchestrated` always uses one, `cloud-pr` the runner's checkout). `plan-accept`, `proposal-handoff` and `dev-integration` independently allow `ask` or `auto`; `exception` always needs resolution; explicit user authority, worktree and PR policy, external protections and action permissions still apply.

## Planning feedback

Each Planning run captures observed feedback in its proposal's `feedback/` before its last work commit and, before every return to the user, writes fresh sweep evidence before its single `worker` envelope, as the `spec-feedback` skill's `references/sweep.md` ("Planning run coverage") defines. A rejection reuses the last run's recorded coverage and starts no sweep or worker. A direct acceptance has no run or `worker` record: the Host sweeps its own acceptance session at `collect-feedback` before the command. Before deleting a rejected, decomposed or session-reclassified draft's feedback, the Host follows the `spec` skill's `references/feedback-retirement.md`.
