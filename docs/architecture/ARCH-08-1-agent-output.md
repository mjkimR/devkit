---
id: ARCH-08-1-agent-output
title: Agent-First Output
summary: "Output contract for devkit commands: stdout sentinels, JSON envelopes, advisory routing, and log capturing."
status: active
created_at: 2026-10-17
---

# [ARCH-08-1-agent-output] Agent-First Output

The primary consumer of every `devkit` command is an AI coding agent that runs it through a shell or a tool call and acts on what comes back; a person reads the same output, but nothing is shaped for a person at the agent's expense. Everything a command prints lands in the agent's context window, so output is a contract, not a log. This document specifies that contract; the advisory blocks themselves are specified in the `CAP-ADV-agent-advisory-protocol`, exit codes in `ARCH-08-cross-cutting`. The contract is implemented once, in `devkit_cli`, so a click tool outside devkit reports the same way under its own logger and environment prefix (`CAP-CLI-agent-cli-toolkit`).

## 1. Principles

1. **Each advisory reaches the agent once.** In text mode stdout carries facts, the result of the command, and stderr carries directives: what the agent must do or know about that result. In JSON mode the one JSON object carries both, every advisory with its directive text, and stderr MUST NOT carry an advisory. Agent hosts usually merge the two channels into one tool result, so an advisory printed on both would be read, and paid for, twice.
2. **Match, do not parse.** Text output MUST be one fact per line, each behind a sentinel an agent can match with a fixed string. JSON output MUST be exactly one object. Neither needs prose understanding.
3. **Codes, not prose.** Every condition worth reporting MUST have a stable `UPPER_SNAKE` code. Messages explain; codes identify. Callers and tests MUST branch on codes, never on message text.
4. **Directives, not narration.** A condition the agent must act on MUST carry an `[ACTION]` directive that says what to do and what not to do. Nothing relies on the agent inferring intent from a description.
5. **Context budget.** The default output SHOULD carry only what changes the agent's next step or must reach the user. Progress, timing, passed checks and diagnostics MUST be logs, shown only under `-v`. A lasting condition that asks for nothing is announced once, when it appears, and stays visible as data afterwards (`CAP-ADV-agent-advisory-protocol`).
6. **Deterministic.** The same state MUST give the same bytes: no colour, no emoji, no box drawing, no progress bars, no alignment tables, no output that changes with the terminal (TTY detection, width, locale). stdout and stderr MUST always be UTF-8 (a character UTF-8 cannot encode, such as a lone surrogate from an undecodable path, is written as its `\uXXXX` escape, which keeps JSON valid). JSON text MUST be UTF-8 too, never `\uXXXX`-escaped: an escaped non-English path or message costs the agent context and has to be decoded back before it can be used.
7. **Libraries never print.** Library functions return results and collected advisories, and raise `AdvisoryError`; they MUST NOT write to stdout or stderr, which only the CLI layer does. An embedding caller (another tool, an MCP server, a test) gets the same information as data.

## 2. Channels

| Channel | Carries | Never carries |
| --- | --- | --- |
| stdout, text mode | `[KIND: ...]` result lines; documents a command was asked to print (a guide, a rendered work unit) | advisories, logs |
| stdout, JSON mode | exactly one JSON object: the result with its `errors` and `notices`, or `{"error": {...}}` | anything else (no second document, no stray text) |
| stderr, text mode | advisory blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`); `[INFO]` log lines under `-v` | results; free text; click's own `Usage:` text is the only exception (usage errors, exit `2`) |
| stderr, JSON mode | `[INFO]` log lines under `-v`; click's `Usage:` text | advisories: the JSON object carries them |
| exit code | `0` success, `1` negative result, `2` could not do its job | anything finer; the code says which, the advisories say why |

Every stderr line other than click's `Usage:` text MUST be either a sentinel line or a continuation line indented 9 spaces under the sentinel above it.

The native `devkit host hook` transport is a scoped exception: it MUST emit only the host-defined JSON response on
stdout, warnings on stderr and exit 0 for advisory dispatch failures. It has no `--format`, verbosity or strict
options. It MUST NOT emit devkit result sentinels or ordinary error objects; see
`CAP-HOST-lifecycle-observation`. Other host commands follow this contract.

`devkit mcp serve` likewise MUST reserve stdout for native MCP JSON-RPC, without ordinary output options.
Startup errors go to stderr and exit 2; per-tool results carry structured advisory data. The optional SDK owns
protocol framing. See `CAP-MCP-runtime-registration`.

## 3. stdout: Text

Text-mode stdout is made of one-line sentinels:

```text
[KIND: <positional value> key=value key=value key="free text"]
```

- `KIND` MUST be `UPPER_SNAKE` and name the fact (`VIOLATION`, `SUMMARY`, `STAGE`, `GATE`, `HOOK`, `UNIT`, `OK`, ...).
- A value is written bare when it has no whitespace, `"`, `[`, `]`, `=` or backslash; otherwise, and always for free text (messages, titles, remediations, descriptions), it MUST be written as a JSON string, so quotes, backslashes and newlines are escaped and the fact stays on one line.
- An empty value (`None` or `""`) is `-`; a boolean is `yes` or `no`; a list is space- or comma-separated as the command documents it.
- Every devkit command MUST render a field value with the one `devkit_dist.adapters.cli.field_value` (booleans alone with `yes_no`).
- A command that succeeds with nothing to report MUST print an `[OK: ...]` line, so an empty stdout never has to be interpreted.
- A document a command is asked to print (`devkit rules explain`'s guide, `devkit workflow show`'s rendering) follows its sentinel lines as written, and so does the bounded excerpt of a failed command after its `[RUN_OUTPUT: ...]` (`devkit run`) or `[RULE_TEST_OUTPUT: ...]` (`devkit rules test`) line.

**Paging.** A listing command that pages (it takes `--offset` and reports a `total`) MUST end its items with the shared paging lines:

```text
[PAGE: total=25 offset=0 limit=20 count=20 next=20]
[NEXT_CMD: uv run devkit exec list --limit 20 --offset 20]
```

- `[PAGE: ...]` follows the items, also when there are none (`count=0`), so an empty page is an explicit result. `next` is the offset of the following page and `-` on the last page.
- `[NEXT_CMD: ...]` repeats the command's own arguments with `--offset <next>` and is printed only when more items follow.
- A command prints them with `devkit_dist.adapters.cli.echo_page`. A command that adds its own fields after `next` (`docs list`'s `hidden`) MAY instead print `[PAGE: ...]` with `fields_line` in the same field order, under the same `next` and `[NEXT_CMD: ...]` rules; its own fields and any lines after `[NEXT_CMD: ...]` are documented in its capability. Each command's capability states its `--limit` bounds and default, whether `--limit 0` means all items, and its error code for an out-of-bound value. A bounded listing that does not page prints no paging lines.
- The line format is checked by `packages/devkit-dist/tests/unit/adapters/test_sentinels.py`; that a paging command prints them this way is review only.

**Reserved names.** `ERROR`, `WARN`, `WARNING`, `NOTICE`, `INFO`, `DEBUG`, `ACTION`, `WHEN`, `TARGET`, `FIX`, `REPORT` and `DETAIL` are stderr sentinels and MUST NOT be used as a stdout `KIND`. Something that would read as `[NOTICE: ...]` on stdout is a notice and MUST go to stderr; a fact that merely mentions a notice-like state gets its own kind (for example `[STALE_APPROVAL: ...]`).

## 4. stdout: JSON

Under `--format json` (and for the distribution commands other than `sync`, `add` and `remove`, which are JSON-only), stdout MUST be exactly one JSON object, never a bare array. It MUST be compact (no indentation and no spaces after separators), since every byte reaches the agent's context; the example below is indented for reading only. A JSON-only command also accepts `--format json` as a no-op, so an agent MAY pass it to every command; any other format is a usage error:

```json
{
  "violations": [],
  "errors": [],
  "notices": []
}
```

- The command's payload sits under named keys (`violations`, `rules`, `units`, `checks`, `requests`, `overrides`, ...), or is the object itself for a single result (`SyncResult`).
- `errors` lists problems the command collected instead of raising, `notices` lists its warnings and notices; each entry is an advisory's `to_dict()`: `{"code", "level", "message", "exit_code", "advisory": {...}}`, plus fields a module adds (`rule_id`, `file`, `where`). `advisory` holds what the block would show: `mode`, the `[ACTION]` directive as `action`, and each other field only when it has a value (`CAP-ADV-agent-advisory-protocol`). A command that can collect neither omits the key.
- A command that fails outright MUST print `{"error": {...}}` (the same envelope) instead of a result, with the warnings and notices it collected before the failure under `notices`.
- JSON MUST NOT be filtered by `-q` or `-v`: it always carries every error and notice.

## 5. stderr: Advisories

In text mode every error, warning and notice is an Agent Advisory Protocol block (`CAP-ADV-agent-advisory-protocol`) on stderr; in JSON mode none is (section 4 carries them). Their order on stderr is fixed:

1. `[INFO]` log lines (only under `-v`), as they occur;
2. warnings and notices, after the result has been printed: warnings first, then notices, each in the order the command collected them (JSON keeps the collected order);
3. errors, last, so the decisive block ends the output.

A command MUST print each block once. A text-mode command whose result was printed before an error stopped it (`Reported`) renders that error after the result.

## 6. Verbosity and Strictness

Every command takes the same three output options (`devkit_dist.adapters.cli.output_options`, which the error boundary adds to every command), each also settable through the environment, which is how Git hooks (`devkit gate run`) receive them:

| Option | Environment | Effect |
| --- | --- | --- |
| `-q`, `--quiet` | `DEVKIT_QUIET=1` | Hide `[NOTICE]` blocks on stderr. Errors and warnings are always shown. |
| `-v`, `--verbose` | `DEVKIT_VERBOSE=1` | Also print `[INFO]` log lines on stderr, including the traceback behind an `UNEXPECTED_ERROR`. |
| `--strict` | `DEVKIT_STRICT=1` | Exit `1` instead of `0` when the run reported a warning. |

- An environment variable is on only when its value is exactly `1`. A command-line flag wins over the environment.
- `-q` and `-v` together (from flags, or from the environment when no flag is given) are `ARGUMENT_INVALID`.
- `-q` and `-v` affect stderr only; stdout, text or JSON, MUST be the same in all three.
- `--strict` only ever raises the exit code (`0` to `1`); notices never count. It concerns advisory warnings only: a rule violation of severity `warning` is a finding, governed by the rule's severity in `[rules]`, not by `--strict`.
- Options SHOULD go before positional arguments. `devkit gate run` passes everything after `<stage>` to the gates as hook arguments, so its options MUST go before `<stage>`: `devkit gate run -v pre-commit`, not `devkit gate run pre-commit -v`.

## 7. Exit Codes

`0` success, `1` the command ran and reports a negative result, `2` it could not do its job; the full rules are in `ARCH-08-cross-cutting`. Warnings and notices never change the exit code, except under `--strict` (section 6). A command whose reader closes stdout early (`devkit ... | head`) stops writing and exits `2` without an advisory: its result was not delivered.

## 8. Logs (`INFO`)

Diagnostics that neither change the agent's next step nor need to reach the user are logs, written with the standard library's `logging` under the `devkit` logger hierarchy (`logging.getLogger(__name__)`).

- `devkit` installs a `NullHandler` on the `devkit` logger, so log records never reach the interpreter's last-resort handler and never leak onto stderr, in the CLI or in an embedding program.
- Under `-v`, the CLI boundary attaches a stderr handler for the run that prints every `devkit` record as `[INFO]   <module>: <message>` (`<module>` is the logger name without `devkit.`, such as `gate.engine.runner`), with a traceback and further lines indented 9 spaces as continuation lines. The sentinel is `[INFO]` whatever the record's level: a log line is never a directive.
- What to log: passed and skipped checks, timing, cache hits, why a candidate was or was not selected, the traceback behind an error the run already reports as an advisory.
- What never to log: anything the agent must act on or the user must learn; it MUST be a warning or notice, returned with the result. Library code MUST NOT log at `WARNING` or above to communicate. `logger.exception` MAY be used only to keep the traceback of an error that is also reported as an advisory.

## 9. Implementation Map

| Concern | Where |
| --- | --- |
| Advisory model, levels, modes, `[ACTION]` texts, block rendering, `to_dict` | `devkit.advisory` ([reference](../development/reference/advisory.md)) |
| `Boundary` (with `output_options` and the log handler), `echo_notices`, `exit_on_warnings`, `echo_json`, `exit_on_problems`, `LazyGroup` | `devkit_cli` (`CAP-CLI-agent-cli-toolkit`) |
| devkit's `boundary` (`Boundary("devkit")`: the `devkit` logger, `DEVKIT_*` variables) and the re-exported helpers every devkit command imports | `devkit_dist.adapters.cli` ([reference](../development/reference/core.md)) |
| `NullHandler` on the `devkit` logger, `get_logger` for every module | `devkit_core.core.logs` |
| Result lines and JSON payloads of each command | each area's `cli/` package, documented in its reference |
| Warnings and notices each area reports | each area's reference (error and notice code tables) |

## 10. Checklist for a New Command or Output

- [ ] The result goes to stdout only: `[KIND: ...]` lines in text mode, one object under `--format json`; no reserved name used as a kind.
- [ ] Every condition the agent must act on is an advisory with a code: raised as an `AdvisoryError` when the command cannot do its job or refuses, returned in `notices` at `WARNING` or `NOTICE` when it succeeded.
- [ ] The library function returns its warnings and notices; the command prints the result, then `echo_notices`, then `exit_on_warnings`.
- [ ] A listing command that pages prints `[PAGE: ...]` and `[NEXT_CMD: ...]` through `echo_page`, or with `fields_line` when it adds fields after `next` (section 3), and its capability states its limit bounds.
- [ ] Diagnostics are `logging` calls, not output.
- [ ] The command goes through `boundary` (which adds the output options) and, when it prints text, takes `--format`.
- [ ] Its reference documents the result lines, the JSON keys, and every error and notice code with its level.

## 11. Example

`devkit sync` in a project where an override hides upstream changes and a newly installed bundle is not selected yet.

stdout:

```text
[SYNC: create=0 update=1 remove=0 seed=0 dry_run=no]
[CHANGE: update .devkit/managed/devkit/guide.md]
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

Exit code `0` (`1` with `--strict`). With `-q`, the `[NOTICE]` block is not printed. The next `devkit sync` in this clone repeats the warning (the override still needs a decision) but not the notice. A run with nothing to write prints `[SYNC: create=0 update=0 remove=0 seed=0 dry_run=no]` and `[OK: the workspace matches the selection]`: the deployed state is the same on every run, so text mode never repeats it.

`devkit sync --format json` prints the same advisories inside the one object and nothing on stderr (abridged):

```json
{
  "dry_run": false,
  "actions": [{"path": ".devkit/managed/devkit/guide.md", "action": "update"}],
  "drift": [{"bundle": "starter", "asset": "development"}],
  "unselected": [{"bundle": "extras", "opted_out": false}],
  "notices": [
    {"code": "OVERRIDE_DRIFT", "level": "WARNING", "message": "upstream drift behind the override of starter:development", "exit_code": 0,
     "advisory": {"code": "OVERRIDE_DRIFT", "level": "WARNING", "mode": "CONTINUE", "action": "CONTINUE — The operation succeeded; ...", "fix": "devkit override diff starter:development", "...": "..."}},
    {"code": "BUNDLE_UNSELECTED", "level": "NOTICE", "message": "installed bundles not selected yet: extras", "exit_code": 0,
     "advisory": {"code": "BUNDLE_UNSELECTED", "level": "NOTICE", "mode": "NOTE", "action": "NOTE — For awareness only; ...", "fix": "devkit add extras", "...": "..."}}
  ]
}
```

JSON is never filtered by `-q`, and `extras` stays listed under `unselected` on later runs.
