---
name: devkit-run
description: Read before running tests, linters or type checks directly, outside a project recipe or script, or before setting up such recipes. Covers devkit run, how to read its bounded output and full log, its exit codes, and wrapping recipes with it.
---

# Running verification commands with `devkit run`

`uv run devkit run -- <command>` runs a command with its complete output in a log
file and prints only what an agent needs: the outcome, the summary lines the tool
printed, its warnings and, when it failed, an excerpt of the output without
progress and noise. Prefer it when you run a test runner, linter or type checker
yourself:

```bash
uv run devkit run -- uv run pytest tests/test_api.py -x
uv run devkit run -- npm run check
```

When the project's recipe already wraps the command (a `just` recipe that calls
`devkit run`), run the recipe as it is; do not wrap it a second time.

## Reading the output

| Line | Meaning |
| --- | --- |
| `[RUN: "<command>" outcome=passed\|failed exit=<code> log=<path>]` | The result; `exit` is the command's own code. |
| `[RUN_SUMMARY: "..."]` | A summary line the tool printed (`3 passed in 0.5s`). |
| `[RUN_LAST_LINE: "..."]` | Passed without a recognized summary: the last lines of the output, usually the tool's verdict. |
| `[RUN_FAILURE: "<test>" kind=... message=...]` | Failure only: a failed test the excerpt cuts out; rerun it by its node ID. |
| `[RUN_WARNING: "..." location=...]` | A warning the tool printed, once per message. |
| `[RUN_OMITTED: ...]` | Something did not fit the budget; it is in the log. |
| `[RUN_OUTPUT: shown=N omitted=N filtered=N]` | Failure only: the excerpt follows, head and tail of the output; `filtered` lines of progress and noise are only in the log. |

Advisory blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`) from nested `devkit` commands
come on stderr, whole; follow their `[ACTION]` as usual.

Act on the excerpt first. Read the log at `log=` only when the excerpt is not
enough, and read the part you need, not the whole file: the excerpt's
`[... N characters omitted, log lines A-B ...]` line names what it left out
(`sed -n 'A,Bp' <log>`); otherwise search it (`rg -n "<test name>" <log>`). A
`[... previous line repeated N more times ...]` line stands for copies of the
line above it.

`devkit run` exits `0` when the command passed, `1` when it failed, and `2` when
the command could not be started (`RUN_COMMAND_NOT_STARTED`: `[TARGET]` names
the command that does not exist, or the working directory that cannot be
entered).

## Setting up recipes

In a project that runs its checks through recipes (`just`, `make`, `npm`
scripts), put `devkit run` inside the recipe, so agents and people get the same
compact output without remembering it:

```just
test *args:
    uv run devkit run -- uv run pytest --tb=short {{args}}

lint:
    uv run devkit run -- uv run ruff check --output-format=concise .
```

Shorten the tools' own reports with their options, as above: `pytest
--tb=short` prints the failing line and the `E` lines of each frame instead of
the whole test source, and ruff's concise format prints one line per finding
instead of a code frame. Keep the long forms when the project needs them.
