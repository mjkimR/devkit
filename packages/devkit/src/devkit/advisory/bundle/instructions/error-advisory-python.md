---
name: error-advisory-python
description: Read before raising, rendering, or serializing errors in Python code. Explains the devkit.advisory library (AdvisoryError, factories, CLI/MCP/HTTP rendering) that implements the Agent Advisory Protocol.
---

# Agent Advisory Protocol in Python (`devkit.advisory`)

The `devkit.advisory` module implements the protocol defined in the `error-advisory` instruction. It is standard-library only. Read `error-advisory` first for mode semantics; this guide covers the Python API.

## Raising errors

Raise `AdvisoryError` subclasses instead of bare `ValueError`, `RuntimeError`, or framework exceptions at boundaries agents read. Declare stable defaults on the subclass and pass per-raise context as keywords. Every field can have a class-level default (`code`, `actor`, `retry`, `guardrail`, `input_error`, `retry_after`, `fix`, `what_to_report`, `target_files`, `exit_code`); a keyword argument other than `None` overrides it for one raise. Positional arguments after the message become `[DETAIL]` lines and are converted to `str`:

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

For one-off errors, use the factories. They set the field combination for each mode:

| Factory | Mode | Fields set |
| --- | --- | --- |
| `AdvisoryError.invalid_input(msg, *details, code=, fix=, target_files=)` | `INPUT_ERROR` | `input_error`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.blocked(msg, *details, code=, fix=, target_files=)` | `BLOCKED` | `guardrail`, `DEVELOPER`, `AFTER_FIX` |
| `AdvisoryError.auto_fix(msg, *details, fix=, code=, target_files=)` | `AUTO` | `TOOL`, `AFTER_FIX` |
| `AdvisoryError.interaction(msg, *details, code=, what_to_report=, fix=)` | `INTERACTION` | `USER`, `AFTER_FIX` |

Factories are classmethods, so `MyDomainError.blocked(...)` returns `MyDomainError`. Other modes (`HALT`, `MAINTENANCE`, `DEFER`) are set through `actor`, `retry`, and `retry_after` on the constructor or the subclass. A bare `AdvisoryError("...")` derives `HALT` (`actor=NONE`, `retry=UNSAFE`); choose fields deliberately instead of relying on that default.

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

- `error.lines()` / `error.render()`: sentinel lines for stderr or an MCP tool error result; multi-line values continue on lines indented under their sentinel.
- `error.to_dict(include_advisory=True)`: JSON payload `{code, message, exit_code, advisory}`.
- `error.to_problem_details(status=404, type_base="https://docs.example.com/errors")`: RFC 7807 body. `status` is the HTTP status chosen by the web layer; the library never maps codes to statuses.
- `as_advisory_error(exc)` / `render_error(exc)`: pass through `AdvisoryError`, adapt anything else to `UNEXPECTED_ERROR` (`MAINTENANCE`).

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
