---
name: agent-advisory
description: Read before authoring CLI commands, tool or API errors, warnings, notices, rule violations or advisory envelopes.
---

# The Agent Advisory Protocol

Every error, warning and notice an agent reads carries a stable `UPPER_SNAKE_CASE`
code and an `[ACTION]` directive derived from its fields. Callers branch on the
code, never on message text.

## Levels

1. If the operation could not do its job, refused, or a check it ran found a negative result: `ERROR`. A refusal is never a warning.
2. If it succeeded and the user must learn or decide something: `WARNING`.
3. If it succeeded and the agent may want to know why the result looks as it does or what it could do next: `NOTICE`.
4. Otherwise emit no advisory; log it at most.

| Level | Headline | Exit code |
| --- | --- | --- |
| `ERROR` | `[ERROR]` | `1` negative result, `2` could not run; never `0` |
| `WARNING` | `[WARN]` | unchanged (a strict mode may turn `0` into `1`) |
| `NOTICE` | `[NOTICE]` | unchanged |

Return warnings and notices with the result under `notices`; never raise them.
Name all affected items in one advisory per condition. Keep a condition the user
must act on a warning on every run until resolved; announce a notice only when
it appears or changes.

## Fields and modes

| Field | Levels | Meaning |
| --- | --- | --- |
| `code`, `level` | all | Stable code; `ERROR` (default), `WARNING` or `NOTICE` |
| `actor` | error | `TOOL` (agent runs the fix), `USER` (a human decides), `DEVELOPER` (code or input must change), `NONE` |
| `retry` | error | `SAFE`, `AFTER_FIX` or `UNSAFE` (retry risks corruption or duplicate effects) |
| `guardrail`, `input_error` | error | A deliberate policy refused; a flag, argument or input file is malformed |
| `retry_after` | error | Earliest retry time or duration |
| `fix` | all | One exact runnable command or edit, never a template with placeholders |
| `what_to_report` | all | What the agent must relay to the user |
| `target_files` | all | Files, flags or `path:line:col` locations; identifiers go in the message or `details` |
| `details` | all | Diagnostic lines |
| `brief` | notice | Omit `[ACTION]` when there is no `fix` |

The mode is derived, never set; the first matching rule wins:

| Rule | Mode | Use for |
| --- | --- | --- |
| `level = WARNING` / `NOTICE` | `CONTINUE` / `NOTE` | succeeded; the user must know / worth knowing |
| `input_error` | `INPUT_ERROR` | malformed flags, missing arguments, parse errors in user files, content checks the agent fixes and retries (failing tests, rule violations or an empty message in a commit) |
| `guardrail` | `BLOCKED` | protected branches, out-of-scope edits, policy refusals by rules and gates |
| `actor = DEVELOPER` | `MAINTENANCE` | invariant violations, unexpected exceptions, tool defects |
| `retry = UNSAFE` | `HALT` | half-applied mutations or state that further execution can damage |
| `actor = TOOL` | `AUTO` | a safe, idempotent fix command exists; `fix` is required |
| `actor = USER` | `INTERACTION` | ambiguous intent, sign-off, missing credentials; set `retry = AFTER_FIX`, not `UNSAFE` |
| `retry = SAFE` | `DEFER` | rate limits, running jobs, locks held elsewhere; set `retry_after` |
| otherwise | `HALT` | |

Choose the fields from the directive the agent must follow, then check the
derived mode. Render the `[ACTION]` text of each mode exactly as
`devkit.advisory.ACTION_TEXT` defines it.

## Rendering

```text
[ERROR]  (<CODE>) <One concise sentence>
[ACTION] <MODE> — <directive>
[WHEN]   Not before: <retry_after>
[TARGET] <target_files>
[FIX]    <fix>
[REPORT] <what_to_report>
[DETAIL] <one line per detail>
```

- Pad sentinels to 9 characters, indent continuation lines 9 spaces, and omit empty fields.
- Text mode prints the result on stdout and advisories on stderr, warnings before notices, errors last. JSON mode prints one object on stdout: `{"code", "level", "message", "exit_code", "advisory"}` per advisory, collected under `errors` and `notices`, or `{"error": {...}}` when the command fails outright.
- A tool call returns the rendered error block as its error text, or appends warning and notice blocks to its result text.
- HTTP errors use RFC 7807 with `title` = code; the server decides whether to expose `advisory`.
- Lower an `ERROR` from third-party extension code that must not fail the operation to `WARNING`. A quiet mode hides notices only.

Run `fix` without asking only in `AUTO`; in `INTERACTION` after approval; in
`CONTINUE` and `NOTE` when the user asks. A transport adapter never runs it.
