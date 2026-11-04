---
id: FB-rules-test-runs-stale-deployed-copy
title: devkit rules test runs the deployed copy, which lags the bundle source until devkit sync
scope: repo
kind: suggestion
category: docs-mismatch
target: devkit rules test
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-04
---

# [FB-rules-test-runs-stale-deployed-copy] devkit rules test runs the deployed copy, which lags the bundle source until devkit sync

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: after editing a rule's tests under the bundle source
  (`packages/<pkg>/src/.../bundles/<bundle>/bundle/rules/<name>/tests/test_rule.py`), `uv run devkit rules test
  RULE-<id>` runs `.devkit/managed/<bundle>/rules/<name>/tests`, the copy `devkit sync` deployed earlier. Until a
  `devkit sync` runs, the command tests the old fixtures against the new implementation and reports failures (or
  passes) that do not describe the source; nothing in its output says the deployed copy differs from the source.
  The repository's `pytest` on the source path and `just test-affected` run the current tests.
- **Proposed Procedure**: have `devkit rules test` compare the deployed rule folder with its bundle source when the
  bundle is a repository-owned producer and print a notice (`RULE_TEST_DEPLOYED_STALE`, with the `devkit sync` fix)
  before running; or state in the spec verification guidance that a bundle test edit needs `devkit sync` before
  `devkit rules test`.
- **Expected Benefit**: no misleading failure after editing a rule's tests; one fewer guessed step for an agent that
  follows a task's `devkit rules test` verification line.
- **Cost & Risk**: one directory comparison per run; none for consumers whose deployed copy is the only copy.
- **Attempted**: observed in this session (two misleading runs before `devkit sync`); the notice is a hypothesis.

## Diagnostic Details

- **Reproduction**: edit a bundle rule's `tests/test_rule.py`, run `uv run devkit rules test RULE-<id>` without
  `devkit sync`.
- **Expected / Actual**: expected the edited tests; observed the earlier deployed tests (`collected 3 items` where the
  source held 9).
- **Versions**: the repository at the Development base commit (main, 2026-11-04).
- **Conditions**: a producer repository whose own bundle is installed through `.devkit/managed/`.
- **Workarounds Attempted**: `devkit sync`, then the command tests the source copy; succeeded.
- **Related Assets**: `devkit rules test`, `devkit sync`, `CAP-GOV-spec-rules` section 4 (rule tests deploy with the
  rule).

## Evidence

```text
$ uv run devkit rules test RULE-ux-coverage     # after editing the bundle source tests, before devkit sync
[RULE_TEST: RULE-ux-coverage tests=.devkit/managed/docs/rules/ux_coverage/tests result=failed exit=1 ...]
collected 3 items                                 # the source file held 9 tests
$ uv run devkit sync
[CHANGE: update .devkit/managed/docs/rules/ux_coverage/tests/test_rule.py]
```

- **Disposition**: `AGENTS.md` Verification table: a row says to run `devkit sync` before `devkit rules test` after editing a bundle rule's tests, since the command runs the deployed copy; direct fix, verified by reading the table.
