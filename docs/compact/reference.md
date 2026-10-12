# devkit.compact

Compact command output for agents (`devkit run`), part of the `devkit` distribution. A command runs with its complete output in a log file; the caller gets its outcome, recognized summaries (or, when a command passed without one, its last lines) and warnings, the advisory blocks of nested `devkit` commands and, on failure, a head-and-tail excerpt, each within a fixed budget.

Architecture and design rationale: [Compact Command Output Overview](overview.md).

## Usage

```bash
uv run devkit run -- just test
uv run devkit run -- uv run pytest packages/devkit/tests/compact -x
uv run devkit run --format json -- npm run check
uv run devkit run -q --slow-after 120 -- just lint-check
```

Options go before the command; everything from the command on is passed to it unchanged, so `--` is optional but makes the boundary explicit. The command runs in the current directory.

| Option | Effect |
| --- | --- |
| `--slow-after SECONDS` | Add a `RUN_SLOW_COMMAND` notice when the command runs this long (default `60`; `0` turns it off). |
| `--format text\|json` | Text sentinel lines (default) or one JSON object. |
| `-q`, `-v`, `--strict` | The shared output options; they also reach the command as `DEVKIT_QUIET`, `DEVKIT_VERBOSE`, `DEVKIT_STRICT`. Under `--strict` a relayed `[WARN]` block makes a passing run exit `1`. |

## Output

```text
[RUN: "just test" outcome=failed exit=1 log=/tmp/devkit-run-501/1a2b3c4d5e6f/20261012-183000-just-test-x1y2.log]
[RUN_SUMMARY: "2 failed, 410 passed in 3.1s"]
[RUN_WARNING: "DeprecationWarning: old API" location=tests/test_x.py:12]
[RUN_FAILURE: "tests/test_api.py::test_login[admin]" kind=failed message="AssertionError: assert 401 == 200"]
[RUN_OMITTED: summaries=0 failures=0 warnings=4 advisories=0 output=12345]
[RUN_OUTPUT: shown=8000 omitted=12345 filtered=17]
<first 3,000 characters>
[... 12345 characters omitted, log lines 41-212 ...]
<last 5,000 characters>
```

`[RUN_OMITTED]` appears only when a budget was exceeded (the excerpt's only when it is shown), `[RUN_OUTPUT]` and the excerpt only when the command failed. The omission marker names the log lines it left out (`sed -n '41,212p' <log>` reads them). A command that passed without a recognized summary gets `[RUN_LAST_LINE: "..."]` lines instead: the last non-blank lines of its filtered output, at most 5 and 500 characters. A command that failed gets `[RUN_FAILURE: ...]` lines for the failed tests pytest names (`FAILED`/`ERROR` lines) that the excerpt cuts out, within 2,000 characters, so excerpt and failures together name every failed test or count it in `failures=`. Identical lines in a row collapse into the first and a `[... previous line repeated N more times, log lines A-B ...]` line. Under `-v`, an `[INFO]` line gives the size of the view against the output. The excerpt filters out progress (pytest's dots and `PASSED` lines, `✓` lines, overwritten progress bar states), noise (pytest's session header, uv's success messages), pytest's warnings summary (its warnings are `[RUN_WARNING]` lines) and repeated blank lines, counted in `filtered=`; the log keeps them. Warning locations under the working directory are relative to it. For shorter reports, set the tools' own options in the recipe: `pytest --tb=short`, `ruff check --output-format=concise`. stderr carries the advisory blocks of nested `devkit` commands (warnings and notices, then the runner's notices, then errors). JSON keys: `command`, `outcome`, `exit_code`, `log`, `summaries`, `last_lines`, `failures`, `warnings`, `advisories`, `omitted`, `output`, `filtered`, `notices`. Budgets, recognized formats and ordering: [Overview, sections 4 and 5](overview.md#4-the-bounded-view).

Logs: `<tmp>/devkit-run-<uid>/<project hash>/` (the first level private to the user, `0700`), the 20 newest per project.

Exit codes: `0` the command succeeded; `1` it failed (its own code is `exit=`, `128 + N` for signal `N`); `2` it could not be started or the arguments are invalid.

| Code | Level | Condition |
| --- | --- | --- |
| `RUN_COMMAND_NOT_STARTED` | `ERROR` (`INPUT_ERROR`) | The command does not exist or is not executable, or the working directory does not exist or cannot be entered; `[TARGET]` names which. |
| `RUN_LOG_DIR_INVALID` | `ERROR` (`INTERACTION`) | The per-user log directory is a symlink, another user's, or cannot be created. |
| `RUN_SLOW_COMMAND` | `NOTICE` | The command ran at least `--slow-after` seconds. |

## Library

```python
from devkit.compact import run_command

run = run_command(["uv", "run", "pytest"], slow_after=0)
run.passed, run.exit_code, run.log
run.scan.summaries, run.scan.last_lines, run.scan.failures, run.scan.warnings, run.scan.advisories, run.scan.output, run.scan.omitted
```

`run_command(argv, *, cwd=None, env=None, slow_after=60.0, notices=True, log_dir=None)` never prints and raises `CommandNotStartedError`; `scan(stream, *, notices=True)` reads any text stream into a `Scan`.

## Agent guidance

The `devkit` guide bundle (selected by default) carries the instruction `devkit-run`: when to use `devkit run`, how to read its output and log, and how to put it inside a project's recipes (`just`, `make`, `npm` scripts). Agents find it through `devkit get-context devkit`; it adds nothing to `AGENTS.md`. Its source is `src/devkit/distribution/guide/bundle/instructions/devkit-run.md`; keep it in step with this reference.

## Module map

| File | Contents |
| --- | --- |
| `scan.py` | `scan`, `Scan`, `ToolWarning`, `RelayedAdvisory`, `Omitted`, budgets and recognized formats |
| `execute.py` | `run_command`, `CommandRun`, `default_log_dir`, `log_root`, log retention, process group and signal handling |
| `errors.py` | `CompactError`, `CommandNotStartedError`, `LogDirectoryError`, `SlowCommandNotice` |
| `cli.py` | `devkit run` |
