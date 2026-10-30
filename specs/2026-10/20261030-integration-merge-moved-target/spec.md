---
id: SPEC-integration-merge-moved-target
title: Integrate a conflict-free moved target without requiring the source to contain it
summary: "Let local integration and proposal acceptance merge a moved target themselves and refuse only on a real conflict or failing checks, and run the tests once on main after the units of a local-orchestrated run are finished, so lifecycle merging stays light while defects still surface."
status: in-progress
created: 2026-10-30
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: [CAP-WT-task-worktrees, CAP-INT-mcp-services, CAP-DLV-delivery-workflows, CAP-HARN-agent-guidance]
related_usecases: [UC-drive-development-to-integration]
workflow: sdd-spec-feature
---

# [SPEC-integration-merge-moved-target] Integrate a conflict-free moved target without requiring the source to contain it

## 1. Problem Statement & Motivation

Handed off from proposal PROP-integration-merge-moved-target on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-integration-merge-moved-target`
- **Decisions**: `ADR-moved-target-merge`, `ADR-post-batch-test-run`

### 1. Background & Hypothesis

Local integration requires the source branch to contain the target's HEAD before it merges.
`CAP-WT-task-worktrees` states the rule and its `WORKTREE_MERGE_NOT_FF` refusal, whose fix merges the base into the
branch. `plan_finish` in `packages/devkit/src/devkit_agt/features/worktree/usecases/planning.py` implements it, and
`devkit spec proposal accept --mode accept_only|accept_and_handoff` reuses the same plan. The rule came from
`ADR-local-and-pull-request-integration`; its successor `ADR-host-cli-lifecycle-authority` does not restate it.
The `spec-integrate` skill adds the same requirement as step 1: merge the base into the task branch, re-verify, then
prepare.

In this repository's local-orchestrated runs of 2026-10-30:

- `accept --mode accept_only` refused with `WORKTREE_MERGE_NOT_FF` until the Host merged `main` into the plan branch,
  ran `devkit rules fix` and retried.
- Integration of a Development branch required merging two unrelated documentation commits from `main` and rerunning
  checks before `integration prepare`.

The user finds the containment check unnecessary ceremony, because tests already verify the result.
The hypothesis: the CLI can build the merge of a moved target itself and refuse only on a real textual conflict or
failing readiness, while one test run on `main` after a local-orchestrated batch catches semantic conflicts that a
conflict-free merge can still carry.

#### Settled direction (user)

- A conflict-free moved target is merged by the integrating command itself; the source need not contain it first.
  Real conflicts and failing readiness still refuse.
- Readiness on the built merge runs CI rules only, as the delivery provider's disclosure states for the merged result
  ("CI rules only on the merged result; tests and review ran on the source only"). A semantic conflict that surfaces
  later in CI, nightly CI or hygiene is acceptable; a defect that stays hidden is not. The integration result therefore
  always records the disclosure and the target SHA the command merged.
- Once every unit a local-orchestrated run started is finished and no worker turn of the run is still running, the
  Host runs the project's tests once on `main` (one run on the integrated head, not an aggregation of earlier
  results). A failure is reported with its evidence and becomes follow-up work; nothing is reverted automatically.
- The `spec-integrate` step 1 base merge becomes conditional: the Host merges the base into the task branch only to
  resolve a conflict or a failing check the CLI reports.

#### Planning decisions (user)

- The pull-request route stays out of scope: it keeps refusing a moved target with `WORKTREE_MERGE_NOT_FF`
  (`q-pr-route`).
- The batch test run is the repository's affected selector from the batch start, in this repository
  `just test-affected --base <batch start>` once on `main` with its `mode=full` fallback; nightly CI still runs the
  full suite (`q-batch-command`).
- A unit of the run that ends blocked with its problem recorded, waits for a user decision (its last `worker`
  envelope is `needs_input`) or continues in `direct` mode counts as finished for the batch run: the Host tests what
  the run integrated (`q-blocked-unit`, confirmed at `plan-accept`).
- Outside a batch run, a conflict-free CLI-built merge is covered by its source verification plus the CI rules on the
  merged result; the combined head is tested by a later batch run or by nightly CI (confirmed at `plan-accept`).

## 2. User Stories

- **US-1**: As a Host agent integrating a verified Development branch, I want `devkit integration prepare` and
  `integrate --route local` to merge a target that moved since the branch was cut, so that I merge the base into the
  task branch only when the CLI reports a conflict or a failing check. This changes
  `UC-drive-development-to-integration`.
- **US-2**: As a Host agent accepting a reviewed proposal, I want `devkit spec proposal accept --mode
  accept_only|accept_and_handoff` to accept and integrate a Planning branch whose base moved, refusing before the
  acceptance commit when the merged result fails its checks.
- **US-3**: As the user, I want every integration result to state the target it merged and what was checked on the
  merged result, and one test run on `main` after a local-orchestrated batch, so that a semantic conflict surfaces
  before nightly CI.

## 3. Non-Goals

1. **Scope Excluded**: rebase, force operations or automatic conflict resolution.
2. **Scope Excluded**: dropping readiness checks, or bypassing a host refusal at runtime. Changing the containment
   contract through Planning and an ADR is this change's intent, not a bypass.
3. **Scope Excluded**: automatic revert of a merge whose post-batch test run fails.
4. **Scope Excluded**: merging a moved target in `devkit worktree finish --merge` (no readiness provider), under
   `merge = "ff-only"`, or on the pull-request route.
5. **Scope Excluded**: a CLI command that runs or records the batch test run.
6. **Scope Excluded**: tolerating, under `ask`, a target that moves between the presented prepare and `integrate`
   without a fresh decision; it needs a new preparation, not a base merge.
7. **Scope Excluded**: running tests on the merged result inside integration; the CI rules stay the only check on it.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A conflict-free moved target integrates without a base merge
- **Given** a task branch `dev-demo` cut from `main`, and a later commit on `main` that touches a file the branch did
  not change, under `[worktree] merge = "no-ff"`
- **When** the Host runs `devkit integration prepare dev-demo ... --route local` and then
  `devkit integration integrate dev-demo ... --expected-digest <digest>` from the base checkout
- **Then** prepare exits `0`, integrate exits `0` with `status=completed`, and the landed `main` HEAD is a merge
  commit whose first parent is the moved target and whose second parent is the approved source tip; the task branch
  received no commit.

### [AC-02] Composed acceptance integrates a moved target
- **Given** a reviewed proposal on `plan-idea` whose base `main` gained an unrelated commit after the branch was cut
- **When** the Host runs `devkit spec proposal accept idea --by user --mode accept_only --format json`
- **Then** it exits `0` with `status: accepted`, and the landed `main` HEAD is a merge commit whose first parent is the
  moved target and whose second parent is the acceptance commit; `plan-idea` received no base merge.

### [AC-03] A conflicting moved target refuses at prepare with nothing changed
- **Given** a task branch and a moved target that both changed the same lines of one file
- **When** the Host runs `devkit integration prepare`
- **Then** it refuses with `WORKTREE_MERGE_CONFLICT` (exit `2`), whose `[FIX]` merges the target into the task branch
  to resolve the conflict and prepares again, and the target ref, the source ref and the task worktree are unchanged.

### [AC-04] A moved target that changed integration policy integrates
- **Given** a moved target whose later commit changed `[workflow.approvals] dev-integration`,
  `[worktree] delete_branch` or `[tool.spec]`, none of which the source changed
- **When** the Host prepares and integrates the source
- **Then** integration completes (`status=completed`) with the request's prospective policy taken from the merged
  result, and the deleted or kept source branch follows the merged result's `delete_branch`.

### [AC-05] Failing checks on the merged result refuse before the confirmation
- **Given** a moved target and a merged result on which a blocking CI rule fails (for example a reference the moved
  target renamed), or whose merged `.devkit/installation.json` leaves a record inconsistent
- **When** the Host runs `devkit integration prepare`
- **Then** it refuses with `INTEGRATION_NOT_READY` whose CI-rule reasons name the conditional base merge and
  `devkit rules fix`, respectively `INTEGRATION_RECEIPT_CONFLICT` whose `[FIX]` names the conditional base merge, and
  nothing changes on the target.

### [AC-06] Composed acceptance refuses failing result checks before the acceptance commit
- **Given** a reviewed proposal whose moved target either makes a blocking CI rule fail on the prospective result or
  changed the proposal directory since the merge base
- **When** the Host runs `devkit spec proposal accept <slug> --by user --mode accept_only`
- **Then** it refuses with `SPEC_PROPOSAL_APPROVAL_NOT_READY` (exit `2`) naming the reason and the conditional base
  merge, the proposal stays `status: reviewing`, and `plan-<slug>` HEAD is unchanged (no acceptance commit).

### [AC-07] The request digest is deterministic for a moved target
- **Given** one source and one moved target
- **When** prepare runs twice, the second time with a different Git committer identity and `TZ`
- **Then** both preparations return the same `request.digest`, so `integrate --expected-digest` accepts the digest the
  first preparation presented.

### [AC-08] The routes that cannot absorb a moved target keep their refusal
- **Given** a moved target
- **When** the source policy sets `merge = "ff-only"`, or the Host runs `devkit worktree finish dev-demo --merge`, or
  prepares on `--route pull-request`
- **Then** each refuses with `WORKTREE_MERGE_NOT_FF` as before, and nothing changes.

### [AC-09] Results state the readiness disclosure and the merged target
- **Given** a prepared or executed local integration, or a completed composed acceptance
- **When** its text or JSON result is printed
- **Then** `[INTEGRATION_PREPARED: ...]` carries `target_sha=<confirmation target>` and `[INTEGRATION_SCOPE: ...]` the
  disclosure; `[INTEGRATION: ...]` carries `target_sha=`, `build_target=`, `result=` and `disclosure=` (`-` for a
  build that did not happen: a cleanup-only request names only the prepared target); the JSON keeps
  `request.target.sha`, `request.readiness.disclosure` and `build`; and a composed acceptance result carries
  `target_sha`, `landed_sha` and the delivery provider's `disclosure` in JSON and on its `[ACCEPTED: ...]` line.

### [AC-10] A moved target still needs a committer identity and Git 2.38
- **Given** a moved target
- **When** prepare runs without a committer identity, or with a Git older than 2.38
- **Then** it refuses with `WORKTREE_COMMIT_FAILED`, respectively `WORKTREE_GIT_UNSUPPORTED`, before any request
  exists.

### [AC-11] Guidance makes the base merge conditional and adds the batch test run
- **Given** the shipped spec bundle
- **When** its skills are rendered
- **Then** `spec-integrate` step 1 merges the base only to resolve a conflict or failing check the CLI reports,
  `spec-review-proposal` no longer merges the base routinely before acceptance, and `spec-orchestrate` Completion
  names the batch test run from the batch start and counts a unit as finished when it is integrated, blocked with its
  problem recorded, waiting for a user decision or continued in `direct` (bundle asset tests).

## 5. Assumptions

- **Prospective build only for a moved target**: prepare builds the prospective merge only when the source neither
  contains nor is contained by the target. A source that contains the target keeps today's approved context without a
  result commit, so its digest and readiness do not change.
- **Deterministic prospective commit**: the prospective commit is written with `git hash-object -t commit -w --stdin`
  from the merged tree, both parents, the devkit merge message and the committer line of the parent with the later
  committer date (the first parent on a tie) as both author and committer. `devkit_core.core.git.run_git` takes no
  environment and `packages/devkit-core/` is outside this change, so `git commit-tree` with an overridden identity is
  not used. The object carries no `encoding` header or signature, so it is UTF-8 and unsigned.
- **Preview checks**: the composed acceptance preview runs the delivery provider's result-dependent checks only when
  its context carries a prospective result; a source that contains the target keeps today's preview.
- **Text fields**: the integrate line names absent values as `-`, as the existing `failed=` and `codes=` fields do.
- **Bundle-source integration**: the bundle-source rule in `CAP-HARN-agent-guidance` changes to incorporate the base
  and run `devkit sync` on the branch only after `WORKTREE_MERGE_CONFLICT`, `INTEGRATION_RECEIPT_CONFLICT` or
  `INTEGRATION_NOT_READY`; the post-landing `devkit sync` stays.

## 6. Source feedback

None. `FB-local-render-fix-ignores-worker-write-scope` and `FB-partial-supersession-hides-in-force-clauses` were
recorded during Planning about neighbouring tools and stay open for their own owners.

## 7. Planning answers carried from the proposal

Evidence in historical Git
`6ea3d048d8ca95fea51c6b1e9e98e2e1f613f06b:docs/proposals/PROP-integration-merge-moved-target/envelopes/scout-01.yaml`,
`6ea3d048d8ca95fea51c6b1e9e98e2e1f613f06b:docs/proposals/PROP-integration-merge-moved-target/envelopes/scout-02.yaml`
and `docs/materials/2026-10/20261030-integration-merge-moved-target/options.md`.

- **Merge construction**: `build_result(advance=True)` already builds a merge onto an advanced target in the object
  store; only `plan_finish` refuses a target that moved before preparation. Preparation builds the prospective merge
  (`ADR-moved-target-merge`, option B).
- **Drift on the result**: the reference rules `devkit rules fix` repairs (`RULE-document-reference`,
  `RULE-markdown-link`) run as blocking LINTER-phase CI rules in readiness on the files the merged result changed, so
  drift refuses with `INTEGRATION_NOT_READY`; `receipts.check_merge` refuses an inconsistent merged receipt
  (`INTEGRATION_RECEIPT_CONFLICT`). Their fix is the conditional base merge.
- **Batch test run**: a `spec-orchestrate` Completion step, no CLI helper (`ADR-post-batch-test-run`).
- **Tests**: `test_base_advance.py` `test_diverged_branch_is_refused_with_a_sha_preserving_fix` flips; the `ff-only`,
  `finish --merge`, conflict and later-advance tests stay.

## 8. Lifecycle

- Integration order: every child of `MS-git-operator-lifecycle-refinement` edits `spec-orchestrate/`, so Development
  integrates them one at a time in dependency order; this spec integrates before
  `PROP-git-operator-planning-completion-route`.
- Baseline: at the accepted head `cf991c47`, `test_diverged_branch_is_refused_with_a_sha_preserving_fix` passes
  (prepare of a moved target refuses with `WORKTREE_MERGE_NOT_FF`); the change flips it.
