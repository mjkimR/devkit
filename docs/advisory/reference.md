# devkit.advisory

Python implementation of the [Agent Advisory Protocol](protocol.md), shipped as the `devkit-advisory` distribution, plus the built-in `advisory` bundle of `devkit` that installs its guide in consumer repositories. Where advisories sit in a command's output is specified in [Agent-First Output](../architecture/agent-output.md).

## Scope

This module implements the Agent Advisory Protocol and nothing else.

- **In scope**: advisories at every level (errors, warnings, notices) and their rendering as sentinel blocks, JSON and RFC 7807.
- **Out of scope**: logs (`[INFO]`, `logging`, `-v`) and CLI plumbing (options, printing, exit handling) live in `devkit.core.cli`; anything that is not this protocol belongs in another module.

## Contents

- **Runtime**: `devkit.advisory` in the `devkit-advisory` distribution (`packages/devkit-advisory/`): standard library only, no entry points, and the lowest layer of `devkit` (it imports no other devkit module; tests in both packages enforce this). `devkit-agt` depends on the same version, so the module is present wherever `devkit` is. `error.py` (`AdvisoryError`), `types.py` (`ExitCode`, `Level`, `ActionMode`, `Actor`, `Retry`), `advisory.py` (`Advisory`, mode derivation, `ACTION_TEXT`, the block sentinels `HEADLINE`, `FIELDS` and `CONTINUATION`, rendering). Every other devkit module raises `AdvisoryError` subclasses and returns warnings and notices as `AdvisoryError` instances at a lower level ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)).
- **Bundle** `advisory` (`devkit.advisory_guide`, `bundle/`, `default_preset = "core"`), built into `devkit` (not `devkit-advisory`, so a runtime environment carries no agent content) with `auto_select = true` and therefore selected by default:

| Preset | Assets | For |
| --- | --- | --- |
| `core` | `agent-advisory` (language-agnostic protocol and authoring rules) | Any repository |
| `python` | `agent-advisory` + `agent-advisory-python` (library guide) | Python repositories using `devkit.advisory` |

`agent-advisory` is the consumer-facing mirror of [protocol.md](protocol.md) and `agent-advisory-python` documents this library; both are kept in step with the specification, and a test keeps the `[ACTION]` texts in `agent-advisory` identical to `ACTION_TEXT`.

## Library

| Name | What it is |
| --- | --- |
| `AdvisoryError` | Exception carrying an advisory: `message`, `*details`, and the keyword fields `code`, `level`, `actor`, `retry`, `guardrail`, `input_error`, `retry_after`, `fix`, `what_to_report`, `target_files`, `brief`, `exit_code`. Each can be a class-level default on a subclass; a keyword other than `None` overrides it per instance. Positional details are converted to `str`, so `to_dict()` and `to_problem_details()` are always JSON-serializable. An empty `code` becomes `GENERAL_ERROR`; a `target_files` string is one target. An `ERROR` with `exit_code` `OK`, or whose mode is `AUTO` without `fix`, raises `ValueError`. Instances pickle and copy without calling `__init__`, so subclasses with required constructor arguments do too. |
| `AdvisoryError.with_level(level, *, brief=None)` | A copy of the error at another level (same class, code and fields; `exit_code` `OK` below `ERROR`, kept for an `ERROR` copy of an error, the class default for an `ERROR` copy of a warning or notice): an error reported as a warning or notice where it does not fail the command. |
| Factories | `invalid_input` (`INPUT_ERROR`), `blocked` (`BLOCKED`), `auto_fix` (`AUTO`), `interaction` (`INTERACTION`): classmethods, so `MyError.blocked(...)` returns `MyError`. They set every field that decides the mode (`level` `ERROR`, `actor`, `retry`, `guardrail`, `input_error`) and keep the subclass's defaults for the others. |
| `AdvisoryFields` | `TypedDict` of the keyword fields, for subclasses that add constructor arguments (`**fields: Unpack[AdvisoryFields]`). |
| `Advisory` | Frozen dataclass of the fields with the derived `mode`, `shows_action` (whether the block carries `[ACTION]`), `lines(message)` and `to_dict()`. |
| `Level` | `ERROR`, `WARNING`, `NOTICE`. |
| `ActionMode` | `AUTO`, `INTERACTION`, `DEFER`, `BLOCKED`, `HALT`, `MAINTENANCE`, `INPUT_ERROR`, `CONTINUE`, `NOTE`. |
| `Actor`, `Retry` | Error fields: `TOOL`/`USER`/`DEVELOPER`/`NONE`; `SAFE`/`AFTER_FIX`/`UNSAFE`. |
| `ExitCode` | `OK = 0`, `FINDINGS = 1`, `ERROR = 2`. |
| `ACTION_TEXT` | The canonical directive text per `ActionMode`. |
| `HEADLINE`, `FIELDS`, `CONTINUATION` | The block grammar of [protocol, section 3](protocol.md#3-block-format), for code that parses rendered blocks (`devkit.compact` does): `HEADLINE` maps each `Level` to its 9-character headline sentinel (`"[ERROR]  "`, `"[WARN]   "`, `"[NOTICE] "`), `FIELDS` is the tuple of field sentinels in rendering order (`"[ACTION] "` to `"[DETAIL] "`), and `CONTINUATION` the 9-space indentation of a value's further lines. Every rendered line starts with one of them. A new field sentinel is added to `FIELDS`. |
| `as_advisory_error(exc)`, `render_error(exc)` | Pass an `ERROR`-level `AdvisoryError` through; adapt anything else, a warning or notice that was raised included, to `UNEXPECTED_ERROR` (`MAINTENANCE`). A foreign exception's message is `<ExceptionType>: <text>` (the type alone when the text is empty). |

Rendering and serialization:

- `error.lines()` / `error.render()`: the sentinel block (`[ERROR]`, `[WARN]` or `[NOTICE]` headline by level) for stderr or an MCP tool result.
- `error.to_dict(include_advisory=True)`: `{code, level, message, exit_code, advisory}`; `advisory` holds what the block shows, the `[ACTION]` text as `action` included, and omits empty fields ([protocol, section 9](protocol.md#9-structured-output)).
- `error.to_problem_details(status=..., type_base=...)`: RFC 7807 body, for errors. `status` is the HTTP status chosen by the caller; the library never maps codes or exit codes to statuses.

A warning or notice is an `AdvisoryError` whose `level` is `WARNING` or `NOTICE`, declared on a subclass (`level = Level.NOTICE`) or produced with `with_level`; it is collected and returned, never raised. Field semantics per level (ignored failure fields, `brief`) are in [protocol, section 4](protocol.md#4-fields).

## Installing

A library or service that raises and renders advisories at runtime depends on `devkit-advisory` alone; its
development tooling adds `devkit` and selects the Python preset of the guide:

```bash
# Runtime: devkit.advisory, standard library only
uv add "devkit-advisory @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-advisory"
# Tooling (instead of the runtime-only install): requires the same advisory version
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit add advisory:python
```

Neither is on a package index: name both wheels by URL, or both Git sources at the same `rev`
(`subdirectory = "packages/devkit"` and `"packages/devkit-advisory"`); see the
[root README](../../README.md#using-devkit-in-another-project).

Other repositories need only the guide, which `devkit sync` deploys with the `core` preset by default:

```bash
uvx --from devkit devkit sync
```

Opt out with `[presets] advisory = false` in `.devkit/config.toml` (or `devkit remove advisory`). The runtime module is inert unless imported.

## Compatibility

`devkit-advisory` is the one devkit API other repositories run in production, so it is a versioned contract: within
`0.x` a breaking change to a name in the [library table](#library), a field, a mode derivation, an `[ACTION]` text or
the `to_dict` and RFC 7807 shapes needs a minor version bump, released in lockstep with `devkit` (devkit pins the
exact version). Adding a field or a name is not breaking.
