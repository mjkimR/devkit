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
