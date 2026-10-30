---
reconcile_id: REC-integration-merge-moved-target
spec: SPEC-integration-merge-moved-target
status: resolved
targets:
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-test-selection-and-ci.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: waived
    rationale: >-
      Outside the write scope the accepted proposal grants (its boundaries own only UC-drive-development-to-integration
      among use cases). Nothing in it contradicts the change: its composed-acceptance steps defer to
      CAP-DLV-proposal-planning, which states the moved-base merge, the refusal before the acceptance commit and the
      result fields. The missing extension is tracked as feedback FB-proposal-usecase-moved-base-acceptance.
---

# Reconcile: `SPEC-integration-merge-moved-target`

## Contract comparison

- `CAP-INT-mcp-services` states that local `prepare` of a source that does not contain the confirmation target builds
  the prospective merge and runs the guards on the merge base, readiness, the receipt check and the prospective
  policy on it (AC-01, AC-03, AC-04, AC-05), that the prospective commit is deterministic (AC-07), that `ff-only`,
  `finish --merge` and the pull-request route keep `WORKTREE_MERGE_NOT_FF` (AC-08), the new text fields of
  `[INTEGRATION_PREPARED: ...]` and `[INTEGRATION: ...]` (AC-09), the changed-target recovery and the
  `INTEGRATION_TARGET_MOVED` row without a base merge. Code: `integration/usecases/service.py` `_prepare`,
  `integration/cli.py`, `integration/usecases/pull_request.py`.
- `CAP-WT-task-worktrees` states `plan_finish(advance=True)` as the local integration's opt-in and
  `build_result(prospective=True)` as the deterministic unsigned prospective commit; its `finish --merge` containment
  rule is unchanged (AC-08, AC-10). Code: `worktree/usecases/planning.py`, `worktree/services/merging.py`.
- `CAP-DLV-delivery-workflows` §4.8 states the prospective context the `spec` provider receives at `prepare`, the
  conditional-base-merge wording of CI-rule reasons on a merged result, `result_reasons` and `SPEC_POLICY` read from the
  prospective result (AC-04, AC-05). Code: `delivery/usecases/integration.py`.
- `CAP-DLV-proposal-planning` states that composed acceptance merges a moved base, that its preview refuses failing
  result checks before the acceptance commit (AC-02, AC-06), and the `target_sha=`, `landed_sha=`, `disclosure=` fields
  of `[ACCEPTED: ...]` and their JSON keys (AC-09). Code: `delivery/usecases/native_plan_accept.py`,
  `delivery/cli/proposals.py`.
- `CAP-HARN-agent-guidance` replaces "Integration incorporates a moved base" in the repository verification policy
  with the conditional base merge and the batch test run, and makes the bundle-source base merge and re-sync
  conditional on `WORKTREE_MERGE_CONFLICT`, `INTEGRATION_RECEIPT_CONFLICT` or `INTEGRATION_NOT_READY` (AC-11). Source
  assets: `spec-integrate`, `spec-orchestrate` and its `git-operator-operations.md`, `spec-review-proposal`,
  `spec/references/completion.md`. It now lists `UC-drive-development-to-integration`, which cites it for the batch
  run, both ways.
- `UC-drive-development-to-integration` drops the routine base merge from step 6, presents the merged target and
  disclosure at step 7, adds extension 7i (a refused preparation of a moved base), returns 8a to a fresh preparation,
  adds the batch test run to 1b and scenarios 29 to 31.
- `ADR-local-and-pull-request-integration` gains the "Superseded in part by" line naming `ADR-moved-target-merge`
  that its follow-ups require; `ADR-test-selection-and-ci` gains the same line naming `ADR-post-batch-test-run` as a
  consistency repair. Status and `superseded_by` are unchanged. `ADR-post-batch-test-run`'s own follow-ups
  (`AGENTS.md`, `docs/development/ci-cd.md`, `docs/development/workflow.md`, `CAP-HARN-agent-guidance`) are done.
- `UC-plan-and-hand-off-a-proposal` is waived below: it lies outside this change's write scope.

Reference documents follow the same contract without being Living Spec targets: `docs/development/ci-cd.md`,
`docs/development/workflow.md`, `docs/development/reference/{worktree,integration}.md`, `AGENTS.md` (Verification,
outside the managed block) and `guides/INSTALL_GUIDE.md` (Git 2.38 note).

No architecture contract changed: no layer direction or package boundary moved and `packages/devkit-core/` is
untouched. No new domain term: "moved target" and "prospective merge" are the terms the ADRs and `CAP-INT-mcp-services`
already use. No screen changed.

## Source feedback and deferred work

The spec names no source feedback. `FB-proposal-usecase-moved-base-acceptance` tracks the waived
`UC-plan-and-hand-off-a-proposal` extension. `FB-local-render-fix-ignores-worker-write-scope` and
`FB-partial-supersession-hides-in-force-clauses` stay open for their own owners. Nothing in scope is deferred; the
acceptance route that follows this change is `PROP-git-operator-planning-completion-route`, already planned.

## Review and verification

The initial medium `code-reviewer` reviewed 83286f89 and reported three P3 findings (`review-01.yaml`); the
implementer fixed them at e7510cd6 and closed them in `reverify-01.yaml`. The independent medium `reconcile-reviewer` checked 48f56acc with no P1 and two P2 and four P3
findings (`reconcile-check-01.yaml`); the implementer fixed the CAP-HARN trigger list and route qualifier, UC 7h and
7i, the CAP-DLV-proposal-planning field timing, the CAP-INT refusal list and `INTEGRATION_NOT_READY` row and this
record's ADR attribution, and waived the out-of-scope use case with feedback (`reconcile-check-02.yaml`). Sync outputs: `devkit sync --check` passed at
the start; `.devkit/installation.json` is the only tracked output and is listed in Task 3 as `(sync output)`.
Baseline: at cf991c47 `test_diverged_branch_is_refused_with_a_sha_preserving_fix` passed (prepare of a moved target
refused with `WORKTREE_MERGE_NOT_FF`); after the change, prepare and integrate of the same setup land the merge
(`test_moved_target_before_preparation_lands_a_merge_without_a_base_merge`).

## Entrypoints

Added `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py` to `CAP-DLV-delivery-workflows`
(the §4.8 provider doorway) and `packages/devkit/src/devkit_agt/features/worktree/usecases/planning.py` to
`CAP-WT-task-worktrees` (`plan_finish`). Rejected: the receipt, `AGENTS.md`, `guides/INSTALL_GUIDE.md`, test
directories and whole feature directories, which are hubs or already covered by existing entrypoints.
