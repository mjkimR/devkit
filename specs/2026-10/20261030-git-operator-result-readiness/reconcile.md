---
reconcile_id: REC-git-operator-result-readiness
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconcile: `SPEC-git-operator-result-readiness`

## Contract comparison

- `CAP-DLV-proposal-planning` (Host-authorized proposal lifecycle CLI) states the composed handoff commit as
  `ADR-composed-handoff-commits-its-own-transaction` decides and `native_handoff._commit_handoff` implements it: the
  whole `git status` delta staged and committed once with `spec: hand off <slug> to Development`, `commit` read
  after `git commit` returns, the single-parent and clean checks (`_verify_handoff_commit`, `SPEC_HANDOFF_STALE` on a
  landed but unclean commit), and the refusal (`SPEC_HANDOFF_COMMIT_REFUSED`, `INPUT_ERROR`, `commit=-`, next action,
  no next command, writes staged, exit `1`). The output paragraph adds `commit=` to `[HANDOFF: ...]` and to the
  `accept_and_handoff` `[ACCEPTED: ...]`; the acceptance paragraph names `handoff`, `handoff_commit` and `commit`.
  The error table gains the new row and widens the `SPEC_HANDOFF_STALE` row. The dropped-record sentence "handoff does
  not create a commit" is narrowed to the plain form. §4.7 states the unchanged sibling rewrite and the
  take-base-then-`devkit rules fix` resolution. Verified by AC-01..AC-04 tests
  (`test_handoff_commit.py`, `test_composed_output.py`, `test_handoff_error_modes.py`, `test_plan_accept_cli.py`).
- `CAP-DLV-delivery-workflows` §4.6.1 states `checks.worker_input {head, dirty_paths}` for `prepare-worktree` and
  `handoff`, dirty paths as `remaining_effects` with `needs_input`, no other readiness, permission or next-actor
  field, the Host's comparison before a worker, the evidence separation and the GOP-06 operator-scope wording, as
  `git-operator.md`, `git-operator-dispatch.md` and `git-operator-operations.md` state them. Verified by AC-05..AC-07
  contract-text tests in `test_git_operator.py`.
- `CAP-DLV-proposal-planning` and the review fix: a landed commit that is not one clean direct child of the base is
  `SPEC_HANDOFF_STALE` whose `[FIX]` repairs `dev-<slug>` in place, and every stopped outcome after the handoff
  writes clears the nested next command (`test_a_landed_commit_that_leaves_files_is_repaired_in_place`).
- `UC-plan-and-hand-off-a-proposal` updates step 9 (link fixes in a later Host commit after the composed handoff, in
  the writes' commit after the plain one), extension 7a (the committed handoff, `checks.worker_input`, the refused
  commit), the new extension 8a (sibling conflict), the minimal guarantee (a refused handoff commit keeps the writes)
  and Scenario 12, and adds Scenarios 21-23.

`CAP-WT-task-worktrees` is unchanged: worktree start and setup did not change (non-goal 5). No architecture contract,
glossary term or screen changed. `ADR-composed-handoff-commits-its-own-transaction` needs no repair: its references
resolve and its decision is implemented as written.

## Source feedback

- `FB-handoff-rewrite-edits-sibling-draft`: resolved. The final diff keeps the sibling rewrite and adds the
  take-base-then-`devkit rules fix` resolution to `post-handoff.md`, `CAP-DLV-proposal-planning` §4.7 and
  `UC-plan-and-hand-off-a-proposal` extension 8a; `test_post_handoff_guidance.py`, `test_unit_dependencies.py` and
  the medium code review (review-01, reverify-01) verify it. Its Resolution section names the evidence.
- The unit's other feedback files (`FB-received-feedback-status-during-planning`, `FB-reverify-resolve-overwrites-waiver`)
  arrived with the handoff but are not addressed by this unit's scope; they stay open.

## Deferred work

None: every acceptance criterion is implemented in this unit.

## Review and verification

Medium code review (nested `code-reviewer`) at 3142b1d7 found one P2 and two P3 findings (`envelopes/review-01.yaml`);
the implementer fixed them at 78b9d3f1 and closed the round in `envelopes/reverify-01.yaml`. The initial
`devkit sync --check` passed; `.devkit/installation.json` is the only tracked sync output (Task 2.2, `(sync output)`).

## Entrypoints

The three targets already list the doorways this change touched (`native_handoff.py`, `native_plan_accept.py`,
`cli/proposals.py`, `git-operator.md`); no entrypoint changes.
