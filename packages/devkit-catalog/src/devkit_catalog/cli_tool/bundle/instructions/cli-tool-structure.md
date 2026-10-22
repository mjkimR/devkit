---
name: cli-tool-structure
description: Read before creating or restructuring a Python command-line tool that agents run. Defines the framework, dependencies, the required feature layout and layer directions, the devkit-cli output contract, errors and exit codes, the import budget and tests.
---

# Agent-Facing CLI Tools

A command-line tool here is run by an agent on the user's behalf (user → agent → tool), so its output is a contract
the agent acts on, not a display. Build every new tool the same way: click for parsing, `devkit-cli` for the output
contract, a thin command layer over use cases. Follow this guide for a new tool and for every command added to one;
an existing tool that predates it is restructured only when the user asks.

## Framework and dependencies

- Parse with **click**. Do not use argparse, typer, fire or docopt.
- Depend at runtime on `devkit-cli` and `devkit-advisory` (from the same devkit release or commit; no package index
  serves them). They bring click; add only the libraries the commands need.
- Use **no** colour, tables, progress bars, spinners or interactive prompts: nothing a terminal renders and an agent
  pays for. `rich`, `tqdm` and `questionary` do not belong in a tool's runtime.

## Layout

```text
src/<package>/
  __init__.py          # version and public exports only; adds a NullHandler to the tool's logger
  __main__.py          # optional: python -m <package>
  cli.py               # root group (LazyGroup) and the tool's Boundary; imports no feature at module level
  errors.py            # the tool's AdvisoryError subclasses
  base/, utils/        # optional: contracts several features share; technical helpers
  features/<feature>/  # every feature, also the first and only one
    cli.py             # the feature's commands: parse, call the use case, print
    usecases.py        # one class per operation with a typed execute(); returns data and notices
    services.py        # logic; repositories.py for files, Git, HTTP or databases; models.py for data
    mcp.py, errors.py, utils.py   # optional: an MCP transport, feature errors, helpers
```

The feature layout is required from the first command: a flat package (`usecases.py` beside the root `cli.py`) is
rebuilt when the second feature arrives (`RULE-cli-tool-layout`). Each name may be a module or a directory; what a
layer directory holds is free. Imports go one way, `models`/`errors`/`utils` <- `repositories` <- `services` <-
`usecases` <- `cli`/`mcp`, and package-level `base`, `utils` and `errors` import no feature (`RULE-cli-tool-layers`).

- Commands live only in CLI modules (`cli.py`, `cli/`, `__main__.py`); click and `devkit_cli` are imported nowhere
  else. A command parses arguments, calls one use
  case, prints its result and returns: no business logic, no file or network access.
- A use case is a class whose constructor receives dependencies and whose `execute` method takes and returns typed
  values. Create `services`, `repositories` and `models` only when a feature needs them. Lower layers never import
  CLI modules.
- Libraries never print: everything below the CLI module returns data, raises `AdvisoryError` or logs
  (`RULE-cli-tool-library-output`).

## The boundary and the output contract

One `devkit_cli.Boundary` per tool, named after the tool's logger root; it reads `<PREFIX>_QUIET`, `<PREFIX>_VERBOSE`
and `<PREFIX>_STRICT`. Every command carries it under its click decorators (`RULE-cli-tool-command-boundary`):

```python
# src/mytool/cli.py
import click
from devkit_cli import Boundary, LazyGroup

boundary = Boundary("mytool")


@click.group(cls=LazyGroup, lazy_commands={"scan": "mytool.features.scan.cli:scan"})
def cli() -> None:
    """mytool: <one line on what it does>."""


# src/mytool/features/scan/cli.py
import click
from devkit_cli import FORMAT_OPTION, echo_json, echo_notices, exit_on_warnings

from mytool.cli import boundary


@click.command()
@click.argument("path")
@FORMAT_OPTION
@boundary
def scan(path: str, output_format: str) -> None:
    """Scan PATH and report the files that need work."""
    from mytool.features.scan.usecases import ScanFiles  # heavy dependencies load only for this command

    result = ScanFiles().execute(path)
    if output_format == "json":
        echo_json({"files": result.files, "notices": [notice.to_dict() for notice in result.notices]})
    else:
        for file in result.files:
            click.echo(f"[FILE: {file}]")
        click.echo(f"[SCAN: files={len(result.files)}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
```

- **stdout is the result**: one fact per line as `[KIND: value key=value key="free text"]` (`KIND` in
  `UPPER_SNAKE`, never `ERROR`, `WARN`, `NOTICE` or `INFO`), or exactly one JSON object under `--format json`. A
  command that succeeds with nothing to report prints `[OK: ...]`.
- **stderr is for advisories**: the boundary renders errors; `echo_notices` renders the warnings and notices a use
  case returned, after the result. Diagnostics are `logging` calls on the tool's logger, shown only under `-v`.
- **Context budget**: print only what changes the agent's next step or must reach the user. Put details behind
  `--format json` or a separate `show` command rather than in every run.

## Errors and exit codes

- A failure or refusal raises an `AdvisoryError` subclass with a stable `UPPER_SNAKE` code (the `advisory` bundle's
  `agent-advisory` and `agent-advisory-python` instructions define the fields). Do not invent error classes, codes or
  rendering outside `devkit.advisory`.
- A semantic argument check raises `devkit.advisory.ArgumentError` (`ARGUMENT_INVALID`); click only parses syntax.
- Exit codes are `0` success, `1` the command ran and the result is negative (findings, a failed check), `2` it could
  not do its job. Warnings and notices never change the exit code except under `--strict`. Never call `sys.exit`
  with any other code.

## Import budget

Every invocation, `--help` included, imports the root group and the CLI module of the command it runs.

- Register subcommands through `LazyGroup` (`lazy_commands`), not by importing every command module in `cli.py`.
- Import heavy libraries (HTTP clients, data frames, LLM SDKs, ORMs, `pydantic`) inside the command function or in the
  use case module the command imports there, never at CLI module level (`RULE-cli-tool-heavy-imports`).
- Budget: `python -X importtime -c "import <package>.cli"` stays under 100 ms of cumulative import time beyond click
  and `devkit_cli`. Measure it when adding a dependency.

## Tests

- Run commands in tests through `devkit_cli.testing.invoke(command, args, env=...)` and assert on the outcome:
  `exit_code`, `stdout` lines, `json()` for the one object, `codes()` for the advisory codes on stderr. Branch on codes,
  never on message text.
- Test each use case directly with its dependencies substituted; command tests cover parsing, output and exit codes.

## Rules

`devkit rules check` runs `RULE-cli-tool-layout`, `RULE-cli-tool-layers`, `RULE-cli-tool-command-boundary`,
`RULE-cli-tool-library-output` and `RULE-cli-tool-heavy-imports` on `src/`; `devkit rules explain <RULE-id>` prints each rule's guide and settings.
