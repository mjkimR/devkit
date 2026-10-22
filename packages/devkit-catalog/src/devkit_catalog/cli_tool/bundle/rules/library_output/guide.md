# [RULE-cli-tool-library-output] Libraries Never Print

## 1. Overview

Everything a command writes lands in the agent's context, so only the command decides what reaches stdout and
stderr. A service, repository or use case that prints puts text where the agent expects a result line or one JSON
object, and its output cannot be suppressed, tested as data or reused by another transport (an MCP tool, a test).
This rule reports terminal writes outside CLI modules and every `print`.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `cli-tool` bundle (`devkit add cli-tool`).
- **What is checked**: in every Python file matching `include` and not `exclude`, calls of `print` anywhere, and
  calls of `click.echo`, `click.secho`, `sys.stdout.write` and `sys.stderr.write` in files that do not match
  `cli_modules`. Import aliases are resolved (`import click as c`, `from click import echo`, `from sys import stdout`).
- **Not checked**: writes through other objects (a file handle, a logger), and calls through a name bound some other
  way than an import.

## 2. Cause of Violation

One violation per call, at its line and column:

- `print() writes output outside the output contract`: in any module. A CLI module writes with `click.echo` or
  `devkit_cli.echo_json`, which the boundary keeps UTF-8 and stops cleanly on a closed reader.
- `<call>() writes output outside a CLI module`: a terminal write in a library module.

## 3. Remediation

There is no autofix: where the data should go is a design decision.

- A result: return it to the command, which prints `[KIND: ...]` lines or one JSON object.
- Something the agent must act on: raise an `AdvisoryError` for a failure, or return a `WARNING` or `NOTICE` with the
  result for the command to pass to `echo_notices`.
- A diagnostic: a `logging` call on the tool's logger, shown under `-v`.

The `cli-tool-structure` instruction describes the layers and the output contract.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `include` | list of patterns | `["**/src/**"]` | Source files the rule reads. |
| `cli_modules` | list of patterns | `["**/cli.py", "**/cli/**", "**/__main__.py"]` | Files that may write to the terminal. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out. |

Patterns are workspace-relative; a standalone `**` matches zero or more path segments. Each setting accepts per-path
overrides (`[[rules.settings.RULE-cli-tool-library-output.overrides]]`).

## 5. Exceptions

A module whose job is terminal output outside the command layer (a renderer shared by several CLI modules) is added
to `cli_modules`, with the reason in a comment directly above the setting. Developer scripts outside `include` are
not checked.
