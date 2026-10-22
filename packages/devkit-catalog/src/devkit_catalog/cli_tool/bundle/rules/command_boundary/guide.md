# [RULE-cli-tool-command-boundary] Commands Go Through a Boundary

## 1. Overview

An agent reads a command's stdout as its result, its stderr as advisories and its exit code as the outcome. A click
command without a `devkit_cli.Boundary` decorator lets an exception escape as a Python traceback, prints errors as
free text, ignores `--format json` on failure and has no `-q`, `-v` or `--strict`. This rule reports such commands.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `cli-tool` bundle (`devkit add cli-tool`).
- **What is checked**: in every Python file matching `include` and `cli_modules` and not `exclude`, each function
  with a decorator named `command` (`@cli.command()`, `@click.command`, `@command()`), read statically.
- **Not checked**: group callbacks (`@click.group`, `@cli.group()`): a group only dispatches to its commands. Commands
  outside CLI modules are not looked for: that a command lives in a CLI module is the structure the
  `cli-tool-structure` instruction asks for.

## 2. Cause of Violation

One violation per command function without a decorator named in `boundary_names`, at the function's line:

`Command <name> has no boundary decorator (boundary); its errors bypass the output contract`

## 3. Remediation

There is no autofix. Create one `Boundary` for the tool (`boundary = Boundary("mytool")`, usually in the package's
`cli` module) and put it under the click decorators of the command:

```python
@cli.command()
@FORMAT_OPTION
@boundary
def scan(output_format: str) -> None: ...
```

When the tool names its boundary differently (`@guard`), or wraps it in a decorator of its own that applies the
boundary (`@json_command`, calling `boundary(json_only=True)` inside), add that name to `boundary_names` instead of
renaming it.
Read the `cli-tool-structure` instruction for the output contract the boundary implements.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `include` | list of patterns | `["**/src/**"]` | Source files the rule reads. |
| `cli_modules` | list of patterns | `["**/cli.py", "**/cli/**", "**/__main__.py"]` | Files that are CLI modules. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out. |
| `boundary_names` | list of names | `["boundary"]` | Decorator names that count as the boundary (a name or an attribute's last part, called or not). |

Patterns are workspace-relative; a standalone `**` matches zero or more path segments. Each setting accepts per-path
overrides (`[[rules.settings.RULE-cli-tool-command-boundary.overrides]]`).

## 5. Exceptions

A command that must not take the output options (a hidden command whose stdout belongs to another protocol, such as
a host hook or an MCP server) is a justified exception: leave its module out with a path override setting `include`
to `[]` for that file, with the reason in a comment directly above it.
