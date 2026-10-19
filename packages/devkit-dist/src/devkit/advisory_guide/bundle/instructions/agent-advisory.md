---
name: agent-advisory
description: Read before authoring CLI commands, tool or API errors, warnings, notices, rule violations or advisory envelopes.
---

# The Agent Advisory Protocol

Every error, warning and notice an AI agent reads (CLI commands, rules, validation, MCP tools) follows this protocol, so agents act on explicit directives instead of guessing, improvising workarounds or retrying in loops.

## Principles

- **Direct, do not describe.** `[ACTION]` says what to do next; the other lines supply what that step needs.
- **Deterministic wording.** Directives never hedge ("likely", "might"); they forbid a blind retry and a workaround, not a rerun after the cause is fixed.
- **Stable codes.** Every advisory has an `UPPER_SNAKE_CASE` code; callers branch on the code, never on message text.
- **Context budget.** Emit an advisory only when it changes the agent's next step or must reach the user; other diagnostics are logs, hidden unless verbose.
- **Channels.** In text mode the result goes to stdout as one-line sentinels and advisories to stderr; in JSON mode one JSON object on stdout carries both and nothing goes to stderr. Each advisory is printed once.

## Levels

| Level | Headline | The operation | Exit code | `[ACTION]` |
| --- | --- | --- | --- | --- |
| `ERROR` | `[ERROR]` | did not do its job, or refused | the error's (`1` negative result, `2` could not run) | always; mode derived from the fields |
| `WARNING` | `[WARN]` | succeeded; the user must learn or decide something | unchanged (a strict mode may turn `0` into `1`) | always; mode `CONTINUE` |
| `NOTICE` | `[NOTICE]` | succeeded; something is worth knowing | unchanged | recommended; mode `NOTE`; may be omitted (`brief`) |

Choose the level first:

1. The command could not do its job, or a check it ran found a negative result: `ERROR`. A refusal is never a warning.
2. It succeeded, and the user must learn or decide something afterwards: `WARNING`.
3. It succeeded, and the agent may want to know why the result looks as it does or what it could do next: `NOTICE`.
4. Nobody needs to act and nothing needs explaining: no advisory; log it at most.

The same condition can be an `ERROR` in one command and a `WARNING` in another; it keeps its code.

## Block format

Render advisories as sentinel lines on standard error (or as the text of a tool result):

```text
<HEADLINE> (<CODE>) <Concise description>
[ACTION] <MODE> — <Behavioral directive>
         <Continuation lines indented 9 spaces>
[WHEN]   Not before: <time or duration>           (ERROR only, when retry_after is set)
[TARGET] <File path, flag, or argument involved>
[FIX]    <Concrete command or edit that remediates the issue>
[REPORT] <What must be communicated to the user>
[DETAIL] <Diagnostic context; one line per detail>
```

Each sentinel is padded to 9 characters; the headline always carries the code, then the message: one concise sentence. A notice omits `[ACTION]` only when it is `brief` and has no `[FIX]`, since a fix without a directive reads as an instruction to run it. Omit any other line whose field is empty. A multi-line value continues on lines indented 9 spaces; a block never contains a blank line, colour, emoji or Markdown.

## Fields

| Field | Levels | Meaning |
| --- | --- | --- |
| `code` | all | Stable identifier (`UPPER_SNAKE_CASE`). Default `GENERAL_ERROR`, which an empty code also becomes. |
| `level` | all | `ERROR` (default), `WARNING` or `NOTICE`. |
| `actor` | error | Who takes the next step: `TOOL` (the agent itself runs the fix), `USER` (a human decides), `DEVELOPER` (code or input must be edited), `NONE` (nobody right now). |
| `retry` | error | `SAFE` (retry unchanged is safe), `AFTER_FIX` (safe only after the fix), `UNSAFE` (retry risks corruption or duplicate effects). |
| `guardrail` | error | `true` when a deliberate policy refused the operation. |
| `input_error` | error | `true` when a flag, argument, or input file is malformed. |
| `retry_after` | error | Earliest retry time or duration (for `DEFER`). |
| `fix` | all | Exact, copy-pasteable command or edit. |
| `what_to_report` | all | Summary or question the agent must relay to the user. |
| `target_files` | all | Exact files, flags, or `path:line:col` locations involved. |
| `details` | all | Diagnostic lines. |
| `brief` | notice | `true` omits `[ACTION]` when there is no `fix`. |

An error never exits `0`, even in `DEFER` or `INTERACTION` mode: the operation did not happen. A command whose job is to report a state (a workflow waiting for a person) reports it as its result and exits `0`.

## Mode derivation

The mode is never set directly; it is derived. The first matching rule wins:

0. `level = WARNING` → `CONTINUE`; `level = NOTICE` → `NOTE`
1. `input_error` → `INPUT_ERROR`
2. `guardrail` → `BLOCKED`
3. `actor = DEVELOPER` → `MAINTENANCE`
4. `retry = UNSAFE` → `HALT`
5. `actor = TOOL` → `AUTO`
6. `actor = USER` → `INTERACTION`
7. `retry = SAFE` → `DEFER`
8. otherwise → `HALT`

Choose fields by asking which directive the agent must follow, then confirm the derived mode matches.

## Action modes

The `[ACTION]` text is canonical: implementations render exactly these directives.

### `INPUT_ERROR`: invalid arguments, syntax, or user files

- **Use for**: malformed flags or options, missing required arguments, YAML/JSON/TOML parse errors in user-supplied files.
- **Set**: `input_error = true`, `actor = DEVELOPER`, `retry = AFTER_FIX`, and `target_files` naming the flag, file, or line.

```text
INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
              fail identically. Correct the flag, argument, or input file before rerunning.
```

### `HALT`: critical state hazard or corruption risk

- **Use for**: half-applied mutations, lock conflicts, possible state corruption: **only** where further execution can damage state.
- **Never use for** input typos or fixable syntax errors; use `INPUT_ERROR`.
- **Set**: `retry = UNSAFE` with `actor` `NONE` or `TOOL`.

```text
HALT — Unsafe to retry. Execution stopped to prevent state corruption.
       Report what happened, including anything left half-done. Do not retry or finish by hand.
```

### `BLOCKED`: deliberate guardrail or policy refusal

- **Use for**: protected branches, out-of-scope edits, workflow or architecture rule refusals, commit gate refusals.
- **Set**: `guardrail = true`. `fix` may name the sanctioned exception mechanism, such as an ignore comment that requires a justification.

```text
BLOCKED — A deliberate guardrail refused this. Report it and stop.
          Do not propose or apply a way around it; changing the rule is the
          user's decision, not a fix.
```

### `AUTO`: deterministic machine fix available

- **Use for**: a safe, idempotent remediation command exists (formatter, cache rebuild, regenerate lock).
- **Set**: `actor = TOOL`, `retry = AFTER_FIX` (or `SAFE`), and `fix` with the exact command. `fix` is required: the directive runs it.

```text
AUTO — Run the [FIX] command once, then retry the operation once.
       This is the only mode that authorizes a retry. Stop after it either way.
```

### `INTERACTION`: human decision or permission required

- **Use for**: ambiguous intent, drift that needs confirmation, destructive operations that need sign-off, missing credentials.
- **Set**: `actor = USER`, `retry = AFTER_FIX`, `what_to_report` with the question, and `fix` with the command to run once the user agrees. Do not use `retry = UNSAFE` here: it derives `HALT`, which forbids that follow-up.

```text
INTERACTION — Stop and ask the user. Do not retry, and do not
              improvise a way around this. [FIX], when present, is the command
              for once they agree.
```

### `MAINTENANCE`: internal bug or tool defect

- **Use for**: invariant violations, unexpected exceptions, unsupported toolchain states. Unhandled exceptions are adapted to `UNEXPECTED_ERROR` with `actor = DEVELOPER`, `retry = UNSAFE`.
- **Set**: `actor = DEVELOPER`, with `target_files` naming the affected code when known.

```text
MAINTENANCE — A codebase defect or tool failure occurred.
              Report it and stop; repairing the code/tool is a separate task.
              [TARGET], when present, names the affected files.
```

### `DEFER`: not an error; retry later

- **Use for**: rate limits, external jobs still running, a lock another process holds, scheduled windows: the operation did not happen (one that did is at most a `NOTICE`).
- **Set**: `actor = NONE`, `retry = SAFE`, and `retry_after`.

```text
DEFER — Nothing is broken and nothing here is yours to fix.
        Do not retry now. Report the cause and when it can be retried.
```

### `CONTINUE`: a warning; the operation succeeded and the user needs to know

- **Use for**: a hand-edited file left behind, an override hiding upstream changes, files the tool ignores where they may cause harm, a post-operation hook that failed after the work was done.
- **Set**: `level = WARNING`, `what_to_report` with what the user must learn or decide, and `fix` with the command for when they ask.

```text
CONTINUE — The operation succeeded; this does not block it. Do not retry
           or undo it. Tell the user about it ([REPORT] when present); run [FIX]
           only when they ask for it.
```

### `NOTE`: a notice; the operation succeeded and this is worth knowing

- **Use for**: an available but unused option, a check skipped because its input does not exist yet, a tracked file rewritten for a benign reason, a transition that is ready.
- **Set**: `level = NOTICE`; `fix` when there is an obvious follow-up, otherwise `brief = true`, since the directive would only cost context.

```text
NOTE — For awareness only; nothing needs doing now. Continue. Mention it
       when it bears on the task; run [FIX] only when the user asks for it.
```

## Warnings and notices in practice

- **Never raised.** Return a warning or notice with the result (under `notices`), printed after the result; a raised one is a defect, reported as `UNEXPECTED_ERROR`.
- **One advisory per condition.** Name all affected items in one advisory, not one block per file.
- **Lasting conditions.** A condition the user must act on is a warning on every run until resolved; one that asks for nothing is a notice reported when it appears or changes, then left to data (a JSON field, a list command). A condition the user decided on is never announced again.
- **Warnings first.** On stderr, warnings precede notices and errors come last; JSON keeps the collected order.
- **Targets are files.** `[TARGET]` names a file, a flag or a `path:line:col` location; identifiers such as rule IDs belong in the message or `[DETAIL]`.
- **Fixes are runnable.** `[FIX]` is never a template with placeholders; for several candidates, name a listing command and give one exact command per candidate in `[DETAIL]`.
- **Extension points.** An `ERROR` received from third-party code that must not fail the operation (a post-operation hook) is lowered to `WARNING`.
- **Quiet output.** A quiet mode hides notices, never warnings or errors; JSON always carries every advisory.

## Structured output

Machine channels carry the same envelope as data:

- **JSON**: `{"code", "level", "message", "exit_code", "advisory": {...}}`. `advisory` carries what the block shows: `code`, `level`, `mode`, the `[ACTION]` text as `action` when shown, the error-only fields for an error, and the other fields when set. A result lists collected errors under `errors` and warnings and notices under `notices`; a command that fails outright prints `{"error": {...}}`.
- **HTTP (RFC 7807)**: errors only: `{"type", "title": <code>, "status": <HTTP status>, "detail": <message>, "code", "advisory"}`, `type` being `<documentation base URI>/<code>` or `about:blank`. The server, never a request header, decides whether to expose `advisory`. Warnings and notices travel in the successful response body.
- **MCP tools**: a failed call returns the rendered error block as the error result text; a successful call appends its rendered warning and notice blocks after the result text.

A consumer never executes `fix` automatically outside `AUTO` (and `INTERACTION` after approval, `CONTINUE`/`NOTE` when the user asks). A transport adapter never executes `fix` on the agent's behalf.
