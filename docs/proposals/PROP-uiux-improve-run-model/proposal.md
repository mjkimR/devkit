---
id: PROP-uiux-improve-run-model
title: app-uiux-improve runs outside the repository workflow on per-task approval
summary: Makes app-uiux-improve announce up front that it proceeds outside the repository's development workflow, whatever that workflow is, and continue only on the user's explicit per-task approval or follow the workflow when the user prefers.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
    - packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/
  excludes:
    - docs/capabilities/harness/
    - packages/devkit-spec/
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit-dist/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-uiux-improve-pilot-fit
workflow: sdd-proposal
---

# [PROP-uiux-improve-run-model] app-uiux-improve runs outside the repository workflow on per-task approval

## 1. Background & Hypothesis

`CAP-DLV-uiux-improvement` rule 3 (consumer authority) requires the coordinator to carry every requested change
through the consumer's existing workflow, permissions and approvals (`ADR-uiux-improvement-workflow-boundary`
clause 2, kept by `ADR-impeccable-session-authority`). The bundle installs without `devkit-spec` (rule 13), so "the
consumer's workflow" can be SDD, adaptive development, a team PR and CI process, or nothing formal.

The bundle owner's observation: running a UI/UX improvement through the repository's development workflow did not
fit, and a whole-surface overhaul is hard to carry through it. This proposal is a workflow-neutral bundle policy: it
does not add a route to any particular workflow, and it depends on no `devkit-spec` concept. Split from
~~`PROP-uiux-improve-pilot-fit`~~ (drafted in `6902170e9`, deleted in this split) with
`PROP-uiux-improve-bundle-hygiene` and `PROP-uiux-improve-impeccable-routing`. The user set the delivery order: this
proposal first, then `PROP-uiux-improve-impeccable-routing` (`depends_on` this one), then
`PROP-uiux-improve-bundle-hygiene` (`depends_on` the routing proposal).

Proposed default (the bundle owner's): before starting, the skill tells the user that this procedure proceeds without
following the repository's development workflow and guidelines, and proceeds only after the user approves (or hears
the user's preference). The user may instead choose to follow the repository workflow, and the skill then keeps
rule 3 as it is today.

### Evidence

Two runs in one SDD consumer; `MAT-uiux-improve-pilot` holds the first and `MAT-uiux-improve-second-pilot` (held in
this bundle) the second, the commit attribution and the measurement plan.

- First run, through the workflow (`spec` depth): 18 branch commits, of which 4 touched product code, tests or the UI
  README. By cause (challenger attribution, kept as found): 8 commits record only an envelope (tooling
  granularity, recorded as separate tooling feedback); 2 of those are optional UX-review rounds and 2 are
  finding-driven re-checks; contract amendments during the build came partly from scope creep that the contract
  correctly surfaced; an invented non-goal was a coordinator error (fixed by `PROP-uiux-improve-bundle-hygiene`).
  The residue that SDD structure alone explains is the spec, plan and task authoring, three lifecycle commits,
  `reconcile.md` and the mandatory check envelopes. The workflow also caught real defects: a semantic defect (UX
  review), a test gap (code review) and stale UX documents (reconcile).
- Second run, outside the workflow on the user's explicit per-task instruction: about three product commits and one
  merge, one question round; no independent code or UX review and no documentation reconcile; the edit-list rule
  caught an unwanted dependency bump. Confounds: a narrower task, a coordinator that had learned from the first run,
  and no independent check to show what it missed.

The evidence supports "much less bookkeeping"; it does not yet show "no loss of caught defects". The measurement plan
in `MAT-uiux-improve-second-pilot` tracks that.

### Governance objection and how this proposal answers it

A challenger review objected that a catalog skill defaulting outside a configured approach contradicts rule 3,
`ADR-uiux-improvement-workflow-boundary` clause 2, `CAP-HARN-agent-guidance` ("installing or selecting spec assets
never switches the approach"), `CAP-DLV-adaptive-development` rule 4 and the spec constitution. This proposal keeps
those boundaries:

- The skill never leaves the workflow on its own. It only announces and asks; the departure rests on the user's
  explicit per-task approval. The spec constitution already honors that ("Explicit user instructions take
  precedence"), and the second run used exactly that route.
- Selecting or installing the bundle changes nothing. `CAP-HARN-agent-guidance` and the capability's closing line
  ("Selection changes neither the development approach nor the consumer's execution authority") stay intact; only the
  user's per-task approval does, and only for that task.
- The wording is workflow-neutral: it names no `devkit-spec` policy key or stage, so it reads the same for a team
  process with no devkit workflow.

Hypothesis: announcing and asking per task gives the user the light route when it fits, keeps every departure
attributable to a user decision, and loses no defect-catching value if the loop keeps the independent checks the user
wants.

## 2. Technical Spike Questions

- **Q1 (main)**: Announcement and default. Settle the announcement's content and when it is shown (at entry, before
  any product edit). Must it state explicitly that it proceeds outside an established methodology even when one is
  configured? The bundle owner leans yes: tell the user and get approval. Settle the alternative of asking for the
  user's preference with no default, and what happens without an approval channel (non-interactive host).
- **Q2**: Git and delivery authority. When the repository workflow no longer supplies commit, integration and
  publication authority, the skill asks the user. Settle the granularity without being stricter than needed: one
  question covering the run's Git effects at the start or at the end (as the second run did), rather than one per
  effect.
- **Q3**: Documentation impact. Rule 17 stays report-only: the run reports each consumer OOUX or UX document the
  change made stale and never edits it. Settle whether the report names a concrete follow-up hand-off to the
  repository's own process and how it is worded neutrally.
- **Q4**: Scope growth. If the scope grows mid-run (new surfaces, behavior beyond the approved goal), the coordinator
  asks again before continuing. Settle the trigger.
- **Q5**: Checks in the loop. Which independent checks the loop keeps or offers (independent UX review, independent
  code review, project checks, before/after verification), given that the first run's defects came from them.
- **Q6**: Decision record. A new ADR superseding `ADR-uiux-improvement-workflow-boundary` clause 2 and the
  consumer-authority clauses of `ADR-impeccable-session-authority`; rule 3 rewritten for both modes.

## 3. Proposed Design & Impact

Directions, not final wording; Planning settles each.

1. At entry, one announcement: this procedure proceeds outside the repository's development workflow and
   guidelines; continue, or follow the repository workflow instead? Proceed only on the user's explicit approval
   for this task.
2. Outside the workflow: run the skill's own loop (inspect, independent role passes, user picks, implement inline or
   through Impeccable, project checks, before/after verification), offer the independent checks Planning keeps, ask
   for Git authority as Q2 settles, re-ask on scope growth and end with the stale-document report.
3. Following the workflow: rule 3 as today.
4. A superseding ADR and rule 3 rewritten; `UC-improve-an-interface-and-user-flow` gains acceptance examples for both
   modes; a test asserts the announcement and approval step and that the wording names no workflow-specific policy
   key.

Impact: `CAP-DLV-uiux-improvement` (rules 3, 17, possibly 12), `UC-improve-an-interface-and-user-flow`, one ADR, the
bundle's `SKILL.md`, `references/orchestration.md` and README, and the bundle tests. No change to `devkit-spec`,
delivery workflows, `CAP-HARN-agent-guidance` or distribution.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to `sdd-spec-feature` on
  `dev-uiux-improve-run-model`. The proposal is deleted there, its decision becomes the superseding ADR, and
  `MAT-uiux-improve-second-pilot` moves to `docs/materials/`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
