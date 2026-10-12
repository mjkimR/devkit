# devkit.advisory

Python implementation of the **Agent Advisory Protocol** plus the built-in `advisory` bundle that installs its guide in consumer repositories.

The protocol itself (levels, block format, fields, mode derivation, `[ACTION]` texts, structured output) is specified in [Agent Advisory Protocol](protocol.md); where advisories sit in a command's output is specified in [Agent-First Output](../architecture/agent-output.md). This page is the quick reference.

## Scope

This module implements the Agent Advisory Protocol and nothing else. It is not a home for general agent-facing features.

- **In scope**: advisories at every level: errors (`[ERROR]`, a failure whose mode directs the agent's next step), warnings (`[WARN]`, `CONTINUE`) and notices (`[NOTICE]`, `NOTE`); their rendering as sentinel blocks, JSON and RFC 7807.
- **Out of scope**: logs (`[INFO]`, `logging`, `-v`) and CLI plumbing (options, printing, exit handling) live in `devkit.core.cli`; anything that is not this protocol belongs in another module.

## Contents

- **Runtime**: `devkit.advisory` (standard library only; the lowest layer of `devkit`, importing no other devkit module). Every other devkit module raises `AdvisoryError` subclasses and returns warnings and notices as `AdvisoryError` instances at a lower level; see [Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms).
- **Bundle** `advisory` (`default_preset = "core"`), built into `devkit` with `auto_select = true` and therefore selected by default:

| Preset | Assets | For |
| --- | --- | --- |
| `core` | `agent-advisory` (language-agnostic protocol and authoring rules) | Any repository |
| `python` | `agent-advisory` + `agent-advisory-python` (library guide) | Python repositories using `devkit.advisory` |

## Library

| Name | What it is |
| --- | --- |
| `AdvisoryError` | Exception carrying an advisory: `message`, `*details`, and the keyword fields `code`, `level`, `actor`, `retry`, `guardrail`, `input_error`, `retry_after`, `fix`, `what_to_report`, `target_files`, `brief`, `exit_code`. Each can be a class-level default on a subclass; a keyword other than `None` overrides it per instance. |
| `AdvisoryError.with_level(level, *, brief=None)` | A copy of the error at another level (same class, code and fields; `exit_code` `OK` below `ERROR`): an error reported as a warning or notice where it does not fail the command. |
| Factories | `invalid_input` (`INPUT_ERROR`), `blocked` (`BLOCKED`), `auto_fix` (`AUTO`), `interaction` (`INTERACTION`): classmethods, so `MyError.blocked(...)` returns `MyError`. |
| `AdvisoryFields` | `TypedDict` of the keyword fields, for subclasses that add constructor arguments (`**fields: Unpack[AdvisoryFields]`). |
| `Advisory` | Frozen dataclass of the fields with the derived `mode`, `lines(message)` and `to_dict()`. |
| `Level` | `ERROR`, `WARNING`, `NOTICE`. |
| `ActionMode` | `AUTO`, `INTERACTION`, `DEFER`, `BLOCKED`, `HALT`, `MAINTENANCE`, `INPUT_ERROR`, `CONTINUE`, `NOTE`. |
| `Actor`, `Retry` | Error fields: `TOOL`/`USER`/`DEVELOPER`/`NONE`; `SAFE`/`AFTER_FIX`/`UNSAFE`. |
| `ExitCode` | `OK = 0`, `FINDINGS = 1`, `ERROR = 2`. |
| `ACTION_TEXT` | The canonical directive text per `ActionMode`. |
| `as_advisory_error(exc)`, `render_error(exc)` | Pass an `ERROR`-level `AdvisoryError` through; adapt anything else, a warning or notice that was raised included, to `UNEXPECTED_ERROR` (`MAINTENANCE`). |

Rendering and serialization:

- `error.lines()` / `error.render()`: the sentinel block (`[ERROR]`, `[WARN]` or `[NOTICE]` headline by level) for stderr or an MCP tool result.
- `error.to_dict(include_advisory=True)`: `{code, level, message, exit_code, advisory}`.
- `error.to_problem_details(status=..., type_base=...)`: RFC 7807 body, for errors. `status` is the HTTP status chosen by the caller; the library never maps codes or exit codes to statuses.

A warning or notice is an `AdvisoryError` whose `level` is `WARNING` or `NOTICE`, declared on a subclass (`level = Level.NOTICE`) or produced with `with_level`. It is collected and returned, never raised.

## Python repositories

Use the library at runtime and select the Python preset of the guide:

```bash
uv add devkit
uv run devkit add advisory:python
```

## Other repositories

Only the guide is needed. `devkit sync` deploys the `core` preset by default:

```bash
uvx --from devkit devkit sync
```

Opt out with `[presets] advisory = false` in `.devkit/config.toml` (or `devkit remove advisory`). The runtime module is inert unless imported.

## Specification and mirrors

[protocol.md](protocol.md) is canonical. The `agent-advisory` instruction is its consumer-facing mirror (the protocol for any language) and `agent-advisory-python` documents this library for consumer repositories; both are kept in step with the specification, and a test keeps the `[ACTION]` texts in the guide identical to `ACTION_TEXT`.

## Python API notes

- Positional details are converted to `str`, so `to_dict()` and `to_problem_details()` are always JSON-serializable.
- The factories keep the subclass's defaults for the fields they do not set.
- `actor`, `retry`, `guardrail`, `input_error` and `retry_after` are ignored below `ERROR`; the mode of a warning is `CONTINUE` and of a notice `NOTE`.
- `brief` only matters for a notice without `fix`: it omits the `[ACTION]` line.
