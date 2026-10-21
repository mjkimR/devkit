---
name: devkit-run
description: Read before running tests, linters or type checks outside a project recipe, reading devkit run output, or setting up such recipes.
---

# Running verification commands with `devkit run`

`uv run devkit run -- <command>` keeps the complete output in a log file and
prints the outcome, the tool's summary lines and warnings and, on failure, an
excerpt without progress and noise. Prefer it when you run a test runner,
linter or type checker yourself:

```bash
uv run devkit run -- uv run pytest tests/test_api.py -x
uv run devkit run -- npm run check
```

Run a recipe that already calls `devkit run` as it is; never wrap it twice.

## Reading the output

| Line | Meaning |
| --- | --- |
| `[RUN: "<command>" outcome=passed\|failed\|interrupted exit=<code> log=<path>]` | The result; `exit` is the command's own code. |
| `[RUN_SUMMARY: "..."]` | A summary line the tool printed (`3 passed in 0.5s`). |
| `[RUN_LAST_LINE: "..."]` | Passed without a recognized summary: the last output lines. |
| `[RUN_FAILURE: "<test>" kind=... message=...]` | A failed test the excerpt cuts out; rerun it by its node ID. |
| `[RUN_WARNING: "..." location=...]` | A warning the tool printed, once per message. |
| `[RUN_OMITTED: ...]` | Something did not fit the budget; it is in the log. |
| `[RUN_OUTPUT: shown=N omitted=N filtered=N]` | Failure only: the excerpt (head and tail) follows; `filtered` noise lines are only in the log. |

Advisory blocks of nested `devkit` commands come on stderr, whole.

Act on the excerpt first. Read the log at `log=` only when the excerpt is not
enough, and only the part you need: the excerpt's
`[... N characters omitted, log lines A-B ...]` line names what it left out
(`sed -n 'A,Bp' <log>`); otherwise search it (`rg -n "<test name>" <log>`). A
`[... previous line repeated N more times ...]` line stands for copies of the
line above it.

`devkit run` exits `0` when the command passed, `1` when it failed, `2` when it
could not be started (`RUN_COMMAND_NOT_STARTED`), and `128 + N` when signal `N`
interrupted it (`130` Ctrl-C, `143` SIGTERM; only the `[RUN]` line is printed).

## Setting up recipes

In a project that runs its checks through recipes (`just`, `make`, `npm`
scripts), put `devkit run` inside the recipe:

```just
test *args:
    uv run devkit run -- uv run pytest --tb=short {{args}}

lint:
    uv run devkit run -- uv run ruff check --output-format=concise .
```

Shorten the tools' own reports as above: `pytest --tb=short` prints the
failing line and `E` lines of each frame instead of the test source, and ruff's
concise format one line per finding. Keep the long forms when the project needs them.
