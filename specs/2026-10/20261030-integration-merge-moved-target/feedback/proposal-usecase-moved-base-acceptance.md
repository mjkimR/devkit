---
id: FB-proposal-usecase-moved-base-acceptance
title: UC-plan-and-hand-off-a-proposal lacks the moved-base composed acceptance extension
scope: repo
kind: change-request
category: other
target: UC-plan-and-hand-off-a-proposal
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-proposal-usecase-moved-base-acceptance] UC-plan-and-hand-off-a-proposal lacks the moved-base composed acceptance extension

Living Spec coverage gap left by a write scope that named only one delivery use case.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `SPEC-integration-merge-moved-target` changed composed acceptance
  (`devkit spec proposal accept --mode accept_only|accept_and_handoff`): a conflict-free moved base lands without a
  merge into `plan-<slug>`; a failing CI rule on the prospective result or a base change to the proposal directory
  refuses with `SPEC_PROPOSAL_APPROVAL_NOT_READY` before the acceptance commit; a conflict refuses with
  `WORKTREE_MERGE_CONFLICT`; the result carries `target_sha`, `landed_sha` and `disclosure`.
  `CAP-DLV-proposal-planning` states this, but `UC-plan-and-hand-off-a-proposal` has no extension for these refusals,
  because the proposal's `boundaries.owns` listed only `UC-drive-development-to-integration` among use cases.
- **Proposed Procedure**: Add a step 6 or 7 extension to `UC-plan-and-hand-off-a-proposal` naming the two refusals
  and the recovery (merge the base into `plan-<slug>`, `devkit rules fix` on the proposal, commit, rerun), and a
  scenario for a moved base that is accepted without a base merge.
- **Expected Benefit**: An agent following the use case finds the moved-base refusals and their recovery.
- **Cost & Risk**: A wording change of one use case; no behavior change.
- **Attempted**: The independent reconcile check of this spec found the gap; the reconcile records the use case as
  waived with this feedback as its destination.

## Evidence

```text
reconcile-check-01.yaml finding 1 (P2): UC-plan-and-hand-off-a-proposal is neither a reconcile target nor covered
by a no-impact statement; CAP-DLV-proposal-planning reflects the contract and nothing contradicts it.
```

## Disposition

Resolved by `SPEC-shipped-bundle-citations-and-doc-fixes`: `UC-plan-and-hand-off-a-proposal` has extension 6a (the
moved-base refusals `SPEC_PROPOSAL_APPROVAL_NOT_READY` and `WORKTREE_MERGE_CONFLICT` before the acceptance commit,
with the recovery), extension 7g (conflict-free landing without a merge into `plan-<slug>`, with `target_sha`,
`landed_sha` and `disclosure`) and scenarios 24 and 25. Verified against `CAP-DLV-proposal-planning` and
`packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`; `devkit rules check --ci --base main`
passes.
