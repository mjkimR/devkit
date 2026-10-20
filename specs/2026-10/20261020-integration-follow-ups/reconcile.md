---
reconcile_id: REC-integration-follow-ups
feature: SPEC-integration-follow-ups
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/roadmap/MS-multi-host-native-integration.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-target-advance-readiness.md
    resolution: modified
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
---

# Reconciliation: integration base advances

- `CAP-INT-mcp-services`: the service lands a merge commit built outside the base checkout (a fast-forward under
  `[worktree] merge = "ff-only"`); the request binds the confirmation target, the merge method, the cleanup-only flag,
  the effective policy digest and the provider's target-bound codes and disclosure; one build per approving call
  (descent check, `merge-tree` on an advanced target, guards and readiness with the execution context, result policy
  and receipt checks, compare-and-swap with `INTEGRATION_TARGET_MOVED`); the form text; the provider contract
  (`result_sha`, `target_bound`, `disclosure`); resume onto the last build target only, recovery by result ancestry,
  the 20-second lock wait of the approving call and `LOCK_HELD` directives (sections 1, 2, 3, 5 and 6).
- `CAP-WT-task-worktrees`: `finish --merge` requires the branch to contain the base HEAD, takes the integration lock
  and lands a devkit-built merge commit (`merging.py`, added to `entrypoints`); the SHA-preserving
  `WORKTREE_MERGE_NOT_FF` and `WORKTREE_PUSH_REJECTED` fixes (a fixture showed `git pull --rebase=merges` rewrites the
  unit's SHAs, so the fix is fetch plus `git merge --no-ff -m ... FETCH_HEAD`, with its cost stated); the rerun
  without a build; the `merge` key; `validate_finish` after the merge.
- `CAP-DLV-delivery-workflows`: the `worktree finish` command row and section 4.8 (execution context, CI rules on the
  result tree, unit-directory reason, `SPEC_POLICY`, target-bound codes and disclosure).
- `CAP-DLV-project-policy`: the `[worktree] merge` default and template line, and the merge method among the policies
  devkit models.
- `CAP-COLL-work-scope-registry`: item 9 states the post-merge criterion of devkit-spec's scoped cleanup (the base
  HEAD contains the result commit and the worktree is gone; later base commits allowed). `CAP-INT-mcp-services`
  section 4 states that cleanup receives the execution context.
- `MS-multi-host-native-integration`: exit condition now reads "bound to the verified source commit and the
  confirmation target and its descendants" (user decision in Planning).
- References: `docs/development/reference/integration.md` and `worktree.md` (codes, APIs, the merge key).
- `ADR-target-advance-readiness`: wording only; the handoff deleted the proposal's `answer-01.yaml`, so its trace now
  reads "(user decision)", as the other promoted ADRs do.

Outside `docs/`: the devkit-spec bundle guidance (`spec-integrate`, `spec/references/completion.md` and
`worktree.md`), the `[worktree]` config template (`devkit config template`), `guides/INSTALL_GUIDE.md` (Git 2.38 for
an advanced target) and the smoke fixture provider. No story describes integration, so none changes; no glossary term
was introduced.

## Source feedback

- `FB-integration-stale-on-base-advance`: fully addressed (AC-01 to AC-13 and AC-16, verified by
  `packages/devkit/tests/integration/test_base_advance.py`, `test_service.py`, `test_mcp.py`,
  `packages/devkit-spec/tests/test_integration.py` and the code-reviewer rounds `review-01`/`review-02`). Its file
  (specs/2026-10/20261019-high-effort-review-loop/feedback/integration-stale-on-base-advance.md) is outside this run's
  write scope: the Host sets it to `resolved` with the disposition `SPEC-integration-follow-ups`.
- `FB-auto-integration-dispatch`: not delivered (Non-Goal 1); stays `open` with its current disposition.
- `FB-multi-host-integration-ergonomics`: not delivered (Non-Goal 3); dismissed when the broader host-confirmation draft was retired for the two-terminal-host usage scope.
- `FB-pr-remote-and-squash-integration`: not delivered (Non-Goal 2); stays `promoted` to
  `SPEC-integration-pull-request-cleanup`.

## Deferred work

None: Planning moved PR cleanup and automatic dispatch to `SPEC-integration-pull-request-cleanup` and
`FB-auto-integration-dispatch`. The separate host-confirmation draft was retired;
`FB-multi-host-integration-ergonomics` records its dismissal. The receipt `.devkit/installation.json` must be
re-synced for the edited spec bundle files (`devkit sync`) before integration; `.devkit/` is outside this run's write
scope.
