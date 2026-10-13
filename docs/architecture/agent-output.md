# Agent-First Output

The primary consumer of every `devkit` command is an AI coding agent that runs it through a shell or a tool call and acts on what comes back; a person reads the same output, but nothing is shaped for a person at the agent's expense. Everything a command prints lands in the agent's context window, so output is a contract, not a log. This document specifies that contract; the advisory blocks themselves are specified in the [Agent Advisory Protocol](../advisory/protocol.md), exit codes in [Architecture Overview, section 4](overview.md#4-errors-exit-codes-and-platforms).

## 1. Principles

1. **Two channels, two purposes.** stdout carries facts: the result of the command. stderr carries directives: what the agent must do or know about that result. An agent can take either channel alone and lose nothing the other one owns.
2. **Match, do not parse.** Text output is one fact per line, each behind a sentinel an agent can match with a fixed string. JSON output is exactly one object. Neither needs prose understanding.
3. **Codes, not prose.** Every condition worth reporting has a stable `UPPER_SNAKE` code. Messages explain; codes identify. Callers and tests branch on codes, never on message text.
4. **Directives, not narration.** A condition the agent must act on carries an `[ACTION]` directive that says what to do and what not to do. Nothing relies on the agent inferring intent from a description.
5. **Context budget.** The default output carries only what changes the agent's next step or must reach the user. Progress, timing, passed checks and diagnostics are logs, shown only under `-v`. A lasting condition that asks for nothing is announced once, when it appears, and stays visible as data afterwards ([protocol, section 8](../advisory/protocol.md#8-warnings-and-notices-in-practice)).
6. **Deterministic.** The same state gives the same bytes: no colour, no emoji, no box drawing, no progress bars, no alignment tables, no output that changes with the terminal (TTY detection, width, locale). stdout and stderr are always UTF-8 (a character UTF-8 cannot encode is written as its `\uXXXX` escape), and JSON is ASCII-only, with `\uXXXX` escapes.
7. **Libraries never print.** Library functions return results and collected advisories, and raise `AdvisoryError`; only the CLI layer writes to stdout or stderr. An embedding caller (another tool, an MCP server, a test) gets the same information as data.

## 2. Channels

| Channel | Carries | Never carries |
| --- | --- | --- |
| stdout, text mode | `[KIND: ...]` result lines; documents a command was asked to print (a guide, a rendered work unit) | advisories, logs |
| stdout, JSON mode | exactly one JSON object: the result with its `errors` and `notices`, or `{"error": {...}}` | anything else (no second document, no stray text) |
| stderr | advisory blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`); `[INFO]` log lines under `-v` | results; free text; click's own `Usage:` text is the only exception (usage errors, exit `2`) |
| exit code | `0` success, `1` negative result, `2` could not do its job | anything finer; the code says which, the advisories say why |

Every stderr line is either a sentinel line or a continuation line indented 9 spaces under the sentinel above it.

## 3. stdout: Text

Text-mode stdout is made of one-line sentinels:

```text
[KIND: <positional value> key=value key=value key="free text"]
```

- `KIND` is `UPPER_SNAKE` and names the fact (`VIOLATION`, `SUMMARY`, `STAGE`, `GATE`, `HOOK`, `UNIT`, `OK`, ...).
- A value without spaces is written bare; free text (messages, titles, remediations, descriptions) is written as a JSON string, so quotes, backslashes and newlines are escaped and the fact stays on one line.
- An empty value is `-`; a boolean is `yes` or `no`; a list is space- or comma-separated as the command documents it.
- A command that succeeds with nothing to report prints an `[OK: ...]` line, so an empty stdout never has to be interpreted.
- A document a command is asked to print (`devkit rules explain`'s guide, `devkit workflow show`'s rendering) follows its sentinel lines as written.

**Reserved names.** `ERROR`, `WARN`, `WARNING`, `NOTICE`, `INFO`, `DEBUG`, `ACTION`, `WHEN`, `TARGET`, `FIX`, `REPORT` and `DETAIL` are stderr sentinels and are never used as a stdout `KIND`. Something that would read as `[NOTICE: ...]` on stdout is a notice and goes to stderr; a fact that merely mentions a notice-like state gets its own kind (for example `[STALE_APPROVAL: ...]`).

## 4. stdout: JSON

Under `--format json` (and for every distribution command, which is JSON-only), stdout is exactly one JSON object, never a bare array:

```json
{
  "violations": [],
  "errors": [],
  "notices": []
}
```

- The command's payload sits under named keys (`violations`, `rules`, `units`, `checks`, `requests`, `overrides`, ...), or is the object itself for a single result (`SyncResult`).
- `errors` lists problems the command collected instead of raising, `notices` lists its warnings and notices; each entry is an advisory's `to_dict()`: `{"code", "level", "message", "exit_code", "advisory": {...}}`, plus fields a module adds (`rule_id`, `file`, `where`). A command that can collect neither omits the key.
- A command that fails outright prints `{"error": {...}}` (the same envelope) instead of a result. Warnings and notices collected before the failure then appear on stderr only.
- JSON is never filtered by `-q` or `-v`: it always carries every error and notice.

## 5. stderr: Advisories

Every error, warning and notice is an Agent Advisory Protocol block ([format](../advisory/protocol.md#3-block-format)). Their order on stderr is fixed:

1. `[INFO]` log lines (only under `-v`), as they occur;
2. warnings and notices, after the result has been printed: warnings first, then notices, each in the order the command collected them (JSON keeps the collected order);
3. errors, last, so the decisive block ends the output.

A command prints each block once. A command whose JSON result already carries an error (`Reported`) still renders that error on stderr, so the text channel stays complete.

## 6. Verbosity and Strictness

Every command takes the same three output options (`devkit.core.cli.output_options`, which the error boundary adds to every command), each also settable through the environment, which is how Git hooks (`devkit gate run`) receive them:

| Option | Environment | Effect |
| --- | --- | --- |
| `-q`, `--quiet` | `DEVKIT_QUIET=1` | Hide `[NOTICE]` blocks on stderr. Errors and warnings are always shown. |
| `-v`, `--verbose` | `DEVKIT_VERBOSE=1` | Also print `[INFO]` log lines on stderr, including the traceback behind an `UNEXPECTED_ERROR`. |
| `--strict` | `DEVKIT_STRICT=1` | Exit `1` instead of `0` when the run reported a warning. |

- An environment variable is on only when its value is exactly `1`. A command-line flag wins over the environment.
- `-q` and `-v` together (from flags, or from the environment when no flag is given) are `ARGUMENT_INVALID`.
- `-q` and `-v` affect stderr only; stdout, text or JSON, is the same in all three.
- `--strict` only ever raises the exit code (`0` to `1`); notices never count. It concerns advisory warnings only: a rule violation of severity `warning` is a finding, governed by the rule's severity in `[rules]`, not by `--strict`.
- Options go before positional arguments. `devkit gate run` passes everything after `<stage>` to the gates as hook arguments, so `devkit gate run -v pre-commit`, not `devkit gate run pre-commit -v`.

## 7. Exit Codes

`0` success, `1` the command ran and reports a negative result, `2` it could not do its job; the full rules are in [Architecture Overview, section 4](overview.md#4-errors-exit-codes-and-platforms). Warnings and notices never change the exit code, except under `--strict` (section 6). A command whose reader closes stdout early (`devkit ... | head`) stops writing and exits `2` without an advisory: its result was not delivered.

## 8. Logs (`INFO`)

Diagnostics that neither change the agent's next step nor need to reach the user are logs, written with the standard library's `logging` under the `devkit` logger hierarchy (`logging.getLogger(__name__)`).

- `devkit` installs a `NullHandler` on the `devkit` logger, so log records never reach the interpreter's last-resort handler and never leak onto stderr, in the CLI or in an embedding program.
- Under `-v`, the CLI boundary attaches a stderr handler for the run that prints every `devkit` record as `[INFO]   <module>: <message>` (`<module>` is the logger name without `devkit.`, such as `gate.engine.runner`), with a traceback and further lines indented 9 spaces as continuation lines. The sentinel is `[INFO]` whatever the record's level: a log line is never a directive.
- What to log: passed and skipped checks, timing, cache hits, why a candidate was or was not selected, the traceback behind an error the run already reports as an advisory.
- What never to log: anything the agent must act on or the user must learn. That is a warning or notice, returned with the result. Library code does not log at `WARNING` or above to communicate; `logger.exception` is used only to keep the traceback of an error that is also reported as an advisory.

## 9. Implementation Map

| Concern | Where |
| --- | --- |
| Advisory model, levels, modes, `[ACTION]` texts, block rendering, `to_dict` | `devkit.advisory` ([reference](../advisory/reference.md)) |
| `boundary` (with `output_options` and the log handler), `echo_notices`, `exit_on_warnings`, `echo_json`, `exit_on_problems` | `devkit.core.cli` ([reference](../core/reference.md)) |
| `NullHandler` on the `devkit` logger | `devkit/__init__.py` |
| Result lines and JSON payloads of each command | each area's `cli/` package, documented in its reference |
| Warnings and notices each area reports | each area's reference (error and notice code tables) |

## 10. Checklist for a New Command or Output

- [ ] The result goes to stdout only: `[KIND: ...]` lines in text mode, one object under `--format json`; no reserved name used as a kind.
- [ ] Every condition the agent must act on is an advisory with a code: raised as an `AdvisoryError` when the command cannot do its job or refuses, returned in `notices` at `WARNING` or `NOTICE` when it succeeded.
- [ ] The library function returns its warnings and notices; the command prints the result, then `echo_notices`, then `exit_on_warnings`.
- [ ] Diagnostics are `logging` calls, not output.
- [ ] The command goes through `boundary` (which adds the output options) and, when it prints text, takes `--format`.
- [ ] Its reference documents the result lines, the JSON keys, and every error and notice code with its level.

## 11. Example

`devkit sync` in a project where an override hides upstream changes and a newly installed bundle is not selected yet (JSON abridged):

stdout:

```json
{
  "dry_run": false,
  "actions": [{"action": "update", "path": ".devkit/managed/devkit/guide.md"}],
  "drift": [{"bundle": "starter", "asset": "development"}],
  "unselected": [{"bundle": "extras", "opted_out": false}],
  "notices": [
    {"code": "OVERRIDE_DRIFT", "level": "WARNING", "message": "upstream drift behind the override of starter:development", "exit_code": 0, "advisory": {"mode": "CONTINUE", "...": "..."}},
    {"code": "BUNDLE_UNSELECTED", "level": "NOTICE", "message": "installed bundles not selected yet: extras", "exit_code": 0, "advisory": {"mode": "NOTE", "...": "..."}}
  ]
}
```

stderr:

```text
[WARN]   (OVERRIDE_DRIFT) upstream drift behind the override of starter:development
[ACTION] CONTINUE — The operation succeeded; this does not block it. Do not retry
         or undo it. Tell the user about it ([REPORT] when present); run [FIX]
         only when they ask for it.
[TARGET] .devkit/overrides/starter/development.md
[FIX]    devkit override diff starter:development
[REPORT] Upstream changed an asset this project overrides; review the diff, then accept it or keep the override
[NOTICE] (BUNDLE_UNSELECTED) installed bundles not selected yet: extras
[ACTION] NOTE — For awareness only; nothing needs doing now. Continue. Mention it
         when it bears on the task; run [FIX] only when the user asks for it.
[FIX]    devkit add extras
[DETAIL] devkit add extras  (package extras-content; presets core; default core)
```

Exit code `0` (`1` with `--strict`). With `-q`, the `[NOTICE]` block is not printed; the JSON is unchanged. The next `devkit sync` in this clone repeats the warning (the override still needs a decision) but not the notice; `extras` stays listed under `unselected`.
