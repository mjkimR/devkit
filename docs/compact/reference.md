# devkit.compact

Compact command output for agents (`devkit run`): a command runs with its complete output in a log file, and the caller gets a bounded view of it. Semantics, budgets and recognized formats: [Compact Command Output Overview](overview.md).

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
[RUN_FAILURE: "tests/test_api.py::test_login[admin]" kind=failed message="AssertionError: assert 401 == 200"]
[RUN_WARNING: "DeprecationWarning: old API" location=tests/test_x.py:12]
[RUN_OMITTED: summaries=0 failures=0 warnings=4 advisories=0 output=12345]
[RUN_OUTPUT: shown=8000 omitted=12345 filtered=17]
<first 3,000 characters>
[... 12345 characters omitted, log lines 41-212 ...]
<last 5,000 characters>
```

`[RUN_LAST_LINE]` lines replace summaries only when the command passed without a recognized one; `[RUN_FAILURE]` lines (failed tests the excerpt cuts out), `[RUN_OUTPUT]` and the excerpt appear only when it failed; `[RUN_OMITTED]` only when a budget was exceeded. A run interrupted by Ctrl-C, `SIGTERM` or `SIGHUP` stops the command's process group and prints only `[RUN: ... outcome=interrupted exit=<code> log=<path>]`; the log shows where the command stopped. Each omission marker names the log lines it left out (`sed -n '41,212p' <log>` reads them), and a `[... previous line repeated N more times, log lines A-B ...]` line stands for identical lines in a row. `filtered=` counts the progress, noise and repeated lines filtered out of the excerpt; the log keeps them. In text mode stderr carries the relayed advisory blocks of nested `devkit` commands (warnings and notices, then the runner's notices, then errors); under `--format json` they are only in `advisories` and stderr stays empty. JSON keys: `command`, `outcome`, `exit_code`, `log`, `summaries`, `last_lines`, `failures`, `warnings`, `advisories`, `omitted`, `output`, `filtered`, `notices`. Line formats, budgets and filters: [Overview, sections 4 and 5](overview.md#4-the-bounded-view). For shorter reports, set the tools' own options in the recipe: `pytest --tb=short`, `ruff check --output-format=concise`.

Logs: `<tmp>/devkit-run-<uid>/<project hash>/` (both levels private to the user, `0700`), the 20 newest per project. The view covers what the command wrote until it exited; processes it leaves running keep running and append to the log.

## Exit and error codes

`0` the command succeeded; `1` it failed (its own code is `exit=`, `128 + N` for signal `N`); `2` it could not be started, the log cannot be written or the arguments are invalid; `128 + N` the run was interrupted by signal `N` (`130` for Ctrl-C, `143` for `SIGTERM`). Codes carry the `RUN_` prefix of the command agents call, not the module name.

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `RUN_COMMAND_NOT_STARTED` | `ERROR` (`INPUT_ERROR`, exit `2`) | `CommandNotStartedError` | The command does not exist or is not executable, or the working directory does not exist (also when the shell's current directory was removed) or cannot be entered; `[TARGET]` names the command or the directory. |
| `RUN_LOG_DIR_INVALID` | `ERROR` (`INTERACTION`, exit `2`) | `LogDirectoryError` | The per-user log directory or the project's directory in it is a symlink, not a directory, or belongs to another user, or the log cannot be created there (no permission, disk full). |
| `RUN_SLOW_COMMAND` | `NOTICE` | `SlowCommandNotice` | The command ran at least `--slow-after` seconds. |
| `ARGUMENT_INVALID` | `ERROR` (exit `2`) | `devkit.core.ArgumentError` | `--slow-after` is negative or not finite. |

## Library

```python
from devkit.compact import run_command

run = run_command(["uv", "run", "pytest"], slow_after=0)
run.passed, run.exit_code, run.log
run.scan.summaries, run.scan.last_lines, run.scan.failures, run.scan.warnings, run.scan.advisories, run.scan.output, run.scan.omitted
```

`run_command(argv, *, cwd=None, env=None, slow_after=60.0, notices=True, log_dir=None)` never prints and raises `CommandNotStartedError`, `LogDirectoryError` when the log cannot be written, or `CommandInterrupted` (a `SystemExit` with code `128 + N`; `.run` is the interrupted `CommandRun`) after stopping the command's group on Ctrl-C, `SIGTERM` or `SIGHUP`; `scan(stream, *, notices=True, base=())` reads any text stream into a `Scan`, showing warning locations under a `base` directory relative to it. Fields: [Overview, Library](overview.md#6-library).

## Agent guidance

The `devkit` guide bundle (selected by default) carries the instruction `devkit-run`: when to use `devkit run`, how to read its output and log, and how to put it inside a project's recipes. Agents find it through `devkit get-context devkit`; by default it adds nothing to `AGENTS.md`. The opt-in preset `devkit:run` (`devkit add devkit:run`) adds one `AGENTS.md` line pointing at `devkit run` and this instruction ([Overview, section 6](overview.md#6-library)). Its source is `src/devkit/distribution/guide/bundle/instructions/devkit-run.md`; keep it in step with this reference.

## Module map

| File | Contents |
| --- | --- |
| `scan.py` | `scan`, `Scan`, `ToolWarning`, `RelayedAdvisory`, `Omitted`, budgets and recognized formats |
| `execute.py` | `run_command`, `CommandRun`, `CommandInterrupted`, `default_log_dir`, `log_root`, log retention, process group and signal handling |
| `errors.py` | `CompactError`, `CommandNotStartedError`, `LogDirectoryError`, `SlowCommandNotice` |
| `cli.py` | `devkit run` |
