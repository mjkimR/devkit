---
name: agent-advisory-python
description: Read before raising, returning, rendering, or serializing errors, warnings or notices in Python code. Explains the devkit.advisory library (AdvisoryError, levels, factories, CLI/MCP/HTTP rendering) that implements the Agent Advisory Protocol.
---

# Agent Advisory Protocol in Python (`devkit.advisory`)

The `devkit.advisory` module implements the protocol defined in the `agent-advisory` instruction. It is standard-library only. Read `agent-advisory` first for level and mode semantics; this guide covers the Python API.

## Raising errors

Raise `AdvisoryError` subclasses instead of bare `ValueError`, `RuntimeError`, or framework exceptions at boundaries agents read. Declare stable defaults on the subclass and pass per-raise context as keywords. Every field can have a class-level default (`code`, `level`, `actor`, `retry`, `guardrail`, `input_error`, `retry_after`, `fix`, `what_to_report`, `target_files`, `brief`, `exit_code`); a keyword argument other than `None` overrides it for one instance. Positional arguments after the message become `[DETAIL]` lines and are converted to `str`:

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

For one-off errors, use the factories. They set every field that decides the mode (`level = ERROR`, `actor`, `retry`, `guardrail`, `input_error`), so a subclass default never changes the mode a factory names:

| Factory | Mode | Fields set |
| --- | --- | --- |
| `AdvisoryError.invalid_input(msg, *details, code=, fix=, target_files=)` | `INPUT_ERROR` | `input_error`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.blocked(msg, *details, code=, fix=, target_files=)` | `BLOCKED` | `guardrail`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.auto_fix(msg, *details, fix=, code=, target_files=)` | `AUTO` | `TOOL`, `AFTER_FIX` |
| `AdvisoryError.interaction(msg, *details, code=, what_to_report=, fix=)` | `INTERACTION` | `USER`, `AFTER_FIX` |

`exit_code` defaults to `ExitCode.ERROR` (`2`, the command could not do its job). An error that reports a negative result of a check that did run, such as a guardrail refusing a commit, sets `exit_code = ExitCode.FINDINGS` (`1`). An error never exits `ExitCode.OK` (`0`): constructing one, or an `AUTO` error without `fix`, raises `ValueError`. `target_files` given as one string is one target.

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

Factories are classmethods, so `MyDomainError.blocked(...)` returns `MyDomainError`. Other modes (`HALT`, `MAINTENANCE`, `DEFER`) are set through `actor`, `retry`, and `retry_after` on the constructor or the subclass. A bare `AdvisoryError("...")` derives `HALT` (`actor=NONE`, `retry=UNSAFE`); choose fields deliberately instead of relying on that default.

## Returning warnings and notices

Something an operation that **succeeded** must tell its caller is an `AdvisoryError` at level `WARNING` or `NOTICE`. It is never raised: return it with the result, typically in a `notices` list, and let the boundary print the result first and the notices after it. Its `exit_code` is `0` and its mode is `CONTINUE` (warning) or `NOTE` (notice); `actor`, `retry`, `guardrail`, `input_error` and `retry_after` are ignored.

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

A condition that is an error in one place and a warning in another keeps its class and code: `error.with_level(Level.WARNING)` returns a copy at the lower level. A raised warning or notice is a defect: `as_advisory_error` reports it as `UNEXPECTED_ERROR`.

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
- `error.to_dict(include_advisory=True)`: JSON payload `{code, level, message, exit_code, advisory}`.
- Print the result before its warnings and notices, and errors last; a quiet mode may skip notices, never warnings or errors.
- `error.to_problem_details(status=404, type_base="https://docs.example.com/errors")`: RFC 7807 body. `status` is the HTTP status chosen by the web layer; the library never maps codes to statuses.
- `as_advisory_error(exc)` / `render_error(exc)`: pass through an `ERROR`-level `AdvisoryError`, adapt anything else to `UNEXPECTED_ERROR` (`MAINTENANCE`) with the message `<ExceptionType>: <text>`.

## Boundary rules

- Web frameworks own HTTP status mapping, headers such as `Retry-After`, and the server-side decision to include `advisory`. Keep that adapter code in the application or framework package, not in `devkit.advisory`.
- Never execute `fix` automatically in an adapter.
- Do not copy the enums, mode derivation, or `[ACTION]` texts into application code. Subclass `AdvisoryError` for domain errors instead.

## Testing

Assert on `error.code` and `error.mode` rather than message strings, and check that `fix` and `target_files` are exact:

```python
assert exc_info.value.mode is ActionMode.INPUT_ERROR
assert exc_info.value.target_files == ("config.toml:12",)
```
