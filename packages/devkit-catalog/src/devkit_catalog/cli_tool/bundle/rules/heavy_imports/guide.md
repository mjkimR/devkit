# [RULE-cli-tool-heavy-imports] CLI Modules Import Heavy Libraries Lazily

## 1. Overview

Agents call a tool many times per task, often for `--help` or one small command, and every call imports the CLI
modules on its path. A heavy library imported at module level of a CLI module (an HTTP client, a data frame library,
an LLM SDK, an ORM) is paid by every one of those calls, also when the command does not use it. This rule reports
such imports so they move into the command that needs them.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `cli-tool` bundle (`devkit add cli-tool`).
- **What is checked**: in every Python file matching `include` and `cli_modules` and not `exclude`, the imports
  executed when the module is imported: module and class bodies, including `if`, `try` and `with` blocks. A name
  matches a heavy module when it is the module or one of its submodules (`google.cloud.storage` matches
  `google.cloud`); `from a import b` is matched as `a` and as `a.b`, and relative imports are resolved against the
  package of the file (below its last `src` directory).
- **Not checked**: imports inside functions, imports under `if TYPE_CHECKING:` (annotations only), and modules that
  are not CLI modules: a use case imports what it needs, and the command imports the use case inside its function
  when the use case is heavy.

## 2. Cause of Violation

One violation per import statement, at its line, naming the matched heavy module:

`<module> is imported at module level of a CLI module; every command pays for it`

## 3. Remediation

There is no autofix: where the import belongs depends on what uses it.

- Import it inside the command function, or in the use case module the command imports inside its function.
- For annotations only, import it under `if TYPE_CHECKING:` with `from __future__ import annotations`.
- Check the result with `python -X importtime -c "import <cli module>"`; the `cli-tool-structure` instruction gives
  the import budget.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `include` | list of patterns | `["**/src/**"]` | Source files the rule reads. |
| `cli_modules` | list of patterns | `["**/cli.py", "**/cli/**", "**/__main__.py"]` | Files that are CLI modules. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out. |
| `heavy_modules` | list of dotted names | about forty common heavy libraries (`numpy`, `pandas`, `httpx`, `requests`, `pydantic`, `sqlalchemy`, `openai`, `anthropic`, `litellm`, `torch`, `rich`, ...) | Modules reported; replacing the list drops the defaults. |
| `extra_heavy_modules` | list of dotted names | `[]` | Further modules added to `heavy_modules`, such as the tool's own modules that load a model or open a connection at import. |

`devkit rules explain RULE-cli-tool-heavy-imports` prints this guide; the full default list is `HEAVY_MODULES` in the
rule's `rule.py`. Each setting accepts per-path overrides (`[[rules.settings.RULE-cli-tool-heavy-imports.overrides]]`).

## 5. Exceptions

A command module that exists only to run the heavy library (a single-command tool whose every invocation uses it)
may keep the import: remove the module from `heavy_modules` with a path override for that file, with the reason in a
comment directly above it.
