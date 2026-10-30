---
id: SPEC-git-operator-planning-completion-route
title: Planning completion and acceptance execution route for git-operator
summary: Name the stage a Planning run records its final return at when workflow next shows no current stage, and make the Host-run composed accept --mode the single documented Planning acceptance route, with no git-operator acceptance job.
status: in-progress
created: 2026-10-30
depends_on:
  - SPEC-integration-merge-moved-target
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: [CAP-DLV-proposal-planning, CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-git-operator-planning-completion-route] Planning completion and acceptance execution route for git-operator

## 1. Problem Statement & Motivation

Handed off from proposal PROP-git-operator-planning-completion-route on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-git-operator-planning-completion-route`
  (`MAT-planning-acceptance-route-comparison`)

### Background

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), the Host accepted and integrated a
verified Planning result with `accept --mode accept_only` itself, because the git-operator operating reference lists
handoff and integration but no Planning-acceptance job. A later split route (Host records and commits the
acceptance, then the operator integrates it) also succeeded, at about four Host actions where the composed command
costs one, and adds no capability the composed command lacks (`MAT-planning-acceptance-route-comparison`).

Under `plan-accept = "auto"`, `devkit workflow next` printed `[STAGE: - complete=yes]` while proposals were still
`reviewing` and no acceptance command had run. Planning workers needed Host guidance to record their return at
`direction-handoff` instead of the printed `-` sentinel: `worker-records.md` §1 says `--stage` is the stage `next`
names, the envelope contract refuses `-`, and an unknown stage is accepted at write time and holds every gate.

`accept --mode` refuses `--check`, so a composed acceptance cannot be dry-run, and its usage error does not say what
the Host can read instead.

The hypothesis: explicit route guidance and an explicit return stage remove the Host's interpretation at the end of
Planning without widening the operator's role.

### Settled direction (user, at Planning)

- **q1**: the Host runs the composed `devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff`
  itself; the git-operator references say so in one line; git-operator gains no acceptance job, and its contract
  (`subagents/git-operator.md`) and `ADR-reusable-lifecycle-resource-manager` are unchanged. The split route is not
  documented as a route.
- **q2**: guidance only for the final Planning return stage: `worker-records.md` §1 and `planning.md` step 6 name
  `direction-handoff`, pinned by one behavior test. The engine change to `next` stays a Non-Goal.
- **q3**: no `--check` for the composed form: the usage error is reworded to say why and to point to
  `devkit spec proposal report <slug>` and `devkit workflow envelope check --unit <dir>`, pinned by one CLI test.

### Current base (premise check)

The base this unit starts from already holds the prerequisite `SPEC-integration-merge-moved-target` (the composed
acceptance merges a conflict-free moved target itself and runs the result checks on the prospective merge before
the acceptance commit; a refusal after the acceptance commit returns the accepted, unmerged plan branch) and
`SPEC-git-operator-result-readiness` (the composed handoff commits its own transaction; the operator-scope wording
of GOP-06 lives in `subagents/git-operator.md`). Both premises of the proposal hold; the route is documented against
that behavior, and GOP-06 is a regression check only.

## 2. User Stories

- **US-1**: As a Host agent finishing a Planning unit in `local-orchestrated` mode, I want the git-operator operating
  references and the acceptance skills to name one acceptance route, the composed command I run myself, so that I
  neither dispatch an operator job nor split the acceptance from its integration.
- **US-2**: As a Planning worker whose `devkit workflow next` prints `[STAGE: - complete=yes]` while the proposal is
  still `reviewing`, I want the worker records reference to name the stage I record my `worker` envelope at, so that
  my open questions hold `plan-accept` and I invent no acceptance or handoff effect.
- **US-3**: As a Host agent that asks for a dry run of `accept --mode`, I want the usage error to say why there is
  none and which read-only commands give the material to present, so that I present the proposal under `ask` without
  guessing.

## 3. Non-Goals

1. **Scope Excluded**: a git-operator acceptance job, a change to `subagents/git-operator.md` or to
   `ADR-reusable-lifecycle-resource-manager`.
2. **Scope Excluded**: a change to the workflow engine's evaluation or `next` output (`packages/devkit/`).
3. **Scope Excluded**: a `--check` or other dry run for the composed acceptance, and any change to what the composed
   acceptance does (its effects, readiness, codes and recovery).
4. **Scope Excluded**: a daemon, persistent approval store, global repository lock or autonomous scheduler; operator
   source authoring, semantic decisions, approval grants, force operations or arbitrary remote deletion.
5. **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
6. **Scope Excluded**: unmeasured token, cost or latency savings.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The operating references name the Host-run composed acceptance (GOP-01)
- **Given** the spec bundle sources of `skills/spec-orchestrate/references/git-operator-operations.md` and
  `git-operator-dispatch.md`
- **When** a wording test reads them
- **Then** each states in one line that Planning acceptance is the Host's composed
  `devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff`, which already includes
  integration and cleanup, so no operator job follows it; the operations table keeps exactly its six rows
  (`prepare-worktree`, `handoff`, `prepare-integration`, `execute-integration`, `cleanup`, `inspect-recovery`) and has
  no acceptance row.

### [AC-02] The acceptance skills name the same command and the post-commit recovery
- **Given** the `spec-orchestrate` skill source and the local rendering of the `spec-review-proposal` skill
- **When** a wording test reads step 4 of each
- **Then** both name `devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff` as
  run by the Host; `spec-review-proposal` step 4 states that a refusal in preparation leaves nothing written, that a
  refusal after the acceptance commit (`needs_recovery` with `completed_steps`) returns the accepted, unmerged
  `plan-<slug>` to the Host with the reported code, that the source is prepared on that branch before the same command
  is rerun, and that a rerun which would repeat a deterministic refusal is not made.

### [AC-03] The composed acceptance's effects are unchanged (GOP-01 regression)
- **Given** a verified committed Planning source on `plan-idea`
- **When** the existing composed-acceptance CLI tests run
  (`packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`)
- **Then** each passes unchanged: a policy acceptance is never redirected to the user (`SPEC_PROPOSAL_POLICY_NOT_AUTO`,
  `SPEC_PROPOSAL_WRONG_WORKTREE`), a target change to the proposal refuses before the acceptance commit
  (`SPEC_PROPOSAL_APPROVAL_NOT_READY`, `plan-idea` HEAD unchanged), and a refused acceptance commit withdraws its
  writes (`SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED`, refs unchanged).

### [AC-04] The worker records name `direction-handoff` for the final Planning return (GOP-03 guidance)
- **Given** the spec bundle sources of `skills/spec/references/worker-records.md` and `planning.md`
- **When** a wording test reads `worker-records.md` §1 and `planning.md` step 6
- **Then** both state that a Planning run whose `devkit workflow next` prints `[STAGE: - complete=yes]` while
  `proposal.md` is still `reviewing` records its `worker` envelope at `direction-handoff`, never `handoff` or `-`, and
  `worker-records.md` adds that open questions recorded there hold `plan-accept` and that the run records no
  acceptance or handoff effect.

### [AC-05] An open question recorded at `direction-handoff` holds the composed acceptance (GOP-03 behavior)
- **Given** a reviewed proposal PROP-idea on `plan-idea` with `status: reviewing`, its feedback swept, and
  `[workflow.approvals] plan-accept = "auto"` on the base and the plan branch
- **When** `devkit workflow next --unit docs/proposals/PROP-idea` runs in the Planning worktree, then a `worker`
  envelope with one question is recorded there with `--stage direction-handoff` and committed, and the Host runs
  `devkit spec proposal accept idea --by policy --mode accept_only --format json` from the base checkout
- **Then** `next` first prints `[STAGE: - complete=yes]` and exits `0`; the acceptance exits `2` with
  `SPEC_PROPOSAL_APPROVAL_NOT_READY` and a `[DETAIL]` line starting `hold: `; every ref of the repository is unchanged,
  `proposal.md` on `plan-idea` still says `status: reviewing`, the proposal has no `gate:plan-accept` record and no
  `dev-idea` branch exists.

### [AC-06] The composed form's `--check` usage error points to the read-only material (q3)
- **Given** any repository
- **When** the Host runs `devkit spec proposal accept idea --by user --mode accept_only --check`
- **Then** it exits `2` with a usage error on stderr and nothing on stdout; the error says that the composed
  acceptance has no `--check`, that its readiness refusals in preparation come before the first write and a later
  failure returns `needs_recovery` with `completed_steps`, and names
  `devkit spec proposal report idea` and `devkit workflow envelope check --unit docs/proposals/PROP-idea`; nothing is
  written. With `--direct` instead of `--check` it exits `2` with the usage error
  `composed acceptance cannot use --direct`.

### [AC-07] The operator still returns out-of-scope work to the Host (GOP-06 regression)
- **Given** the git-operator contract `subagents/git-operator.md`
- **When** the existing test `test_operator_returns_production_edits_and_broader_authority_to_the_host` runs
- **Then** it passes, and this unit's diff does not touch `subagents/git-operator.md`.

## 5. Assumptions

- The `--direct` and `--check` refusals of the composed form are split into two usage errors so that the `--direct`
  refusal keeps its meaning and the `--check` one carries the explanation; when both flags are given, `--direct` is
  reported. The error names the commands with the given slug in the project's documented invocation form.
- The Living Spec reflection goes to `CAP-DLV-proposal-planning` (route, `--check` refusal, post-commit recovery) and
  to the `plan-accept` rule of `CAP-DLV-delivery-workflows` (return stage), leaving its git-operator section, which a
  sibling unit edits, unchanged.
- No before/after measurement applies: the change is guidance, one usage error and tests, and the proposal excludes
  unmeasured cost or latency savings.
