---
id: SPEC-git-operator-result-readiness
title: Separate effect, readiness, permission and next actor in git-operator results
summary: Make the composed handoff commit its own transaction and make git-operator results report worker-input readiness with exact dirty paths apart from the original CLI result and host-permission blockers, so an uncommitted transaction is never read as clean worker input.
status: in-progress
created: 2026-10-30
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities:
  - CAP-DLV-proposal-planning
  - CAP-DLV-delivery-workflows
related_usecases:
  - UC-plan-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-git-operator-result-readiness] Separate effect, readiness, permission and next actor in git-operator results

## 1. Problem Statement & Motivation

Handed off from proposal PROP-git-operator-result-readiness on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-git-operator-result-readiness`
- **Decision**: `ADR-composed-handoff-commits-its-own-transaction`

The resource-indexer consumer pilot reused one named `git-operator` for six worktree preparations and one
Development handoff (`MAT-git-operator-consumer-pilot`). All seven guarded operations returned exit 0 and the Host
checked their effects. The pilot has not established a net token, cost or latency benefit.

A successful handoff left a known generated transaction uncommitted. CLI effect completion did not by itself mean
clean committed worker input, and the return named no uniform owner of the next action. This repository repeated it
on 2026-10-30: four composed handoffs (through `accept --mode accept_and_handoff` and the operator's `handoff`) left
the transaction uncommitted, and the Host committed each with one commit of every changed path
(`MAT-git-operator-handoff-commit-evidence`). One of them also carried a rewrite of a sibling draft that was in its own
Planning, which later conflicted (`FB-handoff-rewrite-edits-sibling-draft`).

The first actual integration request in the pilot was denied by automatic approval review before CLI execution. The
Host preserved resources and obtained explicit authorization for the named merge and cleanup effects; the same
guarded route, freshly prepared, then completed five Planning merges and their cleanup. This is observed
host-permission recovery, not evidence that policy-derived readiness grants host permission.

The hypothesis: when the composed handoff commits its own transaction and the operator result reports worker-input
readiness from Git observation, the Host continues without re-deriving it and without committing the handoff
transaction itself.

## 2. User Stories

- **US-1**: As a Host starting Development through the composed handoff, I want the handoff to commit its own
  transaction as one direct child of the reviewed base, so that a worker starts from clean committed input without a
  Host commit step.
- **US-2**: As a Host whose handoff commit was refused, I want a stopped result with the commit output, the exact
  dirty paths and a next action, so that I repair and commit in the Development worktree instead of rerunning.
- **US-3**: As a Host reading a `git-operator` result, I want worker-input readiness (`head`, `dirty_paths`) reported
  from Git observation apart from the CLI result and the role status, so that an exit code is never read as ready
  input.
- **US-4**: As a Host whose Development branch conflicts with a sibling proposal's merged Planning, I want the
  guidance to name the resolution, so that the conflict the reference rewrite causes is resolved the same way each
  time.

## 3. Non-Goals

1. **Scope Excluded**: a commit in the plain `devkit spec proposal handoff <slug>`, a configurable commit subject, a
   rollback of a refused handoff, or skipping Planning-owned siblings in the reference rewrite.
2. **Scope Excluded**: a new top-level field in the `git-operator` result (`next_actor`, a readiness or permission
   field); readiness lives under `checks`, and the Host is always the next actor.
3. **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
   remote deletion; changing policy or bypassing a host refusal to make a lifecycle operation succeed.
4. **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token, cost or latency
   savings.
5. **Scope Excluded**: a change to worktree start or setup (`CAP-WT-task-worktrees` stays as it is).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The composed handoff commits its transaction once
- **Given** an accepted proposal on a clean retained base and a post-commit hook that rewrites the commit metadata
- **When** the Host runs `devkit spec proposal handoff <slug> --effort low`
- **Then** the command exits `0`, `dev-<slug>` holds exactly one new commit with subject
  `spec: hand off <slug> to Development` whose single parent is the reviewed base head, `git status --porcelain` in
  the worktree is empty, the JSON `commit` equals `git rev-parse HEAD` read after the hooks, and the text output is
  `[HANDOFF: PROP-<slug> status=handed_off ... commit=<that sha>]` followed by `[NEXT_CMD: ...]`

### [AC-02] A refused handoff commit stops with the dirty paths
- **Given** an accepted proposal on a clean retained base and a pre-commit hook in the repository that exits `1`
- **When** the Host runs `devkit spec proposal handoff <slug> --effort low`
- **Then** the command exits `1`, stdout starts with `[HANDOFF_STOPPED: PROP-<slug> status=needs_recovery` and holds
  `commit=-` and `[NEXT_ACTION: ...]` but no `[NEXT_CMD: ...]`, stderr carries `SPEC_HANDOFF_COMMIT_REFUSED`
  (`INPUT_ERROR`) with the hook output as `[DETAIL]` and every dirty path as `[TARGET]`, the worktree HEAD is still the
  reviewed base head, and the spec bundle is present uncommitted

### [AC-03] The composed acceptance carries the handoff commit
- **Given** a reviewed proposal on `plan-<slug>` under `proposal-handoff=ask`
- **When** the Host runs `devkit spec proposal accept <slug> --by user --mode accept_and_handoff --effort low`
- **Then** on success the result carries `commit` equal to the `dev-<slug>` HEAD and `completed_steps` includes
  `handoff` and `handoff_commit`; when the handoff commit is refused the command exits `1` with
  `[ACCEPTED_STOPPED: ...]`, `completed_steps` includes `handoff` but not `handoff_commit`, `commit` is null and the
  next action is the refusal's, not a next command

### [AC-04] The plain handoff stays write-only
- **Given** an accepted proposal in a `dev-<slug>` checkout
- **When** the Host runs `devkit spec proposal handoff <slug>` without `--effort`
- **Then** HEAD does not move and the handoff's writes stay uncommitted

### [AC-05] git-operator reports worker-input readiness from Git observation
- **Given** the `git-operator` contract and its dispatch and operations references
- **When** a `handoff` or `prepare-worktree` result is returned
- **Then** `checks.worker_input` carries `head` and `dirty_paths` from `git -C <worktree> rev-parse HEAD` and
  `status --porcelain`, every dirty path is also a `remaining_effects` entry so the result is `needs_input` and never
  `completed`, a CLI exit `0` with dirty paths is reported neither as a failed CLI operation nor as ready input, and
  the Host compares `checks.worker_input` with its own Git observation before starting a worker

### [AC-06] The operator returns production edits and broader authority to the Host
- **Given** a job that needs production edits, semantic conflict resolution or authority beyond the job
- **When** the operator receives it
- **Then** the contract's authority section has it return that work to the Host and perform no such mutation

### [AC-07] Evidence kinds stay separate
- **Given** results mixing live effects, a host refusal before dispatch and untested cases
- **When** the operator or Host reports them
- **Then** the contract keeps the original CLI result (null on a denial before dispatch), role status, Git
  observation and remaining work apart, never reports CLI readiness or `auto` policy as host permission, and reports
  no unmeasured cost or latency as an improvement

### [AC-08] Post-handoff link fixes and the sibling conflict are named
- **Given** a handoff whose result carries `[UNRESOLVED_LINK]` or `[REWRITTEN ...]` lines outside the new spec and
  promoted ADRs, and a sibling draft in its own Planning whose `depends_on` the handoff rewrote
- **When** the Host reads `post-handoff.md`, the `spec` skill's worktree reference and `CAP-DLV-proposal-planning`
- **Then** after the composed handoff the link fixes are a later Host commit on `dev-<slug>` before a worker starts,
  the sibling's `depends_on` is still rewritten by the handoff, and the guidance names the resolution of a later
  base-merge conflict under `docs/proposals/PROP-<other>/`: take the base version, then run `devkit rules fix` on it

## 5. Assumptions

- A commit that landed but is not one clean direct child of the reviewed base (a hook added a commit or left files)
  is reported as `status: needs_recovery` with `SPEC_HANDOFF_STALE`, the landed `commit` and the dirty paths; the
  ADR defines only the refused case, and the existing stale code already means "the new worktree changed after the
  check".
- A refused commit leaves the handoff's writes staged in the worktree: the Host's later `git commit` there needs no
  second `git add`, and nothing is rolled back.
- `SPEC_HANDOFF_COMMIT_REFUSED` takes the `INPUT_ERROR` directive like `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED`: a rerun of
  the same command refuses the dirty worktree, so the Host fixes the reported cause instead.
- The composed acceptance adds `handoff_commit` to `completed_steps` when the commit landed and prints `commit=` on
  `[ACCEPTED: ...]` only for `accept_and_handoff`, so the Host reads the same effect from either composed command.

## 6. Source feedback

- `FB-handoff-rewrite-edits-sibling-draft`: addressed directly (AC-08). The handoff keeps rewriting a sibling
  draft's references (its `depends_on` rewrite keeps later handoffs valid); the guidance names the resolution of the
  later base-merge conflict instead. It stays open until completion verifies the fix.

## 7. Carried Proposal Notes

### Planning answers

- **Result shape**: no new top-level field. For `prepare-worktree` and `handoff` the operator reports
  `checks.worker_input` with the observed `head` and exact `dirty_paths`. A dirty path is also a `remaining_effects`
  entry, so the result is `needs_input`, never `completed`. The next action is the Host's: the operator always
  returns to the Host, which owns scheduling, and `remaining_effects` names the work. Host permission needs no field:
  a denial before dispatch stays a blocker code with a null `cli_result`, and CLI readiness or `auto` policy is never
  reported as host permission.
- **Handoff interface**: the composed handoff gains a commit step
  (`ADR-composed-handoff-commits-its-own-transaction`); its contract lives in `CAP-DLV-proposal-planning`. Worktree
  start and setup do not change. The plain `handoff <slug>` stays write-only.

### Planning decisions

- The user chose the composed handoff commit over a Host commit step or a commit in every handoff, readiness under
  `checks.worker_input` with no new top-level field and no `next_actor`, and an unchanged reference rewrite with
  guidance only over a sibling skip.
- The Host assigned the shared GOP-06 operator-scope wording to this unit: an operator returns production edits,
  semantic conflict resolution and broader authority to the Host. `git-operator.md` keeps that wording in its
  authority section; `PROP-git-operator-planning-completion-route` and `PROP-git-operator-batch-preparation` keep
  GOP-06 only as a regression check and do not reword it.
- `PROP-git-operator-batch-preparation` reports each item with this result shape (`checks.worker_input`, dirty paths
  in `remaining_effects`) and adds no field of its own.
- Development of this unit and its sibling git-operator units integrates one at a time in dependency order, so each
  later sibling rebuilds on the integrated `git-operator.md`, `spec-orchestrate` and delivery capability text.

### Acceptance check map

| Proposal check | Acceptance criterion |
| --- | --- |
| GOP-02 | AC-01 |
| GOP-02b | AC-02, AC-03 |
| GOP-02c | AC-05 |
| GOP-06 | AC-06 |
| GOP-07 | AC-07 |
| GOP-09 | AC-08 |
