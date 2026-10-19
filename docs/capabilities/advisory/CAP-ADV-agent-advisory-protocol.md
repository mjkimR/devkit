---
id: CAP-ADV-agent-advisory-protocol
title: "Agent Advisory Protocol"
summary: "Structured error, warning, and notice protocol with machine-actionable directives."
area: advisory
status: active
created_at: 2026-10-17
---

# [CAP-ADV-agent-advisory-protocol] Agent Advisory Protocol

The Agent Advisory Protocol is how a tool tells an AI agent what happened **and what to do next**. Every error, warning and notice a `devkit` command reports is an advisory: a block of sentinel lines on stderr (or the same envelope as JSON) whose `[ACTION]` directive the agent follows instead of guessing, improvising workarounds or retrying in loops.

This is the canonical specification. `devkit.advisory` implements it ([reference](../../development/reference/advisory.md)); the `agent-advisory` and `agent-advisory-python` instructions of the built-in `advisory` bundle are its consumer-facing mirrors, kept in step with it. Where an advisory sits among the rest of a command's output is specified in `ARCH-08-1-agent-output`.

## 1. Principles

1. **Direct, do not describe.** An advisory exists to change the agent's next step. Its `[ACTION]` says what to do; the other lines supply what that step needs (the file, the command, the question for the user).
2. **Deterministic wording.** Directives never hedge. "Retrying will likely fail" invites one more try; "retrying unchanged fails identically" does not.
3. **Scoped prohibition.** Agents fail in two ways: blind retries of an identical command, and destructive side-quests (inventing `--force`, editing a rule to pass, finishing the job by hand). Directives forbid both, conditionally on the cause, without freezing the agent when the fix is in its reach (see [section 7](#7-the-retry-directive-principle)).
4. **Stable codes.** Every advisory has an `UPPER_SNAKE` code. Callers branch on the code (or the derived mode), never on message text.
5. **Context budget.** An advisory is emitted only when it changes the agent's next step or must reach the user; diagnostics that do neither are logs, not advisories (section 2).

## 2. Levels

Every advisory has a **level**. The level decides whether the operation failed; the mode (section 5) decides what the agent does about it.

| Level | Headline | The operation | Exit code | `[ACTION]` |
| --- | --- | --- | --- | --- |
| `ERROR` | `[ERROR]` | did not do its job, or refused | the error's `exit_code` (`1` or `2`, never `0`) | always; mode derived from the fields |
| `WARNING` | `[WARN]` | succeeded, but something needs the user's attention | unchanged (`--strict` raises `0` to `1`) | always; mode `CONTINUE` |
| `NOTICE` | `[NOTICE]` | succeeded; something is worth knowing | unchanged | recommended; mode `NOTE`; may be omitted (`brief`) |

There is no `INFO` level. Information that neither changes the agent's next step nor needs to reach the user is a log line (`[INFO]`, shown only under `-v`; see `ARCH-08-1-agent-output`).

Choosing a level:

1. The command could not do its job, or a check it ran found a negative result (violations, a refused commit, a needed sync): **`ERROR`**. A refusal is never a warning.
2. The command did its job, and the user must learn about something or decide something afterwards (a hand-edited file left behind, an override hiding upstream changes, a hook that failed after the files were written): **`WARNING`**.
3. The command did its job, and the agent may want to know why the result looks as it does or what it could do next (a newly installed bundle not selected yet, a check skipped because its input does not exist yet, a tracked file rewritten with a new tool version): **`NOTICE`**.
4. Nobody needs to act and nothing needs explaining: no advisory; log it at most.

The same condition can sit at different levels in different commands: override drift is an `ERROR` in `devkit status` (a report that lists problems) and a `WARNING` after `devkit sync` (which succeeded). It keeps its code: the implementation copies the error at the lower level (`with_level` in Python) rather than defining a second code.

## 3. Block Format

An advisory renders as sentinel lines. Each sentinel is padded to 9 characters, so values align and a value that spans several lines continues on lines indented 9 spaces under its sentinel. Every line of a block therefore either starts with a sentinel or belongs to the one above it.

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

| Headline | Level |
| --- | --- |
| `[ERROR]  ` | `ERROR` |
| `[WARN]   ` | `WARNING` |
| `[NOTICE] ` | `NOTICE` |

Rules:

- The headline is always present and always carries the code.
- `[ACTION]` is always present for `ERROR` and `WARNING`. For `NOTICE` it is present unless the notice is `brief` **and** has no `fix`: a `[FIX]` line without a directive would read as an instruction to run it.
- Every other line is omitted when its field is empty or blank, and appears in the order above.
- Blank lines inside a value are dropped: a block never contains a blank line, and a value's first line is its first non-blank one.
- Blocks follow each other without blank lines; the next headline starts the next block.
- No colour, no emoji, no Markdown.

An error:

```text
[ERROR]  (RULES_CONFIG_INVALID) .devkit/config.toml: [rules] phase override for RULE-x must be a string
[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
         fail identically. Correct the flag, argument, or input file before rerunning.
[TARGET] .devkit/config.toml
[FIX]    Set [rules.phases] RULE-x = "linter"
```

A warning:

```text
[WARN]   (ORPHAN_LEFT) left modified file in place: .devkit/managed/starter/old.md (no longer managed)
[ACTION] CONTINUE — The operation succeeded; this does not block it. Do not retry
         or undo it. Tell the user about it ([REPORT] when present); run [FIX]
         only when they ask for it.
[TARGET] .devkit/managed/starter/old.md
[REPORT] A hand-edited file is no longer managed by devkit; delete or move it
```

A notice, with and without its directive:

```text
[NOTICE] (BUNDLE_UNSELECTED) installed bundles not selected yet: starter
[ACTION] NOTE — For awareness only; nothing needs doing now. Continue. Mention it
         when it bears on the task; run [FIX] only when the user asks for it.
[FIX]    devkit add starter
[DETAIL] devkit add starter  (package devkit-starter; presets daily; default daily)
[NOTICE] (TOOL_VERSION_CHANGED) devkit 0.4.0 -> 0.5.0
```

## 4. Fields

| Field | Levels | Meaning |
| --- | --- | --- |
| `code` | all | Stable identifier (`UPPER_SNAKE_CASE`) that names the condition without string matching. Default `GENERAL_ERROR`, which an empty code also becomes. |
| `level` | all | `ERROR` (default), `WARNING` or `NOTICE`. |
| `actor` | `ERROR` | Who takes the next step: `TOOL` (the agent itself runs the fix), `USER` (a human decides), `DEVELOPER` (code or input must be edited), `NONE` (nobody right now). |
| `retry` | `ERROR` | `SAFE` (retry unchanged is safe), `AFTER_FIX` (safe only after the fix), `UNSAFE` (retry risks corruption or duplicate effects). |
| `guardrail` | `ERROR` | `true` when a deliberate policy refused the operation. |
| `input_error` | `ERROR` | `true` when a flag, argument, or input file is malformed. |
| `retry_after` | `ERROR` | Earliest retry time or duration (for `DEFER`). |
| `fix` | all | Exact, copy-pasteable command or edit. |
| `what_to_report` | all | Summary or question the agent must relay to the user. |
| `target_files` | all | Exact files, flags, or `path:line:col` locations involved. |
| `details` | all | Diagnostic lines. |
| `brief` | `NOTICE` | `true` omits the `[ACTION]` line when there is no `fix`. |

`actor`, `retry`, `guardrail`, `input_error` and `retry_after` describe a failure; they are ignored for `WARNING` and `NOTICE`, whose mode is fixed by the level.

## 5. Mode Derivation

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

Choose the level first, then (for an error) the fields, by asking which directive the agent must follow; confirm the derived mode matches.

## 6. Action Modes

The `[ACTION]` texts below are canonical. Every implementation renders exactly these directives, so every tool speaks with one voice; `devkit.advisory.ACTION_TEXT` holds them, and a test keeps the bundled guide identical to it.

### Error modes

#### `INPUT_ERROR`: invalid arguments, syntax, or user files

- **Use for**: malformed flags or options, missing required arguments, YAML/JSON/TOML parse errors in user-supplied files.
- **Set**: `input_error = true`, `actor = DEVELOPER`, `retry = AFTER_FIX`, and `target_files` naming the flag, file, or line.

```text
INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
              fail identically. Correct the flag, argument, or input file before rerunning.
```

#### `HALT`: critical state hazard or corruption risk

- **Use for**: half-applied mutations, lock conflicts, possible state corruption, unrecoverable filesystem hazards. Reserved **strictly** for cases where further execution can damage state.
- **Never use for** input typos or fixable syntax errors; use `INPUT_ERROR`.
- **Set**: `retry = UNSAFE` with `actor` `NONE` or `TOOL`.

```text
HALT — Unsafe to retry. Execution stopped to prevent state corruption.
       Report what happened, including anything left half-done. Do not retry or finish by hand.
```

#### `BLOCKED`: deliberate guardrail or policy refusal

- **Use for**: protected branches, out-of-scope edits, workflow or architecture rule refusals, a commit gate refusing a commit.
- **Set**: `guardrail = true`. `fix` may name the sanctioned exception mechanism, such as an ignore comment that requires a justification.

```text
BLOCKED — A deliberate guardrail refused this. Report it and stop.
          Do not propose or apply a way around it; changing the rule is the
          user's decision, not a fix.
```

#### `AUTO`: deterministic machine fix available

- **Use for**: a safe, idempotent remediation command exists (formatter, cache rebuild, regenerate lock, `devkit recover`).
- **Set**: `actor = TOOL`, `retry = AFTER_FIX` (or `SAFE`), and `fix` with the exact command. `fix` is required: the directive runs it, so an `AUTO` error without one is refused as a programming error.

```text
AUTO — Run the [FIX] command once, then retry the operation once.
       This is the only mode that authorizes a retry. Stop after it either way.
```

#### `INTERACTION`: human decision or permission required

- **Use for**: ambiguous intent, drift that needs confirmation, destructive operations that need sign-off, missing credentials.
- **Set**: `actor = USER`, `retry = AFTER_FIX`, `what_to_report` with the question, and `fix` with the command to run once the user agrees. Do not use `retry = UNSAFE` here: it derives `HALT`, which forbids that follow-up.

```text
INTERACTION — Stop and ask the user. Do not retry, and do not
              improvise a way around this. [FIX], when present, is the command
              for once they agree.
```

#### `MAINTENANCE`: internal bug or tool defect

- **Use for**: invariant violations, unexpected exceptions, unsupported toolchain states. Unhandled exceptions are adapted to `UNEXPECTED_ERROR` with `actor = DEVELOPER`, `retry = UNSAFE`.
- **Set**: `actor = DEVELOPER`, with `target_files` naming the affected code when known.

```text
MAINTENANCE — A codebase defect or tool failure occurred.
              Report it and stop; repairing the code/tool is a separate task.
              [TARGET], when present, names the affected files.
```

#### `DEFER`: not an error; retry later

- **Use for**: rate limits, external jobs still running, a lock another process holds, scheduled windows.
- **Set**: `actor = NONE`, `retry = SAFE`, and `retry_after`.

```text
DEFER — Nothing is broken and nothing here is yours to fix.
        Do not retry now. Report the cause and when it can be retried.
```

`DEFER` is an error mode: the operation did not happen and has to be run again later. Something that did happen and only deserves mention is a `NOTICE`, not a `DEFER`.

### Non-error modes

#### `CONTINUE`: the operation succeeded; the user needs to know

- **Use for**: every `WARNING`: a hand-edited file left behind, an override hiding upstream changes, files the tool ignores where they may cause harm, a post-operation hook that failed after the work was done.
- **Set**: `level = WARNING`, `what_to_report` with what the user must learn or decide, and `fix` with the command for when they ask.

```text
CONTINUE — The operation succeeded; this does not block it. Do not retry
           or undo it. Tell the user about it ([REPORT] when present); run [FIX]
           only when they ask for it.
```

#### `NOTE`: the operation succeeded; worth knowing

- **Use for**: every `NOTICE`: an available but unused option, a check skipped because its input does not exist yet, a tracked file rewritten for a benign reason, a phase transition that is ready.
- **Set**: `level = NOTICE`; `fix` when there is an obvious follow-up. A notice without `fix` should be `brief = true`: it asks for nothing, so the repeated directive only costs context.

```text
NOTE — For awareness only; nothing needs doing now. Continue. Mention it
       when it bears on the task; run [FIX] only when the user asks for it.
```

## 7. The Retry Directive Principle

To prevent blind retries and destructive side-quests without paralyzing the agent:

- **Prohibit blind retries deterministically**: state that retrying unchanged input or state fails identically.
- **Never use an unconditional "Do not retry" for fixable input errors**: when the cause is a typo or malformed file, an absolute prohibition makes the agent either freeze or disobey. Direct it to correct the `[TARGET]` and rerun.
- **Never use probabilistic phrasing**: do not write "retrying will likely fail" or "this might work now". Directives are deterministic and conditional on fixing the cause.
- **Never let a non-error advisory start work**: `CONTINUE` and `NOTE` forbid running `[FIX]` unasked, because an agent that reads a fix command next to a finished operation tends to run it.

## 8. Warnings and Notices in Practice

- **Never raised.** A warning or notice describes an operation that succeeded, so it is never raised as an exception. A function collects it and returns it with its result (in `notices`); the command prints the result first and the notices after it. A notice that reaches a CLI boundary as an exception is a programming error and is reported as `UNEXPECTED_ERROR`.
- **Extension points.** When a tool collects advisories from third-party code that must not fail the operation (for example post-sync extensions), an `ERROR` it receives is lowered to `WARNING`.
- **One advisory per condition.** Report a condition once per run, naming all affected items in `[TARGET]` or the message, rather than one block per file.
- **Lasting conditions.** A condition that persists across runs is reported by what it asks for. One the user must act on is a `WARNING` and is reported on every run until it is resolved (a stray file, an override behind upstream). One that asks for nothing is a `NOTICE` reported when it appears or changes, not on every run that finds it unchanged (a bundle that became available); afterwards it stays visible as data (a JSON field, a list command). A condition the user decided on (an opted-out bundle) is never announced again.
- **Targets are files.** `[TARGET]` names what the agent would open: a file path, a flag, or a `path:line:col` location. Identifiers such as rule IDs or `bundle:asset` labels belong in the message or `[DETAIL]`.
- **Fixes are runnable.** `[FIX]` is an exact command or edit, never a template with placeholders such as `<bundle>`. When there are several candidates, `[FIX]` names a command that lists them (or the command for the single one), and `[DETAIL]` gives one exact command per candidate.
- **Order and quiet runs.** On stderr, warnings precede notices, each in collected order, and errors come last; JSON keeps the collected order. `-q` hides notices, never warnings or errors; JSON always carries every advisory. See `ARCH-08-1-agent-output`.

## 9. Structured Output

Machine channels carry the same envelope as data:

- **JSON**: `{"code", "level", "message", "exit_code", "advisory": {...}}`. A warning or notice has `exit_code` `0`. `advisory` carries what the block shows and no more, so a JSON reader needs no second channel:
  - always `code`, `level` and `mode`;
  - `action`: the canonical `[ACTION]` text on one line, present exactly when the block shows `[ACTION]` (absent for a `brief` notice without `fix`);
  - for an `ERROR` only: `actor`, `retry`, `guardrail`, `input_error`, and `retry_after` when set;
  - `fix`, `what_to_report`, `target_files` and `details` only when they have a value.

  An absent key means "none". A result lists collected errors under `errors` and warnings and notices under `notices`; a command that fails outright prints `{"error": {...}}` (`ARCH-08-1-agent-output`). A JSON command renders no block on stderr: an agent host that merges the channels would read each advisory twice.
- **HTTP (RFC 7807)**: errors only: `{"type", "title": <code>, "status": <HTTP status>, "detail": <message>, "code", "advisory"}`. `type` is `<documentation base URI>/<code>` or `about:blank`. The server decides whether to expose `advisory` (for example, only on authenticated or internal APIs); request headers never enable it. Warnings and notices travel inside the successful response body, in its `notices`.
- **MCP tools**: a failed call returns the rendered error block as the error result text; a successful call appends its rendered warning and notice blocks after the result text.

A consumer never executes `fix` automatically outside `AUTO` (and `INTERACTION` after approval, `CONTINUE`/`NOTE` when the user asks). A transport adapter never executes `fix` on the agent's behalf.

## 10. Authoring Checklist

When writing an advisory in any language or rule format:

- [ ] **Level**: Did the operation fail or refuse (`ERROR`), succeed with something the user must learn (`WARNING`), or succeed with something worth knowing (`NOTICE`)? Would a log line do?
- [ ] **Headline**: Does `code` uniquely identify the condition without string matching (in Python, `RULE-advisory-unique-code` refuses two unrelated classes declaring one code)? Is the message one concise sentence?
- [ ] **`[ACTION]`**: For an error, does the derived mode match the intended directive and distinguish a blind retry from a corrected rerun?
- [ ] **`[TARGET]`**: Does it point to the exact file path, flag name, or line?
- [ ] **`[FIX]`**: If remediation is possible, is it exact and copy-pasteable?
- [ ] **`[REPORT]`**: If the user must decide or learn something, is the question or summary clear?
- [ ] **Brief**: Is a notice without `[ACTION]` self-explanatory and free of `fix`?
- [ ] **Wording**: Is every directive deterministic, with no "likely" or "might"?
