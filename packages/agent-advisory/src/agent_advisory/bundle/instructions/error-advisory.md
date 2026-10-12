---
name: error-advisory
description: Read before authoring CLI commands, tool or API errors, rule violations, or advisory envelopes. Defines the Agent Advisory Protocol format, ActionMode selection (HALT vs INPUT_ERROR vs BLOCKED), and deterministic retry directives.
---

# Error handling and the Agent Advisory Protocol

Apply these conventions when authoring CLI commands, deterministic rules, validation, MCP tools, or any error an AI agent will read. Errors follow the **Agent Advisory Protocol** so that agents act on explicit directives instead of guessing, improvising workarounds, or retrying in loops.

## Core protocol format

Render errors as sentinel lines on standard error (or as the text of a tool error result):

```text
[ERROR]  (<CODE>) <Concise description of what failed>
[ACTION] <MODE> — <Explicit behavioral directive for the agent>
         <Continuation lines indented 9 spaces>
[WHEN]   Not before: <time or duration>           (only when retry_after is set)
[TARGET] <File path, flag, or argument under inspection>
[FIX]    <Concrete command or syntax change that remediates the issue>
[REPORT] <What must be communicated to the user>
[DETAIL] <Diagnostic context; one line per detail>
```

Omit a line when its field is empty. `[ERROR]` and `[ACTION]` are always present.

## Advisory fields

| Field | Meaning |
| --- | --- |
| `code` | Stable identifier (`UPPER_SNAKE_CASE`) that names the error without string matching. Default `GENERAL_ERROR`. |
| `actor` | Who takes the next step: `TOOL` (the agent itself runs the fix), `USER` (a human decides), `DEVELOPER` (code or input must be edited), `NONE` (nobody right now). |
| `retry` | `SAFE` (retry unchanged is safe), `AFTER_FIX` (safe only after the fix), `UNSAFE` (retry risks corruption or duplicate effects). |
| `guardrail` | `true` when a deliberate policy refused the operation. |
| `input_error` | `true` when a flag, argument, or input file is malformed. |
| `retry_after` | Earliest retry time or duration (for `DEFER`). |
| `fix` | Exact, copy-pasteable command or edit. |
| `what_to_report` | Summary or question the agent must relay to the user. |
| `target_files` | Exact files, flags, or `path:line:col` locations involved. |
| `details` | Diagnostic lines. |

Process exit codes: `0` OK, `1` failed, `2` incomplete (for example, rule violations remain), `64` usage error.

## Mode derivation

The mode is never set directly; it is derived from the fields. The first matching rule wins:

1. `input_error` → `INPUT_ERROR`
2. `guardrail` → `BLOCKED`
3. `actor = DEVELOPER` → `MAINTENANCE`
4. `retry = UNSAFE` → `HALT`
5. `actor = TOOL` → `AUTO`
6. `actor = USER` → `INTERACTION`
7. `retry = SAFE` → `DEFER`
8. otherwise → `HALT`

Choose fields by asking which directive the agent must follow, then confirm the derived mode matches.

## The retry directive principle: scoped and conditional prohibition

Agents exhibit two failure modes when they meet errors:

1. **Infinite blind retries**: repeating the identical command without changing inputs or state.
2. **Destructive side-questing**: inventing bypass flags (for example `--force`), editing rules to pass, or finishing the job by hand outside the tool.

To prevent both without paralyzing the agent:

- **Prohibit blind retries deterministically**: state that retrying unchanged input or state fails identically.
- **Never use an unconditional "Do not retry" for fixable input errors**: when the cause is a typo or malformed file, an absolute prohibition makes the agent either freeze or disobey. Direct it to correct the `[TARGET]` and rerun.
- **Never use probabilistic phrasing**: do not write "retrying will likely fail" or "재시도해도 실패할 것 같다". Hedged wording invites guessing and "one more try". Directives are deterministic and conditional on fixing the cause.

## Action modes

The `[ACTION]` text is canonical. Implementations render exactly these directives so that every tool speaks with one voice.

### `INPUT_ERROR`: invalid arguments, syntax, or user files

- **Use for**: malformed flags or options, missing required arguments, YAML/JSON parse errors in user-supplied files.
- **Set**: `input_error = true`, `actor = DEVELOPER`, `retry = AFTER_FIX`, and `target_files` naming the flag, file, or line.

```text
INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
              fail identically. Correct the flag, argument, or input file before rerunning.
```

### `HALT`: critical state hazard or corruption risk

- **Use for**: half-applied mutations, lock conflicts, possible state corruption, unrecoverable filesystem hazards. Reserved **strictly** for cases where further execution can damage state.
- **Never use for** input typos or fixable syntax errors; use `INPUT_ERROR`.
- **Set**: `retry = UNSAFE` with `actor` `NONE` or `TOOL`.

```text
HALT — Unsafe to retry. Execution stopped to prevent state corruption.
       Report what happened, including anything left half-done. Do not retry or finish by hand.
```

### `BLOCKED`: deliberate guardrail or policy refusal

- **Use for**: protected branches, out-of-scope edits, workflow or architecture rule refusals.
- **Set**: `guardrail = true`. `fix` may name the sanctioned exception mechanism, such as an ignore comment that requires a justification.

```text
BLOCKED — A deliberate guardrail refused this. Report it and stop.
          Do not propose or apply a way around it; changing the rule is the
          user's decision, not a fix.
```

### `AUTO`: deterministic machine fix available

- **Use for**: a safe, idempotent remediation command exists (formatter, cache rebuild, regenerate lock).
- **Set**: `actor = TOOL`, `retry = AFTER_FIX` (or `SAFE`), and `fix` with the exact command.

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
              [TARGET] names the affected files.
```

### `DEFER`: not an error; retry later

- **Use for**: rate limits, external jobs still running, scheduled windows.
- **Set**: `actor = NONE`, `retry = SAFE`, and `retry_after`.

```text
DEFER — Nothing is broken and nothing here is yours to fix.
        Do not retry now. Report the cause and when it can be retried.
```

## Structured output

Machine channels carry the same envelope as data:

- **JSON**: `{"code", "message", "exit_code", "advisory": {code, mode, actor, retry, guardrail, input_error, retry_after, fix, what_to_report, target_files, details}}`.
- **HTTP (RFC 7807)**: `{"type", "title": <code>, "status": <HTTP status>, "detail": <message>, "code", "advisory"}`. `type` is `<documentation base URI>/<code>` or `about:blank`. The server decides whether to expose `advisory` (for example, only on authenticated or internal APIs); request headers never enable it.
- **MCP tools**: return the rendered sentinel block as the error result text.

A consumer never executes `fix` automatically outside `AUTO` (and `INTERACTION` after approval). A transport adapter never executes `fix` on the agent's behalf.

## Field authoring checklist

When writing an error in any language or rule format:

- [ ] **`[ERROR]`**: Does `code` uniquely identify the error without string matching?
- [ ] **`[ACTION]`**: Does the derived mode match the intended directive? Does it distinguish a blind retry from a corrected rerun?
- [ ] **`[TARGET]`**: Does it point to the exact file path, flag name, or line?
- [ ] **`[FIX]`**: If remediation is possible, is it exact and copy-pasteable?
- [ ] **`[REPORT]`**: If the user must decide, is the question or summary clear?
- [ ] **Wording**: Is every directive deterministic, with no "likely" or "might"?
