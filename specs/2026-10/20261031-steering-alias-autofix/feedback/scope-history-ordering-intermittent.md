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
status: open
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
