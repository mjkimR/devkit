---
id: PROP-git-operator-planning-completion-route
title: Planning completion and acceptance execution route for git-operator
summary: "Define how a Planning run records its return when workflow next shows no current stage, and document the Host-record then operator-integration acceptance route, adding a composed acceptance job only if it measurably lowers Host burden."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: low
milestone: MS-git-operator-lifecycle-refinement
depends_on: [PROP-integration-merge-moved-target]
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-git-operator-planning-completion-route] Planning completion and acceptance execution route for git-operator

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), the Host accepted and integrated a
verified Planning result with `accept --mode accept_only` itself, because the git-operator operating reference lists
handoff and integration but no Planning-acceptance job. A later split route succeeded: the Host recorded and committed
the acceptance, then the operator integrated it. A new job is therefore an option to compare against clearer
guidance for that route, not a prerequisite.

A readiness ambiguity appeared as well. `workflow next` returned no current stage and `complete=yes` under
`plan-accept=auto` while proposals were still `reviewing` and no acceptance command had run. Planning workers needed
Host guidance to record their return at `direction-handoff` instead of the printed `-` sentinel.

This repository's own run on 2026-10-30 also found that `accept --mode` refuses `--check`, so a composed acceptance
cannot be dry-run.

The hypothesis: explicit route guidance and an explicit return stage remove the Host's interpretation at the end of
Planning without widening the operator's role.

## 2. Technical Spike Questions

- **Q1 Acceptance route**: Is explicit guidance for Host acceptance record/commit followed by operator integration
  enough, or does a composed acceptance job reduce measured burden? Either route keeps exact refs, current authority
  and all readiness and permission checks, with no new approval grant or arbitrary Git execution.
- **Q2 Return stage**: Should `workflow next` expose a record/return stage when policy-derived readiness has no current
  stage, or is an explicit worker-guidance mapping enough? `complete=yes` is rendered by
  `packages/devkit/src/devkit_agt/features/workflow/cli/render.py`, outside this boundary: choosing the engine route
  records a boundary extension in Planning. No acceptance is inferred from policy readiness.
- **Q3 Dry run**: Should a composed acceptance offer a read-only check, given that `--mode` refuses `--check`?

### Spike findings

Evidence: `MAT-planning-acceptance-route-comparison` (route comparison and code trace), `MAT-git-operator-consumer-pilot`
(in `PROP-git-operator-result-readiness`), and the scout and challenger envelopes of this Planning.

- **Q1**: The composed `devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff` already records and
  commits the acceptance on `plan-<slug>`, merges it through the guarded integration service, cleans up, and with
  `accept_and_handoff` hands off. A rerun after a partial result whose acceptance commit landed continues from that
  commit. The split route (Host `accept` in the Planning worktree, commit, then operator `prepare-integration` and
  `execute-integration`) costs about four Host actions where the composed command costs one, and adds no capability
  the composed command lacks. The gap is only that the git-operator operating table lists `handoff` (itself one
  composed command) but no acceptance.
- **Q2**: Under `plan-accept=auto` the `direction-handoff` gate passes by policy and its exit
  (`status reviewing|accepted`) holds for a `reviewing` proposal; `handoff` has no exit, so `next` prints
  `[STAGE: - complete=yes]` before any acceptance (under `ask` the gate record arrives with `status: accepted`, so a
  `reviewing` proposal never reaches this state). The composed acceptance treats that state as ready, which is
  correct. `worker-records.md` §1 ("`--stage` is the stage `devkit workflow next` names") has no answer for it: the
  envelope contract refuses `-`, and any other text is accepted at write time, where an unknown stage holds every gate.
  A question recorded at `direction-handoff` holds `plan-accept` for both the composed and the basic acceptance; one
  recorded at `handoff` would leave the basic acceptance under `ask` unblocked (inferred from code). The stage to
  name is therefore `direction-handoff`, not the last stage.
- **Q3**: Every readiness refusal of the composed command, including today's `WORKTREE_MERGE_NOT_FF`, is raised in the
  preparation before the acceptance write (`plan_finish` and `_Acceptance.preview` run inside
  `IntegrationService._prepare`), so a refused run leaves nothing written. A refusal after the acceptance commit
  needs the base to move between that preparation and the re-preparation after the commit; a dry run could not
  detect that race either. A rerun then either continues from the landed acceptance commit or, when the base
  diverged, refuses in the preparation until the base is brought into `plan-<slug>`. A separate dry run would
  repeat the preparation for no additional protection. No test covers the `--mode` with `--check` usage error.

## 3. Proposed Design & Impact

Recommended design, pending the user's answers to this Planning's questions:

- **Acceptance route (Q1)**: the git-operator operating table gains one operation, `accept-proposal`, that runs only the
  existing composed command from the retained base:
  `uv run devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff [--effort <level>]`.
  The job carries the Host's current `plan-accept` authority (`by`), the `mode` and, for `accept_and_handoff`, the
  current `proposal-handoff` authority and effort. The operator returns completed and remaining effects; after
  `needs_recovery` it inspects state and reruns the same command only within current authority. The Host keeps
  presenting the proposal and obtaining the user's acceptance under `ask`; in `direct` mode the Host runs the same
  command itself. The split route is not documented as a route. `git-operator.md`, `git-operator-dispatch.md`,
  `git-operator-operations.md`, `spec-orchestrate` (step 4) and `spec-review-proposal` (step 4) name this route.
- **Return stage (Q2)**: guidance only, no engine change. `worker-records.md` §1 and `planning.md` step 6 state that a
  Planning run whose `next` prints `[STAGE: - complete=yes]` while `proposal.md` is still `reviewing` records its
  `worker` envelope at `direction-handoff`, the stage whose gate the acceptance passes, never at `handoff`; open
  questions recorded there hold `plan-accept`. The run records no acceptance or handoff effect. A test of the
  bundle's guidance text pins the mapping.
- **Dry run (Q3)**: no `--check` for the composed form. The usage error and the operating reference state that the
  composed command refuses before its first write, and name `devkit spec proposal report <slug>` and
  `devkit workflow envelope check --unit <dir>` for the read-only material the Host presents under `ask`. One CLI test
  pins the usage error.

### Assumption on PROP-integration-merge-moved-target

This design assumes that proposal's settled direction lands first: the composed acceptance merges a conflict-free moved
target itself and refuses only on a real conflict or failing readiness, and that refusal stays in the preparation
(`plan_finish`), before the acceptance write. If a conflict were instead detected after the acceptance commit, the
operator returns `needs_input` with the accepted but unmerged `plan-<slug>`, and the Host resolves the conflict on that
branch before the same command is rerun; the route itself is unchanged. This route documents no base-merge step.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-01 | A verified committed Planning source and exact current Host authority | The operator executes Planning acceptance | Only named existing CLI effects run; source drift or missing authority preserves resources and returns the required Host action. |
| GOP-03 | Auto-policy Planning readiness with no current stage and a reviewing proposal | A worker authors its final return | The record uses an explicit valid workflow stage; no acceptance or handoff effect is invented. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |

### Non-goals

- **Scope Excluded**: a daemon, persistent approval store, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: unmeasured token, cost or latency savings.
- **Scope Excluded**: a change to the workflow engine's evaluation or `next` output (`packages/devkit/`).

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-planning-completion-route`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
