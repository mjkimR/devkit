---
id: FB-scope-history-ordering-intermittent
title: Scope history ordering assertion intermittently starts with an update event
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/tests/integration/features/scope/test_cli.py::test_two_worktrees_register_query_update_release_and_sweep
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-31
---

# [FB-scope-history-ordering-intermittent] Scope history ordering assertion intermittently starts with an update event

## 1. Friction / Question (friction, question)

- **Context**: Running the affected tests for `SPEC-steering-alias-autofix`, which changes document-reference repairs.
- **Expectation**: The scope CLI test's history events preserve register/update/sweep chronology.
- **Actual**: One affected run failed with an update event first; the same isolated test passed immediately afterward.
- **Workaround (or Interpretation Chosen)**: Run the isolated case and repeat the affected selector; preserve the failure as an intermittent observation.
- **Suggestion**: Reproduce event timestamp ordering at subsecond boundaries before deciding whether the query sort or the assertion needs repair. The cause is unverified.

## Diagnostic Details

- **Reproduction**: `just test-affected` failed once; the exact pytest node passed on the immediate isolated rerun.
- **Expected / Actual**: Expected register, update, update, sweep, sweep, sweep. Actual first event was update.
- **Versions**: Review head 5276e4a9 plus the glossary column fix; no scope implementation or test changes.
- **Conditions**: Affected selector used pytest-xdist with eight workers; frequency beyond this single failure is unknown.
- **Workarounds Attempted**: Isolated pytest rerun passed, 1 test in 0.32 seconds; the subsequent affected selector passed all 2140 tests.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/features/scope/repositories/localfs.py` sorts history events by their `at` value; causation has not been verified.

## Evidence

```text
just test-affected: 1 failed, 2139 passed in 20.44s
FAILED .../scope/test_cli.py::test_two_worktrees_register_query_update_release_and_sweep
AssertionError: At index 0 diff: 'update' != 'register'
isolated pytest node: 1 passed in 0.32s
subsequent just test-affected: 2140 passed in 18.06s
```

## Resolution

- **Disposition**: Resolved directly in a session bugfix (`packages/devkit-spec/src/devkit_spec/features/scope/repositories/localfs.py`).
  The cause was `LocalRegistry.history` re-sorting journal events by their wall-clock `at`: a backward system-clock
  step (macOS `timed` applies `settimeofday` steps, a -53 ms one was logged) between `register` and `update`, about
  100 ms apart in this test, stamps the later event earlier. `CAP-COLL-work-scope-registry` defines `query --history`
  in journal order, and appends are serialized under the namespace lock, so history now keeps the append order.
- **Verification**: A simulated 150 ms and 1 s backward step reproduced the recorded failure; 400 repeated runs under
  eight xdist workers without a step passed. `tests/integration/features/scope/test_cli.py::test_history_keeps_journal_order_when_the_wall_clock_steps_back`
  failed before the fix (`At index 0 diff: 'update' != 'register'`) and passes after it;
  `test_localfs.py::test_journal_appends_lines_and_reads_them_back_in_journal_order` now asserts append order.
  `just test-affected` passed 1563 tests.
