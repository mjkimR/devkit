---
id: PADR-moved-target-merge
title: Integrating command merges a conflict-free moved target
summary: For integrating a source that does not contain a moved target, we let the integrating command build and check the merge itself and refuse only on a real conflict or failing readiness, to drop the manual base merge, accepting that only CI rules run on the merged result.
proposal: PROP-integration-merge-moved-target
status: draft
created_at: 2026-10-30
supersedes:
  - ADR-local-and-pull-request-integration
---

# [PADR-moved-target-merge] Integrating command merges a conflict-free moved target

- **Status**: Draft
- **Date**: 2026-10-30

This decision supersedes only the containment clauses of `ADR-local-and-pull-request-integration` for the local
route: "`prepare` still requires the source to contain the target" and its not-fast-forward fix "merge the target into
the branch, re-verify, prepare again". The merge construction outside the checkout, readiness on the result, policy
binding, receipt check, integration lock, pull-request route and cleanup guards of that decision remain in force.

---

## 1. Context & Problem Statement

`devkit integration prepare --route local` and `devkit spec proposal accept --mode accept_only|accept_and_handoff`
refuse a source that does not contain the target's HEAD (`WORKTREE_MERGE_NOT_FF` in `plan_finish`). The Host then
merges the base into the task branch, reruns checks (and `devkit rules fix` when the merge brought reference drift)
and retries, even when the merge is conflict-free and touches unrelated files. The integrate call already absorbs
target commits that land after preparation: it builds the merge in the object store with `git merge-tree
--write-tree`, reruns the finish guards on the real merge base and the readiness provider on the result, checks the
result's effective policy digest and the receipt records, and refuses on a conflict with nothing changed. Only a move
that happened before preparation is refused.

## 2. Decision Drivers

- Lifecycle branch checks stay light; tests verify behavior (user direction).
- A real textual conflict or failing readiness still refuses with nothing changed on the target.
- A semantic conflict may surface later in CI, nightly CI or hygiene; a hidden one may not, so every integration result
  states what was checked on the merged result and which target it merged.
- What can be checked locally is refused before the user's confirmation, not after it.
- The approved source SHA lands; no rebase, force operation or rewrite of the task's cited SHAs.
- One request digest per scope: two preparations of the same source and target yield the same digest.

## 3. Considered Options

- **Keep containment** (rejected): every unrelated base commit costs a merge commit on the branch, a rerun of checks
  and a retry; observed twice in one local-orchestrated run.
- **A: drop the refusal and check only at integrate** (rejected): smallest change, but the prospective policy digest
  is read from the source, so a target that changed an effective integration policy key or `[tool.spec]` refuses
  after the user's OK on every retry until the base is merged; conflicts and CI-rule drift also surface only after
  the confirmation.
- **B: build the prospective merge at prepare** (selected): prepare builds the merge in the object store, runs the
  guards on the real merge base, the readiness provider on the result, the policy digest from the result and the
  receipt check before the scope is presented; integrate rebuilds on the current target as today. Costs a
  `merge-tree` and CI rules over the result at prepare and a change to what the request digest covers.
- **C: merge the target into the task branch automatically** (rejected): rewrites the approved source, needs a checkout
  mid-merge and leaves conflicts in the worktree.

## 4. Decision Outcome

Chosen option B, because it removes the manual base merge while refusing conflicts, CI-rule failures and policy
changes before the confirmation.

- Under `[worktree] merge = "no-ff"`, local preparation accepts a source that neither contains nor is contained by the
  target. It builds the prospective merge commit with `build_result(advance=True)`, unsigned and referenced by no
  ref, and passes it as the execution context's result to the finish guards (with `merge-base(target, source)`), the
  readiness provider, the receipt check (`receipts.check_merge`) and the prospective policy digest.
- A conflict refuses at prepare with `WORKTREE_MERGE_CONFLICT` and nothing changed; failing readiness on the result
  refuses with `INTEGRATION_NOT_READY` and its reasons. Their fix is the conditional base merge: merge the target into
  the task branch to resolve the reported conflict or check, re-verify what the merge changed, prepare again.
- The request digest excludes the prospective result commit (the readiness `result_sha` and the evidence codes the
  provider declared target-bound), so two preparations of the same source and target yield the same digest.
- Integrate keeps today's build: it rebuilds on the current target (which must descend from the confirmation target),
  reruns the guards, readiness, policy digest and receipt check, and fast-forwards the base onto the result.
- Every prepare and integrate result, text and JSON, carries the readiness disclosure and the target SHA the command
  merged (prepare: the confirmation target; integrate: the build target and the landed result). The composed
  acceptance result carries the same two values.
- `merge = "ff-only"` keeps refusing a moved target with `WORKTREE_MERGE_NOT_FF`, because a fast-forward cannot absorb
  it; its fix names merging the target into the branch or the `no-ff` policy.
- `devkit worktree finish --merge` keeps refusing a moved target: it runs no readiness provider, so a merge it built
  would land an unchecked tree.
- The pull-request route keeps its containment refusal: the platform builds its own merge, and its required checks run
  on the platform's merge ref.

## 5. Consequences

- **Positive**:
  - Unrelated base commits no longer require a branch merge, rerun and retry before integration or acceptance.
  - Policy changes, `[tool.spec]` changes, reference drift and receipt inconsistencies on the merged result refuse
    before the confirmation instead of after it.
- **Negative / Risks**:
  - A semantic conflict no CI rule catches can land after a conflict-free merge; tests and review ran on the source
    only, as the disclosure states. `PADR-post-batch-test-run` adds the batch run that surfaces it.
  - Preparation of a moved target needs Git 2.38 or later (`WORKTREE_GIT_UNSUPPORTED` otherwise) and costs a
    `merge-tree` and CI rules over the result.
  - Composed acceptance runs the delivery readiness only after its acceptance commit; CI-rule drift on the result
    then returns `needs_recovery` with the acceptance committed on the Planning branch, as for any readiness failure
    there today.
- **Follow-ups**:
  - Development adds a "Superseded in part by" line to `ADR-local-and-pull-request-integration` naming this
    decision, without changing its status or `superseded_by`.

## 6. Confirmation

- Tests: a conflict-free moved target integrates and accepts without a base merge; a conflict refuses at prepare with
  nothing changed; a target that changed an effective policy key or `[tool.spec]` integrates; CI-rule drift on the
  result refuses at prepare; two preparations yield one digest; `ff-only` and `finish --merge` still refuse
  (`packages/devkit/tests/e2e/features/integration/test_base_advance.py`,
  `packages/devkit/tests/integration/features/worktree/test_merging.py`,
  `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, the plan-accept CLI tests).
- Review: `CAP-WT-task-worktrees`, `CAP-INT-mcp-services` and `CAP-DLV-delivery-workflows` state the changed
  contract.
