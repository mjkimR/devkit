# Development verification evidence

## Comparable blocking experiment

Same fixture commit, argv, setup, isolated environment, machine and resource limits. Async disabled by waiting for the exact same supervisor process inside its launch Popen wrapper; one warmup then three samples per arm. 0.9s independent-work fixture follows launch in each arm. Timing includes process observation; not whole-suite speedup evidence.

Fixture commit: `cdad427ec2256291c415f1f220882639e37a4f2c`; platform macOS. The fixture runs a standard-library native command sleeping 0.8 seconds and checking one committed input; each arm then performs the same 0.9-second independent-work fixture. Both arms use identical detached-checkout preparation and cleanup. This measures caller blocking, not suite acceleration or a comparison against current-directory commands. No network/service resources are used.

| Mode | Launch return median s | Host blocked median s | Preparation median s | Native + observation median s | Child CPU median s | Child peak RSS median MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| synchronous-disabled-async | 1.094 | 1.241 | 0.091 | 0.923 | 0.484 | 16.23 |
| asynchronous | 0.057 | 0.313 | 0.088 | 0.910 | 0.497 | 15.73 |

Both arms pay detached checkout/runtime/evidence storage and supervisor/process-observation CPU cost. Asynchrony overlaps that work with the caller and adds no claim of lower test CPU or full-suite latency. RSS covers reaped children, not aggregate concurrent peak memory. The native command plus observation has similar duration; the latch regression separately proves ordering before release. The baseline is the same head implementation with asynchronous launch disabled, not a checkout of the base.

## Reproduction

The retained harness is `evidence/measure_blocking.py`; run it from the Development worktree with `uv run --no-active python <unit>/evidence/measure_blocking.py` using a fresh ignored `scratch/blocking-consumer` path. The original ignored fixture and its evidence remain in this worktree. `blocking-measurements.json` holds warmups, all samples, runtime IDs and resource measurements.

## Focused verification

- Selector E2E: 91 passed, including edited/explicit E2E, broad mixed directories, shared/unknown full fallback, embedded rule tests, compatibility and empty-tier no-op.
- Execution: 14 subprocess lifecycle probes plus 2 process-identity unit tests passed. Includes fixed SHA/environment, latch ordering, native shell/build argv, setup/locked-sync failure, default retention, parent-return discovery, missing/reused supervisor, interrupted waiter/supervisor, nested session and actual compact cancellation, surviving child, dirty/unrelated/active/unknown refusal and concurrent/idempotent cleanup.
- Guidance/registration: 27 passed; moved-target/doc-code checks: 12 passed.
- Full affected unit/integration fallback, lint/types and governance results are recorded by the final review and worker envelopes after completion.

## Limits and boundary evidence

Linux code paths are designed and statically checked but not executed on this macOS host. Host descendant-kill policies, host application exit, reboot survival and intentional process escape are outside the contract. No OS containment guarantee is claimed. External service/data isolation remains project responsibility.

Host projection is emulated: all commands use the absolute named worktree as cwd; Git uses git -C; sibling writes and shared Git effects are individually escalated and reviewers receive absolute read/probe scopes. These measures are not native path confinement. The first authoring scratch script was mistakenly written to `/private/tmp/devkit_exec_impl.py`; the Host explicitly accepted retention of that one artifact and all later scratch stays under the ignored worktree scratch directory. No deletion or alternate write route was used.
