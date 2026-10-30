---
id: MAT-workflow-record-commit-development
title: Workflow record commit Development evidence
summary: "Same-head write-only baseline and explicit commit observations, including real Git recovery, hook effects and workflow readiness checks. No speed or cost improvement is claimed."
created_at: 2026-10-30
---

# [MAT-workflow-record-commit-development] Workflow record commit Development evidence

## Baseline and outcome

The implemented-head integration test `test_review_reverify_final_report_readiness_and_read_only_commands` records the HEAD after a committed reverify. Final-report authoring and `next`, `show` and `envelope check` retain that HEAD. It captures the final-report bytes, then explicitly commits that file: HEAD changes, bytes stay identical and workflow readiness including revision-ancestor passes. This is the accepted same-head baseline with commit omitted, not a timing comparison or checkout of the base. Existing evidence SHAs remain unchanged.

`test_exact_commit_idempotence_and_evidence` verifies one added path, expected blob, one parent, clean checkout, deterministic subject/body and actual final HEAD. A repeat produces already_committed and null subject. Differently named branches and SPEC/PROP identities are covered. Real rejecting pre-commit/commit-msg hooks, signing failure and same-file staged retry retain the record without allocating another sequence. A metadata-rewriting post-commit hook reports actual final HEAD; extra content, staged paths, extra commits and a simulated unknown process outcome preserve resources and report uncertainty.

## Verification

Initial focused runtime suite: 40 passed. Bundle guidance checks: 3 passed. Deterministic policy unit coverage is included in affected tests. `just test-affected --base c29602db8b804e956cef4d8fa4a58e4208cc1c7e` selected mode=partial, 115 paths and passed 2088 tests. The full fallback remains enabled. Both devkit and devkit-spec lint/format and type checks passed; governance rules passed with zero violations. Later review/final envelopes record verification after fixes.

The unchanged integration engine's `test_integrate_cli_refuses_source_changed_after_preparation` checks that advancing source HEAD makes the prepared digest stale before integration effects. Integration preparation remains a Host step after the final record commit. No gate, worktree or integration engine changed.

## Deployment

The worker's initial sync check passed (exit 0). Spec bundle source guidance sync updated only `.devkit/installation.json` among tracked deployment outputs; Task 2 lists it as `(sync output)`. Managed and host-projected copies remain generated/ignored.


## Independent review fixes

The medium code-reviewer found three issues: uncaptured symbolic HEAD identity, ineligible final-report authoring guidance, and Unit-relative advisory targets. The implementation captures and rechecks the branch reference before staging, after hooks and on failure; the real post-commit branch-switch regression returns UNCERTAIN while preserving the new branch and clean committed content. The final-report example now supplies stage and summary. Invalid-identity tests verify workspace-relative selected targets. The author verified all fixes: runtime plus guidance 45 passed; affected selection 2090 passed in 19.07s; both package lint/types and governance checks passed. The reviewer's denied throwaway probe remained stopped; the regression was added through the ordinary approved tracked test scope.
