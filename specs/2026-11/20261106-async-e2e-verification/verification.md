# Development verification evidence

## Comparable blocking experiment

Same fixture commit, argv, setup, isolated environment, machine and resource limits. Async disabled by waiting for the exact same supervisor process inside its launch Popen wrapper; one warmup then three samples per arm. 0.9s independent-work fixture follows launch in each arm. Timing includes process observation; not whole-suite speedup evidence.

Measured runtime source: `82ab7efb` plus the retained established-group leader validation fix in this batch. Fixture commit: `e4e873bc2ee4ef32890918bb0d4da600aff0301d`; platform macOS. The fixture runs a standard-library native command sleeping 0.8 seconds and checking one committed input; each arm then performs the same 0.9-second independent-work fixture. Both arms use identical detached-checkout preparation and cleanup. This measures caller blocking, not suite acceleration or a comparison against current-directory commands. No network/service resources are used.

| Mode | Launch return median s | Host blocked median s | Preparation median s | Native + observation median s | Child CPU median s | Child peak RSS median MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| synchronous-disabled-async | 1.127 | 1.262 | 0.131 | 0.902 | 0.570 | 15.625 |
| asynchronous | 0.064 | 0.388 | 0.128 | 0.931 | 0.584 | 16.312 |

Both arms pay detached checkout/runtime/evidence storage and supervisor/process-observation CPU cost. Asynchrony overlaps that work with the caller and adds no claim of lower test CPU or full-suite latency. RSS covers reaped children, not aggregate concurrent peak memory. The native command plus observation has similar duration; the latch regression separately proves ordering before release. The baseline is the same head implementation with asynchronous launch disabled, not a checkout of the base.

## Reproduction

The retained harness is `evidence/measure_blocking.py`; run it from the Development worktree with `uv run --no-active python <unit>/evidence/measure_blocking.py` which creates a fresh ignored `scratch/blocking-consumer-<time>` path. The original ignored fixture and its evidence remain in this worktree. `blocking-measurements.json` holds warmups, all samples, runtime IDs and resource measurements.

## Focused verification

- Selector E2E: 91 passed, including edited/explicit E2E, broad mixed directories, shared/unknown full fallback, embedded rule tests, compatibility and empty-tier no-op.
- Execution: 14 subprocess lifecycle probes plus 2 process-identity unit tests passed. Includes fixed SHA/environment, latch ordering, native shell/build argv, setup/locked-sync failure, default retention, parent-return discovery, missing/reused supervisor, interrupted waiter/supervisor, nested session and actual compact cancellation, surviving child, dirty/unrelated/active/unknown refusal and concurrent/idempotent cleanup.
- Guidance/registration: 27 passed; moved-target/doc-code checks: 12 passed.
- Full affected unit/integration fallback, lint/types and governance results are recorded by the final review and worker envelopes after completion.

## Limits and boundary evidence

Linux code paths are designed and statically checked but not executed on this macOS host. Host descendant-kill policies, host application exit, reboot survival and intentional process escape are outside the contract. No OS containment guarantee is claimed. External service/data isolation remains project responsibility.

Host projection is emulated: all commands use the absolute named worktree as cwd; Git uses git -C; sibling writes and shared Git effects are individually escalated and reviewers receive absolute read/probe scopes. These measures are not native path confinement. The first authoring scratch script was mistakenly written to `/private/tmp/devkit_exec_impl.py`; the Host explicitly accepted retention of that one artifact and all later scratch stays under the ignored worktree scratch directory. No deletion or alternate write route was used.

## Review repair and check history

High code review round 1 found two P1 ownership/output defects and four P2 interface/integration defects. Both P1 implementation regressions failed before repair (orphan missed; wait output 4,025,118 bytes). The repaired focused batch passes 24 tests, including retained group ownership until empty, retired-group PID reuse refusal, immediate same-group surviving child, bounded history/argv projection, list pagination/corrupt evidence and text sentinel escaping. Complete internal ownership evidence remains on disk. A separate combined focused run passed 95 cases including existing output/registration/UC parser checks.

The first `just test-affected --base ede62bde -- --basetemp scratch/pytest-affected-1` invocation was invalid: fixtures without their own Git root inherited the ignored scratch parent and appeared empty to rule discovery. It was interrupted and preserved. The same first failing rule file passed 12/12 with a system temporary fixture root. Corrected full fallback then produced 6,357 passed, 3 skipped and four ordinary registration/directive/UC syntax failures, which the repair batch addresses; final corrected fallback is recorded in the final envelopes.

Offline package verification: `uv build --package devkit-agt --wheel --out-dir scratch/wheels --offline` succeeded. The resulting wheel includes the exec entry point, captured runtime and worktree execution API.

## Bounded-recovery stop

Round 2 independently reproduced a recurring P1 at the supervisor terminal gate (passed and cancelled variants) and a P1 cleanup-interruption persistence gap. The passing general suite does not establish these acceptance conditions. This run ends with a problem and no final change report; `recovery-handoff.md` names exact evidence, pending user-required guidance refinement and remaining reconcile/final stages.


## Host-directed recovery of round 2

The Host authorized the same goal/scope remedy and one further fresh independent code-review round 3; this preserves rounds 1/2 and their evidence. Initial recovery `devkit sync --check` passed exit 0. The exact retained R2 probes ran before edits: 3 failed, 2 passed (both passed/cancelled terminal gate variants and interrupted cleanup failed). The unchanged probes and feature-owned translations then passed after repair; focused runtime, lifecycle and guidance verification passed 35 cases before the additional cleanup-serialization regression.

The supervisor retains established stage groups through a fresh post-poll enumeration. It persists pending ownership before postlaunch enumeration and publishes terminal evidence only after positive group quiescence. Enumeration/signalling exceptions leave unknown state and no result. Positively quiesced stage histories remain inspectable but retire from current PID ownership, so later unrelated PID reuse is not signalled or interpreted as an active former writer. This is a portable post-exit gate, without Linux-only waitid assumptions.

Cleanup atomically records in_progress before removal. Interruption leaves unfinished evidence; native removal inherits the cleanup lock, and caught interruptions settle the already-started remover before releasing it. Explicit retry revalidates terminal/process/checkout ownership. Only an absent owned checkout with its exact retained Git registration/marker permits retiring that registration; no dirty or present unrelated checkout permits force removal. Original execution result and logs remain unchanged.

Guidance walkthroughs: (1) inspect docs/scripts/runner/CI and prove the devkit selector's unit/integration command excludes the E2E command's coverage, then run sync group at A, background E2E at fixed A, retain B..C across generated repairs, collect A without calling C tested, and select the uncovered interval at C; (2) a broad pytest tests/npm test already includes browser checks, so a second browser command is duplicate coverage rather than reduced synchronous blocking; establish existing disjoint commands before splitting; (3) an unseparated, unclear or no-E2E consumer keeps every existing required command synchronous and creates no empty E2E evidence; (4) failed/unknown background result holds merges at the next observation and prioritizes repair. No automatic verification restructuring, daemon, native-command retry, profile map or local/cloud selector is introduced.


Recovery checks: focused feature/guidance plus unchanged R2 probes **41 passed**; affected selected-tier full fallback **6374 passed, 3 skipped in 109.48s**, 346 selected paths against `ede62bde` (`scratch/recovery-affected.log`). Whole-workspace lint-check, harness types, whole-worktree governance rules and offline wheel build passed. Initial type check found a fake Runs fixture typing mismatch; corrected by explicit typed fixture cast and rechecked successfully. Only tracked sync output remains `.devkit/installation.json` on Task 3. The controlled measurement above is refreshed on committed recovery runtime; its fixture and limits are identical between arms and it still makes no full-suite or aggregate-memory claim.


## Failed independent recovery round 3

Fresh independent R3 existing runtime/lifecycle/guidance tests passed36 and committed rules passed. Two new independent probes failed in `scratch/review-03/test_independent_recovery.py`: the pre-scan adopted/signalled unrelated reused leader PID200 after the original unobserved leader and orphan disappeared; retained terminal evidence without positive quiescence proof still authorized cleanup with a missed writer alive. Review03 records both as P1. The recovery stops for Host remedy without another fix round. Task2 is reopened; Living Spec reconciliation and final-report remain unfinished. Before/after support-role snapshot is identical `cfc2d2772215dc22479cb76138b33261cf552107`; reviewed HEAD205a6cd4 remained clean. Reviewer reported no outside-worktree source/document reads.

## Host terminal-guard recovery

Review round 3's exact two failure conditions were copied into feature-owned terminal-guard regressions and
failed before repair. The Host then moved the reaped-leader identity guard before discovery and signalling,
required explicit persisted positive quiescence before cleanup, and recorded valid no-process-started evidence
for prelaunch cancellation. Current liveness inspection remains separate from cleanup authorization.

The positive interrupted-cleanup fixture now carries current producer quiescence evidence; a retained terminal
without that proof is a separate refusal regression. This strengthens the cleanup prerequisite without weakening
interruption coverage. An older synthetic scratch probe lacking that prerequisite no longer represents an
eligible removal. Previous review records remain unchanged. Both unchanged round-3 probes and feature-owned
normal lifecycle, interruption and partial-retry scenarios pass after the fix.

The same pre-discovery identity gate now covers every established secondary process group as well as the direct child. A new regression first failed because cancellation signalled an unrelated reused secondary leader, then passed after the generic guard. Final focused runtime/lifecycle verification passes 47 cases including the two unchanged R3 probes; harness types and feature lint pass.

## Terminal-publication observation repair

Fresh independent round 4 confirmed the R3 ownership remedy and found a new P1 observer race outside that fix diff.
The reader could load running state, then miss the supervisor after its terminal publication, returning unknown.
A feature-owned deterministic regression covering absent/reused supervisors, valid/missing/mismatched/nonterminal
publication and retained cleanup first produced 4 failures and 4 passes. The named Runs.read location now reloads
and validates newly published terminal evidence before declaring unknown, exactly as the reviewer recommended.
Missing or nonterminal evidence remains unknown and mismatched identity remains unreadable; no interface changes.
The unchanged independent R4 probe and all owned runtime/lifecycle tests then pass 54 cases in 17.06 seconds.
Harness types and feature lint pass; the sole formatter blank-line requirement was applied before commit.
This nonrecurring batch meets all four minor-fix self-verification conditions: only the named implementation
location plus regression tests and evidence, concrete suggested action applied as written, no public contract
change, and deterministic Red-to-Green evidence. Rounds 1–4 remain retained without reset.

Before that observer-only repair, the complete selected-tier affected fallback passed 6386 tests with 3 skips
against ede62bde (347 paths, 139.54 seconds). Whole lint, 22 governance rules, harness types, generated artifacts
(2 checked, 0 stale) and offline wheel build passed on 1f0d9c6b. Final source and landed checks cover the repair.
