---
name: cli-tool-structure
description: Read before creating or restructuring a Python command-line tool that agents run. Defines the framework, dependencies, the required feature layout and layer directions, the devkit-cli output contract, the import budget and tests.
---

# Agent-Facing CLI Tools

Follow this for a new tool and every command added to one; restructure an older tool only when the user asks. The
`cli-tool` rules check the layout, layer imports, boundaries, library output and heavy imports (`devkit rules
explain <RULE-id>` gives each fix); the `agent-advisory-python` instruction defines errors, notices and exit codes.

## Dependencies

- Parse with click. Depend at runtime on `devkit-cli` and `devkit-advisory` from the same devkit release or commit;
  no package index serves them.
- Add no terminal rendering (`rich`, `tqdm`, `questionary`): no colour, tables, progress bars or prompts.

## Layout

```text
src/<package>/
  cli.py               # root LazyGroup and the tool's one Boundary; imports no feature at module level
  errors.py            # the tool's AdvisoryError subclasses
  base/, utils/        # optional: contracts several features share; technical helpers
  features/<feature>/  # every feature, also the first and only one
    cli.py             # commands
    usecases.py        # one class per operation
    services.py, repositories.py, models.py   # only when the feature needs them
    mcp.py, errors.py, utils.py               # optional
```

The feature layout is required from the first command; a flat package is rebuilt when the second feature arrives.
Each name may be a module or a directory whose inside is free. Imports go one way, `models`/`errors`/`utils` <-
`repositories` <- `services` <- `usecases` <- `cli`/`mcp`; click and `devkit_cli` stay in CLI modules.

- A command parses arguments, calls one use case and prints its result: no business logic, file or network access.
- A use case receives dependencies in its constructor and has a typed `execute` that returns data and notices.

## Output contract

- stdout carries the result: one fact per line as `[KIND: value key=value key="free text"]` (`KIND` in
  `UPPER_SNAKE`, never `ERROR`, `WARN`, `NOTICE` or `INFO`), or one JSON object under `--format json`. A command
  with nothing to report prints `[OK: ...]`.
- stderr carries advisories: the boundary renders errors, and `echo_notices` renders returned notices after the
  result. Diagnostics are `logging` calls on the tool's logger, shown under `-v`.
- Print only what changes the agent's next step; put details behind `--format json` or a `show` command.

```python
@click.command()
@click.argument("path")
@FORMAT_OPTION
@boundary  # Boundary("mytool") from the root cli.py, which registers this command through LazyGroup
def scan(path: str, output_format: str) -> None:
    """Scan PATH and report the files that need work."""
    from mytool.features.scan.usecases import ScanFiles  # heavy dependencies load only for this command

    result = ScanFiles().execute(path)
    if output_format == "json":
        echo_json({"files": result.files, "notices": [notice.to_dict() for notice in result.notices]})
    else:
        for file in result.files:
            click.echo(f"[FILE: {file}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
```

## Import budget and tests

- When adding a dependency, measure `python -X importtime -c "import <package>.cli"`: cumulative import time beyond
  click and `devkit_cli` stays under 100 ms.
- Run commands in tests through `devkit_cli.testing.invoke(command, args, env=...)` and assert on `exit_code`,
  `stdout` lines, `json()` and `codes()`, never on message text. Test each use case directly with substituted
  dependencies.

## Completion

`devkit rules check` reports no `RULE-cli-tool-*` violation on `src/`, and the tests pass.
