---
id: PROP-integration-merge-moved-target
title: Integrate a conflict-free moved target without requiring the source to contain it
summary: "Let local integration and proposal acceptance merge a moved target themselves and refuse only on a real conflict or failing checks, and run the tests once on main after the units of a local-orchestrated run are finished, so lifecycle merging stays light while defects still surface."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/worktree/
priority: high
size: L
planning_effort: high
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/worktree/
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/tests/
    - docs/capabilities/worktree/
    - docs/capabilities/integration/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/delivery/UC-drive-development-to-integration.md
    - docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    - docs/decisions/2026-10/20261022-test-selection-and-ci.md
    - docs/development/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/
    - guides/INSTALL_GUIDE.md
    - AGENTS.md
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-integration-merge-moved-target] Integrate a conflict-free moved target without requiring the source to contain it

## 1. Background & Hypothesis

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

### Settled direction (user)

- A conflict-free moved target is merged by the integrating command itself; the source need not contain it first.
  Real conflicts and failing readiness still refuse.
- Readiness on the built merge runs CI rules only, as today's disclosure states for the merged result
  ("CI rules only on the merged result; tests and review ran on the source only",
  `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py`). A semantic conflict that
  surfaces later in CI, nightly CI or hygiene is acceptable; a defect that stays hidden is not. The integration
  result therefore always records the disclosure and the target SHA the command merged.
- Once every unit a local-orchestrated run started is integrated and no Development work remains (refined by
  `q-blocked-unit` below), the Host runs the project's tests once on `main` (one run on the integrated head, not an aggregation of earlier results). A failure
  is reported with its evidence and becomes follow-up work; nothing is reverted automatically.
- The `spec-integrate` step 1 base merge becomes conditional: the Host merges the base into the task branch only to
  resolve a conflict or a failing check the CLI reports.

### Planning decisions (user)

- The pull-request route stays out of scope: it keeps refusing a moved target with `WORKTREE_MERGE_NOT_FF`
  (`q-pr-route`).
- The batch test run is the repository's affected selector from the batch start, in this repository
  `just test-affected --base <batch start>` once on `main` with its `mode=full` fallback; nightly CI still runs the
  full suite (`q-batch-command`).
- A unit of the run that ends blocked with its problem recorded, or continues in `direct` mode, counts as finished for
  the batch run: the Host tests what the run integrated (`q-blocked-unit`). Planning applies the same rule to a unit
  waiting for a user decision, and the run starts once no worker turn of the run is still running.
- Outside a batch run, a conflict-free CLI-built merge is covered by its source verification plus the CI rules on the
  merged result; the combined head is tested by a later batch run or by nightly CI, which the settled direction
  accepts.

## 2. Technical Spike Questions

Answers from Planning; evidence in `envelopes/scout-01.yaml`, `envelopes/scout-02.yaml` and
`materials/options.md`.

- **Q1 Merge construction**: `build_result(advance=True)` already builds a merge onto an advanced target in the
  object store (`git merge-tree --write-tree`, then `git commit-tree`); only `plan_finish` refuses a target that moved
  before preparation. A real conflict is `WORKTREE_MERGE_CONFLICT` with nothing changed. Preparation builds the
  prospective merge (`PADR-moved-target-merge`, option B).
- **Q2 Policy values**: yes. `ff-only` lands the source tip itself, so it keeps refusing a moved target with
  `WORKTREE_MERGE_NOT_FF`.
- **Q3 Pull-request route**: out of scope (user, `q-pr-route`): the platform builds the merge and runs required checks
  on its merge ref; the route keeps its containment refusal.
- **Q4 Drift on the result**: the reference fixers that `devkit rules fix` applies (`RULE-document-reference`,
  `RULE-markdown-link`) run as blocking LINTER-phase CI rules in readiness on files the source changed, so drift on the
  merged result refuses with `INTEGRATION_NOT_READY`; `receipts.check_merge` refuses an inconsistent merged receipt
  (`INTEGRATION_RECEIPT_CONFLICT`). Under option B both refuse at prepare, and in composed acceptance before the
  acceptance commit (its preview runs the CI rules on the prospective result). Their fix is the conditional base merge.
- **Q5 Batch test run**: a `spec-orchestrate` Completion step, no CLI helper; the repository's integrated-content
  verification once on the base branch head from the batch start (here `just test-affected --base <batch start>` with
  its `mode=full` fallback, user decision `q-batch-command`); a unit that ends blocked, waits for a user decision or
  continues in `direct` counts as finished (`q-blocked-unit`); reported in the conversation, a failure recorded as
  feedback (`PADR-post-batch-test-run`).
- **Q6 Decision record**: `PADR-moved-target-merge` supersedes only the local containment clauses of
  `ADR-local-and-pull-request-integration` (already superseded in part by `ADR-host-cli-lifecycle-authority`; its merge
  and readiness clauses remain in force); `PADR-post-batch-test-run` supersedes only the post-merge clause of
  `ADR-test-selection-and-ci`. Tests: `test_base_advance.py` `test_diverged_branch_is_refused_with_a_sha_preserving_fix`
  flips; the `ff-only`, `finish --merge`, conflict and later-advance tests stay.

## 3. Proposed Design & Impact

### devkit-agt (`worktree`, `integration`)

- `plan_finish` gains an opt-in keyword (`advance`, default off) that only the local integration service (and through
  it composed acceptance) sets: with it, under `no-ff`, a source that does not contain the target plans a merge build
  and still requires a committer identity. Without it (the pull-request route, external library callers) today's
  refusal and error precedence stay; `finish --merge` does not use `plan_finish` and keeps its own refusal.
- Local preparation of a moved target builds a prospective merge with `build_result(advance=True)`: unsigned, no ref,
  UTF-8, author and committer lines copied from the committer of the parent with the later committer date, so the
  commit and the request digest do not depend on Git identity, `TZ` or commit encoding; the merged tree follows the
  repository's Git merge configuration, as the integrate build does. The digest contract is unchanged. A prospective
  context (approved context plus that commit) goes to the finish guards (with `merge-base(target, source)`), the readiness provider, `receipts.check_merge` and the
  prospective policy digest before the request is returned.
- Cleanup scopes are planned from the approved context; the prospective commit never enters
  `IntegrationResult.build_target` or `result_sha`. The `IntegrationContext` docstring states that a provider can
  receive an unlanded prospective result at prepare.
- Integrate rebuilds on the current target as today (signed as configured) and fast-forwards the base onto the result.
  Under `ask`, a target that moved after the presented prepare changes the digest (`INTEGRATION_REQUEST_STALE`); the
  Host presents a fresh prepare for a new decision, with no base merge.
- Prepare and integrate results carry the readiness disclosure and the merged target SHA in text and JSON:
  `[INTEGRATION_PREPARED: ...]`/`[INTEGRATION_SCOPE: ...]` name the confirmation target SHA, `[INTEGRATION: ...]`
  adds the build target and the landed result.
- `WORKTREE_MERGE_NOT_FF` (`ff-only`), `WORKTREE_MERGE_CONFLICT` and `INTEGRATION_RECEIPT_CONFLICT` fixes name the
  conditional base merge. `INTEGRATION_NOT_READY` keeps its core fix; codes and modes stay.
- The pull-request route does not set `advance`, so it refuses a moved target with `WORKTREE_MERGE_NOT_FF` as today,
  merged-PR cleanup included.

### devkit-spec (`delivery`, bundle)

- Composed acceptance (`accept_only`, `accept_and_handoff`) inherits the preparation change. Its preview receives the
  prospective context and runs the provider's result-dependent checks (CI rules and the unit-advance check) on it, so
  a conflict, CI-rule drift or a target change to the proposal directory refuses (`WORKTREE_MERGE_CONFLICT`,
  `SPEC_PROPOSAL_APPROVAL_NOT_READY`) before the acceptance commit.
- The devkit-spec CI-rule reasons on a prospective or built result (`result_sha` set), and the preview's refusal, name
  the conditional base merge and `devkit rules fix`. Its result adds the
  delivery provider's disclosure and the merged target SHA.
- The devkit-spec provider docstring and `CAP-DLV-delivery-workflows` readiness section state that prepare may check a
  prospective result.
- `_unit_advance` keeps refusing a target that changed the unit directory; its fix names the conditional base merge.
- `spec-integrate` step 1 merges the base only to resolve a conflict or failing check the CLI reports; steps 2-4
  re-verify only what such a merge changed. `spec-review-proposal` drops the routine base merge and `rules fix` before
  acceptance. Bundle-source integration (`CAP-HARN-agent-guidance`, "For changed bundle sources") incorporates the
  base and runs `devkit sync` on the branch only after `WORKTREE_MERGE_CONFLICT`, `INTEGRATION_RECEIPT_CONFLICT` or
  `INTEGRATION_NOT_READY`; the receipt check and CI rules on the result guard the rest, and the post-landing
  `devkit sync` stays. `spec-orchestrate` step 5 drops "the implementer first incorporates a moved base"; its
  Completion adds the batch test run once the run's units are integrated, blocked, awaiting a user decision or
  continued in `direct`; `git-operator-operations.md` makes base incorporation conditional.
  `spec/references/completion.md` follows.

### Living Spec and repository policy

- `CAP-WT-task-worktrees`, `CAP-INT-mcp-services` (including its changed-target statement and the
  `INTEGRATION_TARGET_MOVED` row, which drop the base merge), `CAP-DLV-delivery-workflows`, `CAP-HARN-agent-guidance`
  (bundle-source integration and Repository verification policy) and `UC-drive-development-to-integration` state the
  changed contract; `docs/development/reference/{worktree,integration}.md`,
  `docs/development/{ci-cd,workflow}.md`, `AGENTS.md` (Verification) and `guides/INSTALL_GUIDE.md` (Git 2.38 note)
  follow. The two PADRs become ADRs; `ADR-local-and-pull-request-integration` and `ADR-test-selection-and-ci` get a
  "Superseded in part by" line each.

### Acceptance criteria

- A conflict-free moved target integrates (`devkit integration prepare` then `integrate --route local`) and is accepted
  (`devkit spec proposal accept --mode accept_only`) without a base merge into the task branch; the landed merge's first
  parent is the target and its second the approved source (respectively the acceptance commit).
- A conflicting moved target refuses at prepare with `WORKTREE_MERGE_CONFLICT` and leaves the target, source and
  worktree unchanged.
- A moved target that changed `dev-integration`, `delete_branch` or `[tool.spec]` integrates when the source did not
  change them. CI-rule drift on the merged result refuses at prepare with `INTEGRATION_NOT_READY`; in composed
  acceptance it, and a target change to the proposal directory, refuse with `SPEC_PROPOSAL_APPROVAL_NOT_READY` and
  no acceptance commit.
- Two preparations of the same source and moved target print the same digest, also when the second runs with a
  different Git identity and `TZ`.
- `merge = "ff-only"`, `devkit worktree finish --merge` and the pull-request route still refuse a moved target with
  their current codes.
- Every prepare, integrate and composed acceptance result that carries a request shows, in text and JSON, the
  readiness disclosure and the merged target SHA (prepare: confirmation target; integrate and composed acceptance: build
  target and landed result; cleanup-only and `ff-only`: the prepared target).
- `spec-orchestrate` Completion names the batch test run, including that a unit ending blocked, waiting for a user
  decision or continuing in `direct` counts as finished for it, and `spec-integrate` step 1 is conditional (bundle asset tests).

### Non-goals

- **Scope Excluded**: rebase, force operations or automatic conflict resolution.
- **Scope Excluded**: dropping readiness checks, or bypassing a host refusal at runtime. Changing the containment
  contract through Planning and an ADR is this proposal's intent, not a bypass.
- **Scope Excluded**: automatic revert of a merge whose post-batch test run fails.
- **Scope Excluded**: merging a moved target in `devkit worktree finish --merge` (no readiness provider), under
  `merge = "ff-only"`, or on the pull-request route.
- **Scope Excluded**: a CLI command that runs or records the batch test run.
- **Scope Excluded**: tolerating, under `ask`, a target that moves between the presented prepare and `integrate`
  without a fresh decision; it needs a new preparation, not a base merge.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-integration-merge-moved-target`; the proposal is deleted there and its decisions become ADRs.
- Integration order: every child of `MS-git-operator-lifecycle-refinement` owns `spec-orchestrate/`, so Development
  integrates them one at a time in dependency order; this proposal integrates before
  `PROP-git-operator-planning-completion-route`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
