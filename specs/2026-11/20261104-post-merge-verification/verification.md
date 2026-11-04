# Verification evidence: post-merge verification

## Baseline and outcome

Baseline is the accepted input `810adf730993710119ab351b4bbbdce7d716ad98`, read with `git show` without checking it out. An AST scan of integration `usecases/service.py`, `usecases/pull_request.py` and `services/providers.py` counts direct calls ending in `providers.check`, `providers.run_finish_guards`, `receipts.check_merge`, `receipts.check_reader` or `check_rule_runtime`.

The baseline has eight such call sites (service: four, PR route: three, provider runtime: one); the implementation has zero. This is a static coupling measurement, not a timing or failure-rate estimate. Positive fixtures additionally spy on readiness/finish-guard discovery and exercise missing provider configuration, absent rule imports/distributions and a future receipt schema while preserving Git protections.

## Host procedure walkthrough

1. Verify the source with its own runtime, including source workflow holds. Save the target SHA before the first merge and obtain the configured authority for Git effects.
2. Integrate and inspect the confirmed landed SHA and exact cleanup effects. `verification=pending` leaves delivery unfinished; unknown landing is `not_started` and retains recovery state.
3. On the landed target, run the repository setup command in a fresh process, then bundle sync and generated checks. Commit required regeneration before final checks. A setup/import failure stops completion and is repaired on the target.
4. Run required lint, types, rules and `just test-affected --base <saved-target-SHA>` using fresh processes; retain selector full fallback and named frontend checks. Record commands, outcomes and the final checked HEAD.
5. A failing final check leaves all batch units pending. Repair the target and recheck that descendant; do not replay the completed merge or automatically roll it back. A later commit invalidates a claim about the current HEAD until affected checks cover it.
6. After accepted Planning, continue the existing handoff command in another fresh process, retaining mode, authorized scope and effort. Until then the result says handoff not started and has no handoff worktree/commit fields.

Guidance assertions verify this ordering and failure procedure. External final-check completion remains a Host responsibility; no CLI test runner or persistent verification ledger was introduced.

## Branch check results

`just test-affected --base main` selected `mode=full` because package metadata changed: 6566 passed, 15 skipped. Thirteen skips require a devkit-dist-only environment; two require Linux `/proc` and `os.waitid`, unavailable on this macOS host. Follow-up focused tests cover the final internal PR adapter signature cleanup. Both changed source packages passed lint/format and Pyright with zero errors. Staged governance rules passed with zero violations; bundle sync check reported no drift.

The temporary-Git final-check recovery regression passes: independently passing source and target combine cleanly but fail a fresh check, cleanup is already complete, and a repair descendant passes without another merge.

## Review round 1 recovery

All three P1 failure conditions were reproduced before fixes: partial acceptance omitted its confirmed landing in JSON/text (two failing cases), a no-ff cleanup-only retry falsely returned recovery using the source SHA, and text prepare omitted the merge SHA of an already merged PR after target advancement. The fixes use the confirmed landing and construct authorized continuation before partial returns, preserve cleanup-first recovery, and add the prepare text field. The affected acceptance/output/template suite passed 27 tests after fixes; the effective-versus-requested mode test additionally covers policy narrowing without handoff authorization. A fresh review round is required because public output changed.
