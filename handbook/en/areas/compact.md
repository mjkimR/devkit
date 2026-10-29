---
sources:
  ARCH-08-1-agent-output: 6b76bd19787465ed1e7ec7aee1904077cc75042c
  CAP-ADV-agent-advisory-protocol: 572af49f008a71f993b3b82c2d457b7610529192
  CAP-CMP-bounded-execution: 46503e105fa4406f7dd9f90878ce99bef82ac7d8
title: Compact command output
---

# Compact command output

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Test runners, linters and type checkers print for people: progress dots, passing test names, timing tables and
colour. An agent that runs them directly receives all of it, and when the output is long its host cuts it at an
arbitrary point, often losing the failure. `devkit run` fixes that: it runs one command with its complete output in
a log file and prints a bounded view of what matters. See [Concepts](../concepts.md) for why devkit budgets an
agent's context this carefully.

## Run a command through it

```sh
devkit run -- just test
devkit run -- uv run pytest tests/unit/test_scan.py -k timeout
devkit run --format json -- npm run lint
```

Options go before the command; everything from the command on is passed through unchanged. The command runs in the
current directory with stdin closed, so a command waiting for input ends instead of hanging the agent. To run
several commands, wrap a recipe that chains them (`devkit run -- just lint`); the runner wraps, it does not plan.

## Read the result

```text
[RUN: "just test" outcome=failed exit=1 log=/tmp/devkit-run-501/<project>/20261026-101500-just-ab12.log]
[RUN_SUMMARY: "3 failed, 412 passed in 21.4s"]
[RUN_FAILURE: "tests/unit/test_x.py::test_y" kind=failed message=-]
[RUN_WARNING: "DeprecationWarning: ..." location=tests/test_x.py:12]
[RUN_OMITTED: summaries=0 failures=0 warnings=2 advisories=0 output=0]
[RUN_OUTPUT: shown=8000 omitted=31250 filtered=840]
<excerpt>
```

- `[RUN]` gives the outcome, the command's own exit code and the log path.
- `[RUN_SUMMARY]` lines are the result lines the tool printed (pytest, ruff, mypy, Pyright, tsc, Jest, Vitest,
  Playwright, cargo, ESLint, Prettier, coverage totals and `devkit rules` summaries are recognized). A command that
  passed without a recognized summary shows its last lines instead (`[RUN_LAST_LINE]`).
- On failure only, `[RUN_FAILURE]` names failed pytest tests the excerpt cut out, so you can rerun them by node ID,
  and the excerpt shows the head and tail of the output with progress and noise filtered.
- `[RUN_OMITTED]` counts whatever did not fit; nothing is dropped silently. Every omission marker in the excerpt
  names the log lines it stands for, so `sed -n 'A,Bp' <log>` shows exactly what was left out.

Advisory blocks printed by nested `devkit` commands are lifted out whole and relayed on stderr, errors last, so the
decisive `[ACTION]` survives even when the surrounding output is cut ([Advisories](advisory.md)).

## Exit codes

The runner exits `0` when the command passed and `1` when it failed; the command's own code is in `exit=`, so a
tool's `2` is never mistaken for the runner's. The runner exits `2` only when it could not start the command
(`RUN_COMMAND_NOT_STARTED`), write its log (`RUN_LOG_DIR_INVALID`) or parse its own arguments.

Interrupting the run (Ctrl-C, or the agent host's timeout signal) stops the command's whole process group, prints
only the `[RUN]` line with `outcome=interrupted` and exits `128 + N`. No test or build process outlives the run.

## Logs

Logs live outside the work tree, under a per-user, per-project directory in the system temporary directory (created
`0700`). Each run writes one file and the 20 newest per project are kept. The log is the full record: read it with
`rg` or `sed` when the view is not enough.

## Make the view smaller

The largest remaining part of a failure is usually the tool's own report, which only the tool can shorten
reliably. In your recipes, use `pytest --tb=short` and `ruff check --output-format=concise`; the `devkit-run`
instruction recommends both. A command that runs longer than `--slow-after` seconds (default `60`, `0` turns it off)
adds a `RUN_SLOW_COMMAND` notice suggesting a narrower run.

## Where agents learn it

`devkit run` ships with `devkit-agt`; the auto-selected `harness` bundle's `devkit-run` instruction teaches agents to
use it and to put it inside your verification recipes. If your agents often run narrowed commands outside the
recipes, select the opt-in preset with `devkit add harness:run`, which adds one short `AGENTS.md` line pointing at
the runner.

Gates and workflow checks reuse the same runner: the `verify-commands` commit gate runs every command through it
and puts only the bounded view in its refusal ([Commit gates](gate.md)), and `devkit generated` reports a failed
regeneration command the same way ([Generated Files](generated.md)). Library callers use
`devkit_agt.features.compact.run_command`, which never prints and returns a `CommandRun`; its `failure_details` are
the advisory detail lines both of those reuse.

## Sources

- [CAP-CMP-bounded-execution](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/compact/CAP-CMP-bounded-execution.md):
  execution, logs, the bounded view and its budgets, output and the library.
- [Compact reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/compact.md): usage,
  error codes and module map.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md):
  the output contract `devkit run` shares with every command.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  the advisory grammar the runner recognizes.
