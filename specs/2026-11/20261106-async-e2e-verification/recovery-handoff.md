# Bounded-recovery handoff

The Development run stops on the recurring P1 in code-review round 2, as required by the high-effort review loop. No integration, push, merge, reset or rollback was performed. Source remains at repair commit `a9f236cc`; reviewed head is `37074d0d284288055931c856e755e876dd4f806d`. Review count is two; do not reset it. Tasks 2 and 3 are reopened. The agreed fifteen acceptance criteria and approved scope remain intact.

## Required runtime recovery

1. Read `envelopes/review-01.yaml`, `reverify-01.yaml` and `review-02.yaml`. Round 1 P1 regressions failed before repair; helper ownership and bounded public projection now pass, but the supervisor terminal gate still bypasses unresolved established groups.
2. Fix `packages/devkit/src/devkit_agt/features/isolated_execution/repositories/runtime.py` so every terminal record, including exception/cancellation paths, requires fresh post-exit group discovery and positively verified quiescence. The current pre-poll table/known-PID test can return before groups are observed empty. Final `live_owned` checks only persisted known PIDs and cannot discover the missed orphan. Preserve PID/reuse guards and default retention.
3. Keep failing supervisor-level probes: `scratch/review-02/test_recheck.py:87`, both passed/cancelled variants. The controlled process-list/poll sequence exposes PID 201 only after leader reap; current result contains only preparation PID 100. Do not substitute helper-only tests for this gate. Translate the regression into feature-owned tests and retain the Red output; real race frequency is unmeasured.
4. Fix `packages/devkit/src/devkit_agt/features/isolated_execution/services/lifecycle.py` to persist cleanup intent/progress atomically before removal effects. Interruption must leave an inspectable unfinished cleanup outcome, preserve the original command result and allow only safe revalidated remaining effects on explicit retry. The current round-02 probe at line 112 raises KeyboardInterrupt during remove and finds no cleanup evidence. Test interruption, later status and safe retry, including partial resource removal.
5. Preserve complete internal ownership evidence and the passing bounded status/wait/log projections, compact paginated list, escaped text sentinels and no-profile/no-local-cloud-selector interface.

## Required guidance refinement from the user

After the active review closed, the Host specified this refinement within the existing scope:

- In source `skills/spec-orchestrate/references/isolated-execution.md`, discover actual required verification commands and coverage from repository docs, scripts, runner configuration and CI before choosing groups.
- Never infer E2E existence, cost or independent runnability from directory labels alone.
- Split asynchronous execution only after independently runnable subsets are established without dropping any existing required coverage.
- With unseparated/unclear verification or no such subset, retain the existing required verification synchronously. Add no automatic restructuring, profile map or policy selector.
- Devkit's AGENTS just commands are this repository's local adoption example, not a universal tier assumption.
- Restate the conditional in `CAP-DLV-delivery-workflows` section 4.8, `UC-drive-development-to-integration`'s asynchronous section and `CAP-HARN-agent-guidance`. Add the corresponding focused source-guidance regression. Synchronize the source bundle through CLI; annotate and commit any additional tracked sync outputs.

## Verified evidence retained

- `just test-affected --base ede62bde -- --basetemp /private/tmp/devkit-async-affected-final-20261106`: full selected unit/integration fallback, 345 paths; **6367 passed, 3 skipped in 98.78s**. Verbose output: ignored `scratch/affected-final.log`. This passing suite does not override the independent failing process probes.
- Final focused runtime/output tests: **24 passed** (16 E2E, 8 unit). A combined interface/registration/parser run passed 95. Selector E2E passed 91. The newly discovered supervisor/cleanup probe conditions are not yet fixed.
- Whole `just lint-check` passed; whole workspace `just check` passed before review fixes, then final `just check devkit-agt` and targeted source/script types passed; whole-worktree rules and committed `--ci --base ede62bde` passed.
- `uv build --package devkit-agt --wheel --out-dir scratch/wheels --offline` passed. Wheel payload inspection confirms exec entry point, captured runtime and worktree checkout API.
- `devkit generated check`: checked=2, stale=0. `sync_start`: PASS exit=0. Tracked source-sync output: `.devkit/installation.json`, annotated on Task 3. A later sync repaired only ignored MCP registration projections and its immediate check passed.
- Controlled final measurement uses the same fixture SHA/argv/setup/environment in each arm; see `blocking-measurements.json`, `evidence/measure_blocking.py` and `verification.md`. Host-blocked medians 1.227s synchronous-disabled vs 0.343s async; command+observation 0.921s vs 0.930s; child CPU 0.486s vs 0.498s. This is not whole-suite acceleration or aggregate CPU/memory benefit.
- The first nested-scratch pytest basetemp was invalid because parent Git ignore discovery hid fixtures. Its state is retained; system fixture roots corrected the invocation. Do not rerun it.
- Initial authoring script `/private/tmp/devkit_exec_impl.py` was a disclosed scratch-location deviation; Host explicitly accepted retaining that one file. All later scratch/probes are ignored worktree paths or pytest-managed system fixtures. Never delete scratch artifacts.

## Remaining workflow

Host decides recovery within approved scope, without user approval or acceptance weakening. The actor that fixes the problem writes a `resolution` naming this run's worker envelope in the same fix commit, and preserves all review counts. Host-directed recovery gets the further fresh independent round specified by the review loop, named by its resolution. Then the implementer must complete Living Spec reflection and `reconcile.md`, derive/review entrypoints, run a fresh independent reconcile-reviewer (high effort), record `reconcile-check` at living-spec-draft, resolve spec status, sweep feedback and write final-change-report. None of those completion records exists yet.

Current docs are drafts and have not passed semantic reconcile verification. `PROP-test-playbook-verification-policy` still resolves as draft and remains Backlog; do not edit it. No explicit direct-fix source feedback was carried. Linux runtime execution remains unverified on this macOS host. Host-enforced descendant killing, application exit, reboot and intentional escape have no survival guarantee. Emulated host path checks are substitutes, not native confinement.


## Host-directed recovery round 3 handover

The Host-directed remedy is committed at `70064febe5ccec2719dea8220032f1450f588f6a` with `envelopes/resolution-01.yaml` naming worker-01. Its verification and refreshed measurement are committed at reviewed HEAD `205a6cd43264c45a9109a90f64a4cea871201264`. The unchanged R2 probes and feature-owned translations pass, but fresh independent code-review round 3 finds two new P1 ownership failures. `envelopes/review-03.yaml` holds both findings open. No further source fix or reviewer round was attempted. Task 2 is reopened; Task 3 guidance is implemented and its tests pass. The last accepted range base remains `90cf89872da19e0722429f643c3d2535c465a6e4`; retain all three review rounds and both workers.

1. `scratch/review-03/test_independent_recovery.py:55` demonstrates an unobserved original leader 200, observed orphan 201/group 200, then unrelated reused leader/group 200 before an empty scan. The pre-scan discovery adopts it before the post-exit guard; cancellation signals unrelated PID 200. Reject such a reappearing direct-leader PID before every post-reap discovery/signalling step when original identity is missing; retain unknown state and add the supervisor-level regression.
2. The same independent file at line 76 demonstrates cleanup of retained terminal evidence from the preceding captured runtime with no positive quiescence proof and only preparation history, while a missed same-group writer remains alive. Require explicit persisted positive proof before removal; missing/incomplete proof must refuse while preserving the original outcome. Record valid no-launch/no-group completion explicitly; add retained-record regressions.

Recovery verification: focused implementation tests plus unchanged R2 probes 41 passed; independent R3 existing runtime/lifecycle/guidance 36 passed; required affected unit/integration full fallback 6374 passed, 3 skipped in 109.48s across 346 paths; whole lint, harness types, whole-worktree and independent committed rules passed; offline harness wheel passed; generated checked2 stale0 and sync check passed. These passes do not override the two failed independent R3 probes. Linux runtime and real PID-reuse race frequency remain unmeasured.

The controlled warmup+three-samples-per-arm measurement was refreshed on runtime70064f, same fixture SHA/argv/setup/limits in both arms: Host-blocked medians1.162s synchronous-disabled versus0.238s asynchronous; command+observation0.869s versus0.874s; CPU0.485s versus0.498s. Evidence remains `blocking-measurements.json` and `verification.md`; no whole-suite or aggregate-memory benefit is claimed.

Guidance discovery/overlap/exclusion/conditional fallback is implemented consistently in source and CAP-DLV/CAP-HARN/UC reflection; its walkthrough is in verification.md. The only tracked sync output remains `.devkit/installation.json`, annotated on Task3. No new dependency/edge/policy was added. All scratch remains in place.

After Host chooses the next remedy, the implementer must still finish Living Spec reflection for explicit post-exit proof and durable cleanup states, create reconcile.md with all9 approved changed docs, run spec-entrypoints derivation/review, fresh independent high reconcile review1, resolve spec/reconcile, sweep feedback and write final-report. No reconcile-check, feedback or final-report is claimed by this failed recovery. Do not integrate the range with open P1s.
