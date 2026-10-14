# Compact Command Output: Architecture Overview

**Package**: `devkit.compact` (`devkit run` CLI). Usage, error codes and module map: [Compact Reference](reference.md).  
**Related**: [Agent-First Output](../architecture/agent-output.md), [Agent Advisory Protocol](../advisory/protocol.md).

## 1. Overview and Objectives

Test runners, linters and type checkers print for people: progress dots, passed test names, timing tables, colour. An agent that runs them directly receives all of it, and when the output is long the agent host cuts it at an arbitrary point, often losing the part that matters.

`devkit run -- <command>` runs the command with its complete output in a log file and prints a bounded view instead: the outcome, the summary lines the tool printed (or, for a command that passed without a recognized one, its last lines), its warnings, the advisory blocks of nested `devkit` commands and, only when the command failed, a head-and-tail excerpt with progress and noise filtered out.

1. **The log is complete, the view is bounded.** Everything the command wrote goes to the log; every part of the view has a fixed budget. What does not fit is counted (`[RUN_OMITTED]`), never silently dropped, and every omission marker names the log lines it left out.
2. **Match output, not commands.** Summaries and warnings are recognized by the lines a tool prints, so `just`, `npm run`, `uv run` and shell wrappers work without configuration. No result is inferred from progress output.
3. **Progress and noise are not output.** Lines that only report progress or a passing item, overwritten progress bar states, lines that carry nothing an agent acts on, sections that repeat what the view already reports and copies of a line repeated in a row are filtered out of the excerpt, since they push the lines that locate a failure out of the budget. A line that names a failure is never filtered (of a run of identical ones, the first stays). The runner filters only what is safe without understanding a tool's structure; shortening a tool's own reports (tracebacks, code frames) is the tool's option to set (section 5).
4. **Directives survive.** An advisory block a nested `devkit` command prints is taken out whole and relayed on stderr, so its `[ACTION]` reaches the agent even when the output around it is cut.
5. **The runner wraps, it does not plan.** It runs one command as given. Which commands verify a project stays with the project (`justfile`, `package.json` scripts).
6. **Same contract as every devkit command** ([Agent-First Output](../architecture/agent-output.md)).

## 2. Execution

`devkit.compact.run_command` runs the command in the current directory:

- stdout and stderr go to one log file, in the order they were written;
- stdin is closed (`/dev/null`), so a command that waits for input ends instead of hanging the agent;
- the command runs in a session and process group of its own. When the runner is interrupted (Ctrl-C) or terminated (`SIGTERM`, `SIGHUP`, as an agent host does on a timeout), it stops the whole group (`SIGTERM`, then `SIGKILL` to whatever is left of the group after 5 seconds, even when the group's leader has already exited), so no test or build process outlives the run, then prints only `[RUN: "<command>" outcome=interrupted exit=<code> log=<path>]` (the log holds the output up to that point and shows where it stopped) and exits `128 + N` for signal `N`. The handlers are in place before the command starts; a signal that arrives while the command is being started is held until it has started, and further interrupts are ignored while the group is being stopped;
- processes the command leaves running in the background when it exits are not stopped. What they write later is appended to the log, after the part the view was made from: the view covers what the command wrote until it exited;
- the runner's output options reach the command as `DEVKIT_QUIET`, `DEVKIT_VERBOSE` and `DEVKIT_STRICT`, each `1` or `0` from the resolved settings, so nested `devkit` commands apply the same options (and a flag on the runner wins over the environment there too);
- the command's exit code is reported as is; a command ended by signal `N` reports `128 + N`.

The runner itself exits `0` when the command succeeded, `1` when it failed, `2` when it could not be started (`RUN_COMMAND_NOT_STARTED`), its log cannot be written (`RUN_LOG_DIR_INVALID`) or its own arguments are invalid, and `128 + N` when signal `N` interrupted it. The command's own code is the `exit=` field of the `[RUN]` line, so a command's `2` (pytest's usage error, for one) is never mistaken for the runner's.

## 3. Logs

Logs live outside the work tree, under `<tmp>/devkit-run-<uid>/<project>/`, where `<tmp>` is the system temporary directory, `<uid>` the user's ID and `<project>` a hash of the devkit project root containing the current directory (the root `devkit` commands resolve by default). Each run writes `<YYYYMMDD-HHMMSS>-<command>-<random>.log`; the 20 newest logs of a project are kept and older ones are deleted when a new run starts. The scan reads the log back through a file it opened before the command started, so a concurrent run that prunes it first does not lose this run's view; the command appends to the log through a descriptor of its own, so nothing it or a process it leaves behind writes moves what the scan reads.

The `devkit-run-<uid>` directory and each project's directory in it are created `0700`, since `/tmp` may be shared between users; access a group or others have to them is taken away. When either is a symlink, not a directory or belongs to another user, the run stops with `RUN_LOG_DIR_INVALID` before the command starts, and so does a run whose log cannot be created (no permission, disk full).

## 4. The Bounded View

One pass over the log (`devkit.compact.scan`) produces every part of the view. Each line is first reduced to what a terminal would show: ANSI escape sequences (colour and cursor control, OSC hyperlinks and titles, character set selection) are removed, and a carriage return starts the line over, so a progress bar leaves only its last non-blank state. Only the last 64,000 characters of a line are kept (its first 1,000 as well); a line longer than 1,000 characters is recognized by its start only. A line longer than 64,000 characters appears in the excerpt as its first and last 1,000 characters with a `[... N characters of log line L omitted ...]` line between them, unless a carriage return overwrote it.

| Part | Content | Budget |
| --- | --- | --- |
| Summaries | Lines that match a known summary format exactly (below) | 2,000 characters |
| Last lines | The excerpt's last non-blank lines, shown only for a command that passed without a recognized summary | 5 lines and 500 characters |
| Failures | The tests pytest names as failed or errored that no line of the excerpt names, shown beside the excerpt, each message cut at 200 characters | 2,000 characters |
| Warnings | One-line warnings with the first location they name, each message once, cut at 500 characters | 2,000 characters |
| Advisories | Agent Advisory Protocol blocks of nested `devkit` commands, whole | 4,000 characters for errors and 4,000 for warnings and notices, so errors are never crowded out; a block that does not fit is counted, stays in the excerpt, and the next one is tried |
| Excerpt | The output without the relayed blocks and filtered lines: its first 3,000 and last 5,000 characters, with a `[... N characters omitted, log lines A-B ...]` line between them | 8,000 characters |

When an item does not fit its budget, it and every later item of that part are counted in `[RUN_OMITTED]` instead. The tail gets the larger share of the excerpt because failures usually end with the most useful lines (pytest's short test summary, a linter's last findings and counts); the head keeps the first failure in full.

The budgets are measured against a corpus of real tool output in `packages/devkit/tests/compact/fixtures/` (pytest with long, short and line tracebacks, `-v` and `-q`, pytest-xdist `-v` with a crashed worker, `uv run`, ruff's full and concise formats, mypy, a retry loop). `tests/compact/test_corpus.py` bounds the size of each fixture's view and checks that the lines an agent needs survive and that every failed test is named or counted; a change to a pattern or a budget is measured there, and each new tool or output shape the scan learns adds a fixture.

Every omission marker names the log lines it stands for, counted as `sed` counts them (1-based, filtered lines and relayed blocks included), so an agent reads exactly what was left out (`sed -n 'A,Bp' <log>`). The range covers whole lines: a line the cut runs through is included.

**Last lines** stand in for a summary the scan does not recognize (a tool usually ends with its verdict: `Success: no issues found`, `Done in 3s`): a command that passed with no recognized summary shows the excerpt's last non-blank lines, without their indentation; a last line longer than the budget is cut with `...`. They come from the excerpt, so filtered lines and relayed blocks are never among them, and neither are the excerpt's marker lines. A command that printed nothing, or only filtered lines, shows none. A failed command shows the excerpt instead, which ends with the same lines.

**Failures** list the tests a failed run names that the excerpt cuts out, so an agent learns everything that failed, and can rerun it by node ID, without reading the log; a test the excerpt names (in the head, in the tail, by its `-v` line or its short summary line) is not repeated. A test is recognized by pytest's `FAILED <node id>[ - <message>]` and `ERROR <node id>[ - <message>]` short summary lines (also with pytest-xdist's `[gw0] [ 59%]` prefix) and the `<node id> FAILED|ERROR [ 59%]` lines of `-v`; `kind` is `failed`, or `error` for a setup, teardown or collection error, and the message is the one the short summary prints. Other tools' failure lines are not recognized: their failures reach the agent through the excerpt only. Failures are listed in the order the output first names them; those beyond the budget are counted in `[RUN_OMITTED]`, so excerpt, failures and count together account for every failed test. Reads stay bounded: the first 10,000 failed tests are remembered for the list, 100,000 more only to be counted once each; past those, each further line that names a failed test is counted, so a run with more failed tests than that has an approximate count. Like the excerpt, failures are shown only when the command failed.

**Summaries** recognized: pytest's result line (including `no tests ran`, xdist and warning counts), Vitest's `Test Files`/`Tests` lines, Playwright's per-outcome lines, ruff's format and check results, tsc's and mypy's `Found N errors ...` lines and mypy's `Success: no issues found in N source files`, Jest's `Tests:`/`Test Suites:` lines, cargo's `test result:` line, Pyright's and svelte-check's counts, ESLint's problem count, Prettier's success line, pytest-cov's `TOTAL` line (relabelled `Coverage: TOTAL ...`), and `devkit rules`' `[SUMMARY: ...]` line.

**Warnings** recognized: `path:line: SomethingWarning: message` (Python, pytest), `path:line:col - warning: message` (Pyright), `(node:PID) ... Warning: message` (Node), `warning: message` and `Warn: message` (ruff, uv, svelte-check, with the preceding source file as location), and ESLint's `line:col  warning  message` under a file heading. A tool's warnings are findings, like a rule violation of severity `warning`: they are reported, and `--strict` does not apply to them. Warning locations under the working directory are shown relative to it (`tests/test_x.py:12`, not the absolute path pytest prints in its warnings summary); the excerpt is never rewritten this way, since an assertion that compares paths must show them as they are.

**Filtered** out of the excerpt, each line counted in `filtered=`:

- *Progress*: pytest's progress lines without a failure (`tests/test_a.py ....s [ 45%]`, the continuation lines of status characters, and the `[ 12/130]` count style; a line with `F` or `E` stays, since it records which file failed), `-v` lines of tests that passed, were skipped or xfailed, pytest-xdist's `[gw0] [ 12%] PASSED ...` lines, the line pytest-xdist's `-v` prints as each test starts (the node ID and one trailing space; a `--collect-only` listing, which has no trailing space, stays) and its closing `[100%]` alone, the `PASSED <test>` lines `-rA` adds to the short summary, Vitest's and Playwright's `✓` (and skipped `↓`) item lines, Jest's `PASS <file>` lines and Playwright's dot reporter lines of `·` only; plus every state a carriage return overwrote.
- *Noise*: pytest's session header (the `test session starts` banner and the `platform`, `rootdir`, `configfile`, `inifile`, `cachedir`, `testpaths` and `plugins` lines; `collected N items` stays), pytest-xdist's worker startup (`created: 8/8 workers`, `bringing up nodes...`, `scheduling tests via ...`; `8 workers [N items]` stays) and the `[gw0] <platform> -- Python <version> <interpreter>` line above each failure (a crashed worker's `node down` and `replacing crashed worker` lines stay), and uv's success messages (`Resolved`/`Prepared`/`Installed`/`Uninstalled`/`Audited`/`Downloaded N packages in ...`, `Building`/`Built <package> @ <source>`, `Downloading <package> (<size>)`, and the ` + pkg==1.2` / ` - pkg==1.2` / ` ~ pkg==1.2 (from ...)` lines). uv's `error:` and `× No solution found` lines stay.
- *Repeated sections*: pytest's `warnings summary`, from its banner up to its closing `-- Docs:` line, the next banner, a summary line or any other unindented line that is neither where a warning was raised (a node ID, `<file>: N warnings`, `<file>:<line>`) nor a warning line, whichever comes first (under `-q` the final summary has no banner, and a command a recipe runs after pytest must not be filtered with the section, even when the section has no closing line). Its warnings are read before the section is filtered, so they reach `[RUN_WARNING]`.
- *Blank runs*: a blank line that follows another blank line of the excerpt, so the blank lines around a filtered line collapse as well.
- *Repeated lines*: a line identical (as a terminal shows it) to the line before it in the excerpt, as a retry loop or a warning printed once per item produces. The first stays, and the copies after it become one `[... previous line repeated N more times, log lines A-B ...]` line, unless that line is longer than the copies; then they stay. Lines that differ in a timestamp or a counter stay, since telling which part of a line is noise needs the tool's format.

A `FAILED` or `ERROR` line (also inside a filtered section), `SKIPPED [n] <reason>` in the short summary, a pytest progress line with `F` or `E`, any other line with a failure marker, and a diff line that does not name a pinned package stay. The log keeps everything: when a run stops without a summary (a crash, a hang the host killed), its last progress line there shows where.

**Advisory blocks** are recognized by the protocol's grammar ([block format](../advisory/protocol.md#3-block-format)), using the sentinels `devkit.advisory` exports (`HEADLINE`, `FIELDS`, `CONTINUATION`) so the scan follows the protocol's renderer; a rendered block contains no empty line, so an empty line ends one. A block longer than its budget is never relayed: once it outgrows the budget it ends, is counted in `[RUN_OMITTED]` and stays in the excerpt, as does a block that does not fit what is left of the budget. Under `-q`, relayed `[NOTICE]` blocks are dropped (the nested command also receives `DEVKIT_QUIET=1`).

## 5. Output

Text stdout, in this order:

```text
[RUN: "<command>" outcome=passed|failed|interrupted exit=<code> log=<path>]
[RUN_SUMMARY: "<summary line>"]                         one per summary
[RUN_LAST_LINE: "<line>"]                               one per last line, only when the command passed without a summary
[RUN_FAILURE: "<node id>" kind=failed|error message=<message>|-]   one per failed test the excerpt cuts out, only when the command failed
[RUN_WARNING: "<message>" location=<location>|-]        one per warning
[RUN_OMITTED: summaries=N failures=N warnings=N advisories=N output=N]   only when something was left out
[RUN_OUTPUT: shown=N omitted=N filtered=N]             only when the command failed
<excerpt>                                               the rest of stdout
```

An interrupted run prints the `[RUN]` line alone (section 2). `failures` and `output` in `[RUN_OMITTED]` count only when the excerpt is shown, that is when the command failed; `failures` counts the failed tests the view names nowhere. The command, summaries, last lines, node IDs and warning messages are JSON strings; `log`, `location` and a failure's `message` are bare unless they contain spaces, quotes or brackets. `output` and `shown` count characters, `filtered` lines.

stderr in text mode, after the result: the relayed `[WARN]` and `[NOTICE]` blocks in output order, then the runner's own notices (`RUN_SLOW_COMMAND`), then the relayed `[ERROR]` blocks, so the decisive block ends the output. Under `--strict` a relayed `[WARN]` block makes a run that passed exit `1`: the nested command receives `DEVKIT_STRICT=1` and fails on its own, but a wrapper (`|| true`, an npm script) may hide that, and the runner reported the warning either way. Under `-v`, `[INFO]` lines give the runner's run time and log path, and the size of the view against the output (`showed N characters for M of output (P%)`, stdout and relayed blocks against every character the command wrote).

`--format json` prints one object with the same content: `command` (the argument list), `outcome` (`passed`, `failed` or `interrupted`), `exit_code`, `log`, `summaries`, `last_lines` (empty unless the command passed without a summary), `failures` (`test`, `kind`, `message`; empty when the command passed), `warnings` (`message`, `location`), `advisories` (`level`, `text`), `omitted` (`summaries`, `failures`, `warnings`, `advisories`, `output`), `output` (the excerpt, `null` when the command passed), `filtered` (`0` when the command passed) and `notices`. The relayed blocks are then only in `advisories`, in output order, and nothing is printed on stderr.

**Tool options.** The largest remaining part of a failure is usually the tool's own report, which the tool can shorten reliably where the runner could only guess (on a real pytest failure log, the default long traceback's test source and argument values were 40% of the output; ruff's default format spends about 250 characters per finding on a code frame, its concise format about 85). A project that wants a shorter view sets the option in its recipe: `pytest --tb=short` (the failing line, the `E` lines and the location of each frame) and `ruff check --output-format=concise`. The `devkit-run` instruction recommends both.

**Slow commands.** A command that runs at least `--slow-after` seconds (default 60, `0` turns it off) adds a `RUN_SLOW_COMMAND` notice suggesting a narrower run. It is reported after the result, like every notice: an agent sees a command's output only when it ends. `-q` hides it; it never changes the exit code.

## 6. Library

`devkit.compact` exports `run_command`, which never prints and returns a `CommandRun` (`argv`, `exit_code`, `log`, `duration`, `scan`, `notices`, `interrupted`, with `passed` and `command`), or raises `CommandInterrupted` (a `SystemExit` with code `128 + N`, carrying the interrupted `CommandRun` as `run`, its scan empty) once it has stopped the command's group, and `scan`, which reads any text stream into a `Scan` (`summaries`, `failures` as `Failure`, `warnings` as `ToolWarning`, `advisories` as `RelayedAdvisory`, `output`, `omitted` as `Omitted`, `filtered`, `last_lines`, and `read`, the characters it read; whether to show the last lines and the failures is the caller's choice). A bundled gate or workflow check can run a command through `run_command` and report the same view. `compact` imports only `core` and `advisory`.

Agents in consumer repositories learn the command from the `devkit-run` instruction of the `devkit` guide bundle, which also recommends putting `devkit run` inside a project's verification recipes. By default it is not an `AGENTS.md` line: running a command without the wrapper costs context, not correctness, and a project that runs its checks through recipes wraps them once there. The instruction's header is visible only after `devkit get-context devkit`, though, and agents often run a narrowed command (one test file, `-k`) outside the recipes; a project where they do selects the opt-in preset `devkit:run`, whose one `AGENTS.md` line (about 200 bytes per turn) sends them to `devkit run` and its instruction.

## 7. Scope

Not part of `devkit run`, deliberately:

- **Task planning** (`lint`/`check`/`test` derived from `pyproject.toml` and `package.json`): projects already name their verification commands, and wrapping them keeps one source of truth.
- **Several commands per run**: run a recipe that chains them (`devkit run -- just lint`).
- **A timeout**: the agent host already bounds a call; the runner makes sure that bound also stops the command's processes.
- **Raw output and configurable patterns**: the log path is on the `[RUN]` line, and an agent reads it with `rg` or `sed` as needed. Project-specific summary patterns can be added when a real need appears.
