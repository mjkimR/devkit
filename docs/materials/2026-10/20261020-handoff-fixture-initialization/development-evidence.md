# Handoff initialization performance evidence

The implementation reuses a synchronized standalone repository before Planning worktree creation. Each case copies independent Git files and managed assets, then creates its own real Planning checkout, proposal, refinement and merge. No linked-worktree registrations are removed or repaired.

## Reproduction

From the repository root, run with the workspace interpreter:

```bash
.venv/bin/python docs/materials/2026-10/20261020-handoff-fixture-initialization/measure.py
```

The standard-library driver reads the baseline test source from Git, writes a temporary test module and pytest instrumentation plugin, uses the current checkout and pytest configuration for both sources, and checks the exact same twelve original parameterized cases pass in every run. The new isolation regression is excluded from timing and included in affected-test verification. The driver performs the local-socket preflight before pytest and preserves failures.

Baseline source revision: `475e8137e6f43656091203a207b48cabede864ba`. Python 3.12.3. Source hashes and complete samples are retained in `measurements.json`; the checkout head recorded there precedes the uncommitted implementation, so the source hash identifies the measured candidate.

## Samples

| Execution | Baseline seconds | Current seconds | Preparation sync calls, baseline/current |
| --- | ---: | ---: | ---: |
| Serial | 46.168 | 29.222 | 12 / 1 |
| Eight workers, baseline first | 17.939 | 14.620 | 12 / 8 |
| Eight workers, current first | 16.036 | 14.986 | 12 / 8 |

Eight-worker medians: 16.987 to 14.803 seconds, a 2.184-second (12.9%) reduction in this local sample.

All six executions passed twelve tests without skips. Serial initialization and preparation commits dropped from twelve to one; parallel runs performed eight independent initializations rather than twelve. Existing tested handoff operations and per-test proposal creation remain real.

## Verification and limits

- The full integration file passed all 21 cases under affected selection, including the new seed-isolation regression and existing native registration, stale-base, language and cancellation checks.
- The regression mutates copy refs, local Git config, tracked source and an ignored managed asset; verifies the seed remains unchanged; and verifies independent Git directories and the original two-worktree topology in the case.
- Times include pytest process startup and depend on host load, warm filesystem caches and worker scheduling. Serial is one sample per algorithm; parallel uses two samples in reversed order. No hardware-independent threshold or workspace-wide speedup is claimed.
- Module fixtures are worker-local. Reuse depends on multiple relevant cases reaching a worker; a worker executing one case still builds a template.
- Production code, affected-test selection and subprocess operations under test are unchanged. No persistent cache or snapshot-repair machinery is introduced.
