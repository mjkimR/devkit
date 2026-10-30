---
id: PROP-git-operator-planning-completion-route
title: Planning completion and acceptance execution route for git-operator
summary: "Name the stage a Planning run records its final return at when workflow next shows no current stage, and make the Host-run composed accept --mode the single documented Planning acceptance route, with no git-operator acceptance job."
status: accepted
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
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
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
(in `SPEC-git-operator-result-readiness`), and the scout and challenger envelopes of this Planning.

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
- **Q3**: Every readiness refusal the preparation raises, including today's `WORKTREE_MERGE_NOT_FF`, comes before the
  acceptance write (`plan_finish` and `_Acceptance.preview` run inside `IntegrationService._prepare`), so such a refusal
  leaves nothing written. Checks on the built merge (finish guards, CI rules on the landing tree, receipts) run in
  `_land`, after the acceptance commit; today the landing tree equals the source tree, but with a moved target merged
  by the command (`PROP-integration-merge-moved-target`) they can newly refuse there. That proposal's settled Q4 runs
  the CI rules and the unit-advance check on the prospective merge in the preview, before the acceptance commit, so
  what still refuses after the commit is mainly a target that moves between the preview and landing. A dry run repeats only the first
  preparation, so it would not catch those refusals or a base move between the two preparations. A rerun after a
  later refusal continues from the landed acceptance commit, or refuses in preparation once the base diverged. No test
  covers the `--mode` with `--check` usage error.

## 3. Proposed Design & Impact

The single documented Planning acceptance route is the existing composed command, run from the retained base:
`uv run devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff [--effort <level>]`.
The Host runs it. The split route (Host `accept` in the Planning worktree, commit, then operator integration) is not
documented as a route.

- **Acceptance route (Q1): the Host runs the composed command.** `git-operator-operations.md` and
  `git-operator-dispatch.md` (in `spec-orchestrate/references/`) state in one line that Planning acceptance is the
  Host's composed `accept --mode`, which already includes integration and cleanup, so no operator job follows it.
  `spec-orchestrate` step 4 and `spec-review-proposal` step 4 name the same command. git-operator gains no acceptance
  job; its contract (`subagents/git-operator.md`) and `ADR-reusable-lifecycle-resource-manager` are unchanged.
- **Refusal after the acceptance commit.** A refusal raised in preparation leaves nothing written and
  returns the required source preparation. A refusal after the acceptance commit (a conflict, CI rules or receipts on
  the built merge, or a base move between the preparations) returns `needs_recovery` with `completed_steps`; the
  accepted, unmerged `plan-<slug>` goes back to the Host with the reported code, the source is prepared on that branch
  (base merge and `devkit rules fix` when the code calls for it), and only then is the same command rerun. A rerun that
  would repeat a deterministic refusal is not made.
- **Return stage (Q2): guidance only, no engine change.** `worker-records.md` §1 and `planning.md` step 6 state that a
  Planning run whose `next` prints `[STAGE: - complete=yes]` while `proposal.md` is still `reviewing` records its
  `worker` envelope at `direction-handoff`, the stage whose gate the acceptance passes, never at `handoff`; open
  questions recorded there hold `plan-accept`. The run records no acceptance or handoff effect.
- **Dry run (Q3): no `--check` for the composed form.** The usage error that `--mode` raises with `--check`
  (`features/delivery/cli/proposals.py`, today "composed acceptance cannot use --direct or --check") says that
  readiness refusals in preparation precede the first write and a later failure returns `needs_recovery` with
  `completed_steps`, and names `devkit spec proposal report <slug>` and `devkit workflow envelope check --unit <dir>`
  for the read-only material the Host presents under `ask`. The `--direct` refusal keeps its meaning.

### Planning decisions

The user decided q1-q3 of this Planning (`answer-01`), each with the recommended option:

- **q1 (a)**: the Host runs the composed acceptance. The operator `accept-proposal` job (limited to `accept_only`) and
  the documented split route were not taken. No PADR is needed, because the operator's effects stay those
  `ADR-reusable-lifecycle-resource-manager` lists.
- **q2 (a)**: guidance only, pinned by one behavior test (GOP-03). The engine change to `next` in `packages/devkit/` was
  not taken and stays a Non-goal.
- **q3 (a)**: no `--check` for the composed form; the reworded usage error is pinned by one CLI test.

### Prerequisite PROP-integration-merge-moved-target

That proposal settled its questions with its recommendations: composed acceptance merges a conflict-free moved target
itself, and its preview runs the CI rules and the unit-advance check on the prospective merge, so a conflict or
drift on the merged result refuses before the acceptance commit. The route therefore needs no base-merge step before
the command, and the post-commit recovery above covers what remains after the preview, such as a target that moves
between the preview and landing. `depends_on` stays because both proposals change `spec-orchestrate` and the spec
references, and this guidance must not describe the containment step that proposal removes. Development integrates
the sibling proposals of `MS-git-operator-lifecycle-refinement` one at a time in dependency order, so this proposal's
Development starts from a base that already holds that change.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then | Check |
| --- | --- | --- | --- | --- |
| GOP-01 | A verified committed Planning source and exact current Host authority | The Host runs the composed acceptance | Only the composed command's existing effects run; source drift or missing authority preserves resources and returns the required Host action; a post-commit refusal returns the accepted, unmerged branch to the Host. | Existing stale and authority tests of the composed acceptance (`packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`) plus the operating-reference wording check in `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` |
| GOP-03 | Auto-policy Planning readiness with no current stage and a reviewing proposal | A worker authors its final return | The record uses `direction-handoff`; an open question there makes `accept --mode` refuse; no acceptance or handoff effect is invented. | A new behavior test in `packages/devkit-spec/tests/` |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. | Regression check only: the existing operator contract wording, whose shared operator-scope text `SPEC-git-operator-result-readiness` owns; this proposal changes none of it |

Development also adds one CLI test that pins the composed `--mode` with `--check` usage error and its wording.

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
