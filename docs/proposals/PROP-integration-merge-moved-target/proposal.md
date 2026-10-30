---
id: PROP-integration-merge-moved-target
title: Integrate a conflict-free moved target without requiring the source to contain it
summary: "Let local integration and proposal acceptance merge a moved target themselves and refuse only on a real conflict or failing checks, and run the tests once on main after a local-orchestrated batch is integrated, so lifecycle merging stays light while defects still surface."
status: draft
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
- Once every unit a local-orchestrated run started is integrated and no Development work remains, the Host runs the
  project's tests once on `main` (one run on the integrated head, not an aggregation of earlier results). A failure
  is reported with its evidence and becomes follow-up work; nothing is reverted automatically.
- The `spec-integrate` step 1 base merge becomes conditional: the Host merges the base into the task branch only to
  resolve a conflict or a failing check the CLI reports.

## 2. Technical Spike Questions

- **Q1 Merge construction**: How does `plan_finish` build the merge commit when the target moved (merge in the object
  store, as it does today for later target advances), and which stable code reports a real conflict?
- **Q2 Policy values**: Does `[worktree] merge = "ff-only"` keep refusing a moved target by its own definition?
- **Q3 Pull-request route**: Is the PR route in scope, where the remote performs the merge and
  `integration/usecases/pull_request.py` raises the same code?
- **Q4 Drift on the result**: How are receipt or `devkit rules fix` drift on the CLI-built merge detected and refused,
  such as the reference rewrites the Host fixed by hand on 2026-10-30?
- **Q5 Batch test run**: Where does the post-batch run live (spec-orchestrate Completion, a CLI helper, or both), which
  command it runs (`just test-affected --base <batch start>` with its `mode=full` fallback, or the full suite), and
  how its result is reported?
- **Q6 Decision record**: Which ADR supersedes the containment rule, and which tests pin `WORKTREE_MERGE_NOT_FF`
  (for example `packages/devkit/tests/e2e/features/integration/test_base_advance.py`)?

## 3. Proposed Design & Impact

- `devkit-agt` worktree and integration use cases merge a conflict-free moved target as a merge commit; no SHA is
  rewritten and no rebase or force operation runs.
- `devkit-spec` delivery readiness and acceptance reuse that behavior; the readiness disclosure and the merged target
  SHA appear in every integration result.
- `spec-integrate`, `spec-orchestrate` and the spec skill references drop the unconditional base merge and add the
  post-batch test run.
- `CAP-WT-task-worktrees`, `CAP-INT-mcp-services` and `CAP-DLV-delivery-workflows` carry the changed contract; a new ADR
  records it.

### Non-goals

- **Scope Excluded**: rebase, force operations or automatic conflict resolution.
- **Scope Excluded**: dropping readiness checks, or bypassing a host refusal at runtime. Changing the containment
  contract through Planning and an ADR is this proposal's intent, not a bypass.
- **Scope Excluded**: automatic revert of a merge whose post-batch test run fails.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-integration-merge-moved-target`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
