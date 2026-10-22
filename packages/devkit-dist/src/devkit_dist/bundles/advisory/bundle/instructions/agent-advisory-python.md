---
name: agent-advisory-python
description: Read before raising, returning, rendering or serializing errors, warnings or notices in Python code with devkit.advisory.
---

# Agent Advisory Protocol in Python (`devkit.advisory`)

Read the `agent-advisory` instruction first. Make runtime code depend on
`devkit-advisory`, not on `devkit-dist` or `devkit-agt`.

## Raising errors

At boundaries agents read, raise `AdvisoryError` subclasses, not bare
`ValueError`, `RuntimeError` or framework exceptions. Set fields as class
defaults; a keyword argument overrides one for an instance, and positional
arguments after the message become `[DETAIL]` lines.

```python
from devkit.advisory import Actor, AdvisoryError, Retry


class ConfigInvalidError(AdvisoryError):
    code = "CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


raise ConfigInvalidError(
    "config.toml: 'timeout' must be an integer",
    'line 12: timeout = "30s"',
    target_files=["config.toml:12"],
    fix="Set timeout = 30 in config.toml",
)
```

- For a one-off error, use a factory classmethod: `invalid_input`, `blocked`,
  `auto_fix` (requires `fix=`) or `interaction`. It sets every field that decides
  the mode, and `MyDomainError.blocked(...)` returns `MyDomainError`.
- For a malformed argument, raise `ArgumentError` or a subclass of it.
- Set `exit_code = ExitCode.FINDINGS` (`1`) for a negative result of a check
  that ran; the default is `ExitCode.ERROR` (`2`).
- If a subclass takes constructor arguments of its own, accept
  `**fields: Unpack[AdvisoryFields]` and pass them to `super().__init__`.

## Warnings and notices

Subclass with `level = Level.WARNING` or `Level.NOTICE` and return instances in
the result's `notices` list. `error.with_level(Level.WARNING)` returns a copy at
the lower level with the same code.

```python
class OrphanLeftNotice(AdvisoryError):
    code = "ORPHAN_LEFT"
    level = Level.WARNING
    what_to_report = "A hand-edited file is no longer managed; delete or move it"
```

## Rendering at boundaries

Catch at the process or transport boundary, not deep inside the code:

```python
def main() -> int:
    try:
        run()
    except Exception as exc:
        error = as_advisory_error(exc)  # anything not an ERROR-level AdvisoryError becomes UNEXPECTED_ERROR
        print(error.render(), file=sys.stderr)
        return int(error.exit_code)
    return 0
```

- `error.to_dict(include_advisory=True)` gives the JSON payload; a command
  printing JSON renders no block on stderr.
- `error.to_problem_details(status=..., type_base=...)` gives an RFC 7807 body;
  the web layer chooses the status.
- Subclass `AdvisoryError` for domain errors; do not copy the enums, mode
  derivation or `[ACTION]` texts into application code.

## Testing

Assert on `error.code`, `error.mode` and exact `fix` and `target_files`, not on
message strings:

```python
assert exc_info.value.mode is ActionMode.INPUT_ERROR
assert exc_info.value.target_files == ("config.toml:12",)
```
