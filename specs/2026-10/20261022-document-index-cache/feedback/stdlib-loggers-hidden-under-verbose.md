---
id: FB-stdlib-loggers-hidden-under-verbose
title: Modules logging outside the devkit logger never show under -v
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-spec/src/devkit_spec/features/proposals/usecases/binding.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-stdlib-loggers-hidden-under-verbose] Modules logging outside the devkit logger never show under -v

## 1. Friction / Question (friction, question)

- **Context**: Adding the parse memo's diagnostic lines to devkit-spec, which must be visible under `-v` only.
- **Expectation**: `devkit_core.core.logs` says every devkit module takes its logger from `get_logger`, and the CLI
  boundary prints the records of the `devkit` logger as `[INFO]` lines under `--verbose`.
- **Actual**: A logger made with `logging.getLogger(__name__)` is named `devkit_spec...`, outside the `devkit`
  hierarchy, so its records never reach the `-v` handler. The memo's first draft did this and its `-v` test failed.
  Four modules still do it: `devkit_spec.features.proposals.usecases.binding` and `.specs`, and
  `devkit_dist.features.distribution.services.installation.transaction` and `.usecases.status`; their `_log.info`
  diagnostics are invisible under `-v`.
- **Workaround (or Interpretation Chosen)**: The memo uses `get_logger(__name__)`.
- **Suggestion**: Switch the four modules to `get_logger(__name__)` and add a check (a `devkit-dev` rule or a test)
  that refuses `logging.getLogger(__name__)` in workspace packages.

## Diagnostic Details

- **Reproduction**: Call a command that reaches `binding.py`'s `_log.info` with `-v`; no `[INFO]` line appears.
  Reproduced for the memo module before the fix, not for the four modules.
- **Expected / Actual**: Expected an `[INFO]` line under `-v`; observed none.
- **Versions**: worktree `dev-document-index-cache`, Python 3.12.8.
- **Conditions**: Any devkit CLI command with `-v`.
- **Workarounds Attempted**: `get_logger(__name__)` in the new module; the `-v` test then passed.
- **Related Assets**: `devkit_core.core.logs.get_logger`, `devkit_cli.boundary.Boundary._logs_on_stderr`,
  `ARCH-08-1-agent-output`.

## Evidence

```text
devkit_core/core/logs.py: "Every devkit module takes its logger from get_logger"
rg "logging.getLogger(__name__)" packages/*/src:
  devkit_spec/features/proposals/usecases/binding.py:19
  devkit_spec/features/proposals/usecases/specs.py:57
  devkit_dist/features/distribution/services/installation/transaction.py:38
  devkit_dist/features/distribution/usecases/status.py:74
test_a_discarded_memo_is_logged_only_under_verbose: failed with logging.getLogger, passed with get_logger
```
