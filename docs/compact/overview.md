# Compact Command Output: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit.compact` (`devkit run` CLI)  
**Related Documents**:
- [Compact Reference](reference.md)
- [Agent-First Output](../architecture/agent-output.md)
- [Agent Advisory Protocol](../advisory/protocol.md)

---

## 1. Overview and Objectives

Test runners, linters and type checkers print for people: progress dots, passed test names, timing tables, colour. An agent that runs them directly receives all of it in its context window, and when the output is long the agent host cuts it at an arbitrary point, often losing the part that matters.

`devkit run -- <command>` runs the command with its complete output in a log file and prints a bounded view of it instead: the outcome, the summary lines the tool printed, its warnings, the advisory blocks of nested `devkit` commands and, only when the command failed, a head-and-tail excerpt with progress and noise filtered out. The full log is always one path away.

### Principles

1. **The log is complete, the view is bounded.** Everything the command wrote goes to the log; every part of the view has a fixed budget. What does not fit is counted (`[RUN_OMITTED]`), never silently dropped.
2. **Match output, not commands.** Summaries and warnings are recognized by the lines a tool prints, so `just`, `npm run`, `uv run` and shell wrappers work without configuration. No result is inferred from progress output.
3. **Progress and noise are not output.** Lines that only report progress or a passing item, the states a progress bar overwrote, lines that carry nothing an agent acts on, and sections that repeat what the view already reports are filtered out of the excerpt: they do not help an agent find a failure, and they push the lines that do out of the budget. A line that names a failure is never filtered. The runner filters only what is safe without understanding a tool's structure; shortening a tool's own reports (tracebacks, code frames) is the tool's option to set, not the runner's (section 5).
4. **Directives survive.** An advisory block a nested `devkit` command prints is taken out whole and relayed on stderr, so its `[ACTION]` reaches the agent even when the output around it is cut.
5. **The runner wraps, it does not plan.** It runs one command as given. Which commands verify a project stays with the project (`justfile`, `package.json` scripts).
6. **Same contract as every devkit command.** Result lines on stdout, advisories on stderr, `0`/`1`/`2` exit codes and the shared output options ([Agent-First Output](../architecture/agent-output.md)).

---

## 2. Execution

`devkit.compact.run_command` runs the command in the current directory:

- stdout and stderr go to one log file, in the order they were written;
- stdin is closed (`/dev/null`), so a command that waits for input ends instead of hanging the agent;
- the command runs in a session and process group of its own. When the runner is interrupted (Ctrl-C) or terminated (`SIGTERM`, `SIGHUP`, as an agent host does on a timeout), it stops the whole group (`SIGTERM`, then `SIGKILL` after 5 seconds) before the signal propagates, so no test or build process outlives the run;
- the runner's output options reach the command as `DEVKIT_QUIET`, `DEVKIT_VERBOSE` and `DEVKIT_STRICT`, each `1` or `0` from the resolved settings, so nested `devkit` commands apply the same options (and a flag on the runner wins over the environment there too);
- the command's exit code is reported as is; a command ended by signal `N` reports `128 + N`.

The runner itself exits `0` when the command succeeded, `1` when it failed, and `2` when it could not be started (`RUN_COMMAND_NOT_STARTED`) or its own arguments are invalid. The command's own code is the `exit=` field of the `[RUN]` line, so a command's `2` (pytest's usage error, for one) is never mistaken for the runner's.

---

## 3. Logs

Logs live outside the work tree, under `<tmp>/devkit-run/<project>/`, where `<tmp>` is the system temporary directory and `<project>` a hash of the devkit project root containing the current directory (the root `devkit` commands resolve by default). Each run writes `<YYYYMMDD-HHMMSS>-<command>-<random>.log`; the 20 newest logs of a project are kept and older ones are deleted when a new run starts. The scan reads the log back through the file the command wrote, so a concurrent run that prunes it first does not lose this run's view.

---

## 4. The Bounded View

One pass over the log (`devkit.compact.scan`) produces every part of the view. Each line is first reduced to what a terminal would show: ANSI escape sequences are removed, and a carriage return starts the line over, so a progress bar leaves only its last non-blank state. Only the last 64,000 characters of a line are kept (its first 1,000 as well, for recognition); a line longer than 1,000 characters is recognized by its start only.

| Part | Content | Budget |
| --- | --- | --- |
| Summaries | Lines that match a known summary format exactly (below) | 2,000 characters |
| Warnings | One-line warnings with the first location they name, each message once, cut at 500 characters | 2,000 characters |
| Advisories | Agent Advisory Protocol blocks of nested `devkit` commands, whole | 4,000 characters |
| Excerpt | The output without the relayed blocks and filtered lines: its first 3,000 and last 5,000 characters, with a `[... N characters omitted ...]` line between them | 8,000 characters |

When an item does not fit its budget, it and every later item of that part are counted in `[RUN_OMITTED]` instead. The tail gets the larger share of the excerpt because failures usually end with the most useful lines: pytest's short test summary, a linter's last findings and its counts. The head keeps the first failure in full. Measured on ordinary output, 8,000 characters hold about ten short pytest failures or thirty ruff findings with their code frames; output beyond that is usually one cause repeated, and the log has the rest.

**Summaries** recognized: pytest's result line (including `no tests ran`, xdist and warning counts), Vitest's `Test Files`/`Tests` lines, Playwright's per-outcome lines, ruff's format and check results, Pyright's and svelte-check's counts, ESLint's problem count, Prettier's success line, pytest-cov's `TOTAL` line (relabelled `Coverage: TOTAL ...`), and `devkit rules`' `[SUMMARY: ...]` line.

**Warnings** recognized: `path:line: SomethingWarning: message` (Python, pytest), `path:line:col - warning: message` (Pyright), `(node:PID) ... Warning: message` (Node), `warning: message` and `Warn: message` (ruff, uv, svelte-check, with the preceding source file as location), and ESLint's `line:col  warning  message` under a file heading. A tool's warnings are findings, like a rule violation of severity `warning`: they are reported, and `--strict` does not apply to them.

**Filtered** out of the excerpt, each line counted in `filtered=`:

- *Progress*: pytest's progress lines (`tests/test_a.py ..F.s [ 45%]`, the continuation lines of status characters, and the `[ 12/130]` count style), `-v` lines of tests that passed, were skipped or xfailed, pytest-xdist's `[gw0] [ 12%] PASSED ...` lines, the `PASSED <test>` lines `-rA` adds to the short summary, Vitest's and Playwright's `✓` (and skipped `↓`) item lines, Jest's `PASS <file>` lines and Playwright's dot reporter lines of `·` only; plus every state a carriage return overwrote.
- *Noise*: pytest's session header (the `test session starts` banner and the `platform`, `rootdir`, `configfile`, `inifile`, `cachedir`, `testpaths` and `plugins` lines; `collected N items` stays), and uv's success messages (`Resolved`/`Prepared`/`Installed`/`Uninstalled`/`Audited`/`Downloaded N packages in ...`, `Building`/`Built <package> @ <source>`, `Downloading <package> (<size>)`, and the ` + pkg==1.2` / ` - pkg==1.2` / ` ~ pkg==1.2 (from ...)` lines). uv's `error:` and `× No solution found` lines stay.
- *Repeated sections*: pytest's `warnings summary`, from its banner up to its closing `-- Docs:` line, the next banner or a summary line, whichever comes first (under `-q` the final summary has no banner, and a command a recipe runs after pytest must not be filtered with the section). Its warnings are read before the section is filtered, so they reach `[RUN_WARNING]`.
- *Blank runs*: a blank line that follows another blank line of the excerpt, so the blank lines around a filtered line collapse as well.

A `FAILED` or `ERROR` line, `SKIPPED [n] <reason>` in the short summary, any line with a failure marker other than pytest's status characters, and a diff line that does not name a pinned package stay. The log keeps everything: when a run stops without a summary (a crash, a hang the host killed), its last progress line there shows where.

Warning locations under the working directory are shown relative to it (`tests/test_x.py:12`, not the absolute path pytest prints in its warnings summary). The excerpt is never rewritten this way: an assertion that compares paths must show them as they are.

**Advisory blocks** are recognized by the protocol's grammar ([block format](../advisory/protocol.md#3-block-format)): a headline line starting `[ERROR]  `, `[WARN]   ` or `[NOTICE] `, followed by field lines (`[ACTION] `, `[WHEN]   `, `[TARGET] `, `[FIX]    `, `[REPORT] `, `[DETAIL] `) and continuation lines indented 9 spaces. Under `-q`, relayed `[NOTICE]` blocks are dropped (the nested command also receives `DEVKIT_QUIET=1`).

---

## 5. Output

Text stdout, in this order:

```text
[RUN: "<command>" outcome=passed|failed exit=<code> log=<path>]
[RUN_SUMMARY: "<summary line>"]                         one per summary
[RUN_WARNING: "<message>" location=<location>|-]        one per warning
[RUN_OMITTED: summaries=N warnings=N advisories=N output=N]   only when something was left out
[RUN_OUTPUT: shown=N omitted=N filtered=N]             only when the command failed
<excerpt>                                               the rest of stdout
```

`output` in `[RUN_OMITTED]` counts excerpt characters only when the excerpt is shown, that is when the command failed. The command, summaries and warning messages are JSON strings; `log` and `location` are bare unless they contain spaces, quotes or brackets. `output` and `shown` count characters, `filtered` lines.

stderr, after the result: the relayed `[WARN]` and `[NOTICE]` blocks in output order, then the runner's own notices (`RUN_SLOW_COMMAND`), then the relayed `[ERROR]` blocks, so the decisive block ends the output. The runner's run time and log path are an `[INFO]` line under `-v`.

`--format json` prints one object with the same content: `command` (the argument list), `outcome`, `exit_code`, `log`, `summaries`, `warnings` (`message`, `location`), `advisories` (`level`, `text`), `omitted` (`summaries`, `warnings`, `advisories`, `output`), `output` (the excerpt, `null` when the command passed), `filtered` (`0` when the command passed) and `notices`.

**Tool options.** The largest remaining part of a failure is usually the tool's own report, and the tool can shorten it reliably where the runner could only guess. Measured on a real pytest failure log, the test source and argument values of the default long traceback were 40% of the output; ruff's default format spends about 250 characters per finding on a code frame, its concise format about 85. A project that wants a shorter view sets the tool's option in its recipe: `pytest --tb=short` (the failing line, the `E` lines and the location of each frame) and `ruff check --output-format=concise`. The `devkit-run` instruction recommends both.

**Slow commands.** A command that runs at least `--slow-after` seconds (default 60, `0` turns it off) adds a `RUN_SLOW_COMMAND` notice suggesting a narrower run. It is reported after the result, like every notice: an agent sees a command's output only when it ends, so an earlier message would not reach it sooner. `-q` hides it; it never changes the exit code.

---

## 6. Errors and Notices

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `RUN_COMMAND_NOT_STARTED` | `ERROR` (`INPUT_ERROR`, exit `2`) | `CommandNotStartedError` | The command does not exist or is not executable, or the working directory does not exist (also when the shell's current directory was removed) or cannot be entered; `[TARGET]` names the command or the directory. |
| `RUN_SLOW_COMMAND` | `NOTICE` | `SlowCommandNotice` | The command ran at least `--slow-after` seconds. |
| `ARGUMENT_INVALID` | `ERROR` (exit `2`) | `devkit.core.ArgumentError` | `--slow-after` is negative or not finite. |

Codes carry the `RUN_` prefix of the command agents call, not the module name.

---

## 7. Library

`devkit.compact` exports `run_command`, which never prints and returns a `CommandRun` (`argv`, `exit_code`, `log`, `duration`, `scan`, `notices`, with `passed` and `command`), and `scan`, which reads any text stream into a `Scan` (`summaries`, `warnings` as `ToolWarning`, `advisories` as `RelayedAdvisory`, `output`, `omitted` as `Omitted`). A bundled gate or workflow check can run a command through `run_command` and report the same view.

```text
packages/devkit/src/devkit/compact/
├── scan.py     # one bounded pass: summaries, warnings, relayed advisory blocks, excerpt
├── execute.py  # run_command: log file, process group, signals, retention, CommandRun
├── errors.py   # RUN_COMMAND_NOT_STARTED, RUN_SLOW_COMMAND
└── cli.py      # devkit run: text and JSON rendering, output options, exit codes
```

`compact` imports only `core` and `advisory`.

Agents in consumer repositories learn the command from the `devkit-run` instruction of the `devkit` guide bundle (listed by `devkit get-context devkit`), which also recommends putting `devkit run` inside a project's verification recipes. It is deliberately not an `AGENTS.md` line: running a command without the wrapper costs context, not correctness, and a project that runs its checks through recipes wraps them once there.

---

## 8. Scope

Not part of `devkit run`, deliberately:

- **Task planning** (`lint`/`check`/`test` derived from `pyproject.toml` and `package.json`): projects already name their verification commands, and wrapping them keeps one source of truth.
- **Several commands per run**: run a recipe that chains them (`devkit run -- just lint`).
- **A timeout**: the agent host already bounds a call; the runner makes sure that bound also stops the command's processes.
- **Raw output and configurable patterns**: the log path is on the `[RUN]` line, and an agent reads it with `rg` or `sed` as needed. Project-specific summary patterns can be added when a real need appears.

The design comes from `app-tools run` in the app-common repository, adapted to the devkit output contract.
