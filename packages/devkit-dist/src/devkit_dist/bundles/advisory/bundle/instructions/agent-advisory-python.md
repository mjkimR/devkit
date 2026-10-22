---
name: agent-advisory-python
description: Read before raising, returning, rendering or serializing errors, warnings or notices in Python code with devkit.advisory.
---

# Agent Advisory Protocol in Python (`devkit.advisory`)

`devkit.advisory` implements the `agent-advisory` instruction's protocol. Read that instruction first for levels, modes and rendering rules.

The library is standard-library only and ships as `devkit-advisory`. Make runtime code depend on `devkit-advisory`, not on `devkit-dist` or `devkit-agt`.

## Raising errors

At boundaries agents read, raise `AdvisoryError` subclasses, not bare `ValueError`, `RuntimeError` or framework exceptions.

- Set any field as a class-level default on the subclass.
- Pass a keyword argument other than `None` to override a default for one instance.
- Pass positional arguments after the message to add `[DETAIL]` lines.

```python
from devkit.advisory import Actor, AdvisoryError, Retry


class ConfigInvalidError(AdvisoryError):
    code = "CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


raise ConfigInvalidError(
    "config.toml: 'timeout' must be an integer",
    'line 12: timeout = "30s"',  # positional extras become [DETAIL] lines
    target_files=["config.toml:12"],
    fix="Set timeout = 30 in config.toml",
)
```

A code names one condition: it is declared by one class and its subclasses, in their bodies or through `code=` at a call (a subclass may redeclare its base's code). `RULE-advisory-unique-code` checks this in the `python` preset.

For one-off errors, use the factories; they set every field that decides the mode, so a subclass default never changes it:

| Factory | Mode | Fields set |
| --- | --- | --- |
| `AdvisoryError.invalid_input(msg, *details, code=, fix=, target_files=)` | `INPUT_ERROR` | `input_error`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.blocked(msg, *details, code=, fix=, target_files=)` | `BLOCKED` | `guardrail`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.auto_fix(msg, *details, fix=, code=, target_files=)` | `AUTO` | `TOOL`, `AFTER_FIX` |
| `AdvisoryError.interaction(msg, *details, code=, what_to_report=, fix=)` | `INTERACTION` | `USER`, `AFTER_FIX` |

`exit_code` defaults to `ExitCode.ERROR` (`2`); an error reporting a negative result of a check that ran sets `ExitCode.FINDINGS` (`1`). An error with `ExitCode.OK`, or an `AUTO` error without `fix`, raises `ValueError`. `target_files` given as one string is one target.

A subclass that takes constructor arguments of its own forwards the advisory keywords typed with `AdvisoryFields`:

```python
from typing import Unpack

from devkit.advisory import AdvisoryError, AdvisoryFields


class GitFailedError(AdvisoryError):
    code = "GIT_FAILED"

    def __init__(
        self, message: str, *details: object, returncode: int | None = None, **fields: Unpack[AdvisoryFields]
    ) -> None:
        super().__init__(message, *details, **fields)
        self.returncode = returncode
```

Factories are classmethods, so `MyDomainError.blocked(...)` returns `MyDomainError`. Other modes come from `actor`, `retry` and `retry_after`. A bare `AdvisoryError("...")` derives `HALT` (`actor=NONE`, `retry=UNSAFE`); set the fields that derive the intended mode instead.

## Returning warnings and notices

A warning or notice is an `AdvisoryError` at level `WARNING` or `NOTICE`, returned with the result (by convention in a `notices` list), never raised. Its `exit_code` is `0`; `actor`, `retry`, `guardrail`, `input_error` and `retry_after` are ignored.

```python
from dataclasses import dataclass, field

from devkit.advisory import AdvisoryError, Level


class OrphanLeftNotice(AdvisoryError):
    code = "ORPHAN_LEFT"
    level = Level.WARNING
    what_to_report = "A hand-edited file is no longer managed; delete or move it"


class ToolVersionChangedNotice(AdvisoryError):
    code = "TOOL_VERSION_CHANGED"
    level = Level.NOTICE
    brief = True  # self-explanatory, no fix: rendered without [ACTION]


@dataclass
class SyncResult:
    written: list[str]
    notices: list[AdvisoryError] = field(default_factory=list)
```

`error.with_level(Level.WARNING)` returns a copy at the lower level, keeping class and code. `as_advisory_error` reports a raised warning or notice as `UNEXPECTED_ERROR`.

## Rendering at boundaries

Catch at the process or transport boundary, not deep inside the code:

```python
import sys

from devkit.advisory import as_advisory_error


def main() -> int:
    try:
        run()
    except Exception as exc:  # boundary: adapt anything unexpected to UNEXPECTED_ERROR
        error = as_advisory_error(exc)
        print(error.render(), file=sys.stderr)
        return int(error.exit_code)
    return 0
```

- `error.lines()` / `error.render()`: sentinel lines (`[ERROR]`, `[WARN]` or `[NOTICE]` headline by level) for stderr or an MCP tool result; multi-line values continue on lines indented under their sentinel.
- `error.to_dict(include_advisory=True)`: JSON payload `{code, level, message, exit_code, advisory}`; a command printing JSON renders no block on stderr.
- `error.to_problem_details(status=404, type_base="https://docs.example.com/errors")`: RFC 7807 body. `status` is the HTTP status chosen by the web layer; the library never maps codes to statuses.
- `as_advisory_error(exc)` / `render_error(exc)`: pass through an `ERROR`-level `AdvisoryError`, adapt anything else to `UNEXPECTED_ERROR` (`MAINTENANCE`) with the message `<ExceptionType>: <text>`.

## Boundary rules

- Web frameworks own HTTP status mapping, headers such as `Retry-After`, and the server-side decision to include `advisory`; keep that adapter code in the application, not in `devkit.advisory`.
- Do not copy the enums, mode derivation, or `[ACTION]` texts into application code. Subclass `AdvisoryError` for domain errors instead.

## Testing

Assert on `error.code` and `error.mode` rather than message strings, and check that `fix` and `target_files` are exact:

```python
assert exc_info.value.mode is ActionMode.INPUT_ERROR
assert exc_info.value.target_files == ("config.toml:12",)
```
