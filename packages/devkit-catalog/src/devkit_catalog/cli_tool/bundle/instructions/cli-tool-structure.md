---
name: cli-tool-structure
description: Read before creating or restructuring a Python command-line tool that agents run. Defines the framework, dependencies, package layout, the devkit-cli output contract, errors and exit codes, the import budget and tests.
---

# Agent-Facing CLI Tools

An agent runs these tools on the user's behalf, so a tool's output is a contract the agent acts on, not a display.
Follow this instruction for a new tool and for every command added to one; restructure a tool that predates it only
when the user asks.

## Framework and dependencies

- Parse with click, not argparse, typer, fire or docopt.
- Depend at runtime on `devkit-cli` and `devkit-advisory` from the same devkit release or commit, because no package
  index serves them. They bring click; add only the libraries the commands need.
- Print no colour, tables, progress bars, spinners or interactive prompts: an agent pays for what a terminal
  renders. Keep `rich`, `tqdm` and `questionary` out of the runtime dependencies.

## Layout

```text
src/<package>/
  __init__.py          # version and public exports only; adds a NullHandler to the tool's logger
  cli.py               # root group (LazyGroup) and the tool's Boundary
  features/<feature>/
    cli.py             # the feature's commands
    usecases.py        # one class per operation
    services.py        # logic; repositories.py for files, Git, HTTP or databases; models.py for data
  errors.py            # the tool's AdvisoryError subclasses
```

- Put commands only in CLI modules (`cli.py`, `cli/`, `__main__.py`). A command parses arguments, calls one use
  case, prints its result and returns: no business logic, no file or network access.
- Give each use case a constructor that receives dependencies and an `execute` method that takes and returns typed
  values, including the notices to report. Create `services`, `repositories` and `models` only when a feature needs
  them. Lower layers never import CLI modules.
- Below the CLI module, return data, raise `AdvisoryError` or log; never print (`RULE-cli-tool-library-output`).

## The boundary and the output contract

Create one `devkit_cli.Boundary` per tool, named after the tool's logger root; it reads `<PREFIX>_QUIET`,
`<PREFIX>_VERBOSE` and `<PREFIX>_STRICT`. Put it under every command's click decorators
(`RULE-cli-tool-command-boundary`):

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
  case returned, after the result. Write diagnostics as `logging` calls on the tool's logger, shown only under `-v`.
- **Context budget**: print only what changes the agent's next step or must reach the user. Put details behind
  `--format json` or a separate `show` command.

## Errors and exit codes

- Raise an `AdvisoryError` subclass with a stable `UPPER_SNAKE` code for a failure or refusal; the `advisory`
  bundle's `agent-advisory` and `agent-advisory-python` instructions define the fields. Take error classes, codes
  and rendering from `devkit.advisory`, not from your own.
- Raise `devkit.advisory.ArgumentError` (`ARGUMENT_INVALID`) for a semantic argument check; click only parses syntax.
- Exit `0` on success, `1` when the command ran and the result is negative (findings, a failed check), `2` when it
  could not do its job. Warnings and notices change the exit code only under `--strict`. Call `sys.exit` with no
  other code.

## Import budget

Every invocation, `--help` included, imports the root group and the CLI module of the command it runs.

- Register subcommands through `LazyGroup` (`lazy_commands`), not by importing every command module in `cli.py`.
- Import heavy libraries (HTTP clients, data frames, LLM SDKs, ORMs, `pydantic`) inside the command function or in the
  use case module the command imports there, never at CLI module level (`RULE-cli-tool-heavy-imports`).
- When adding a dependency, measure `python -X importtime -c "import <package>.cli"`: cumulative import time beyond
  click and `devkit_cli` stays under 100 ms.

## Tests

- Run commands in tests through `devkit_cli.testing.invoke(command, args, env=...)` and assert on the outcome:
  `exit_code`, `stdout` lines, `json()` for the one object, `codes()` for the advisory codes on stderr. Branch on codes,
  never on message text.
- Test each use case directly with its dependencies substituted; command tests cover parsing, output and exit codes.

## Completion

- `devkit rules check` reports no `RULE-cli-tool-command-boundary`, `RULE-cli-tool-library-output` or
  `RULE-cli-tool-heavy-imports` violation on `src/`; `devkit rules explain <RULE-id>` prints a rule's guide. Without
  the rules installed, check the same three conditions in the command modules by hand.
- The command and use case tests pass.
- After a dependency change, the measured import time is under the budget.
