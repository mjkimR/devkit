# [RULE-cli-tool-layers] Imports Go One Way

## 1. Overview

A tool's layers stay replaceable only when imports go one way: commands call use cases, use cases coordinate
services, services use repositories, and models sit below all of them. The command line (click, `devkit_cli`) stays in
CLI modules, so the rest of the tool can be reused by another transport or a test, and the root group names feature
commands lazily, so `--help` and every command do not import every feature. A module's layer comes from its path
(`RULE-cli-tool-layout`), not from a base class.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `cli-tool` bundle (`devkit add cli-tool`).
- **What is checked**: every import of every Python file matching `include` and not `exclude` in a package below a
  `src` directory, read statically. Imports of the package are resolved by name (`pkg.features.scan.services`) and
  relatively (`from .models import Item` in a feature module, `from ..other.models import Item` across features). Ranks, lowest first: `models`, `errors` and `utils`; `repositories`;
  `services`; `usecases`; the transports `cli` and `mcp`.
- **Every file of the package** is checked for `click` and `devkit_cli`, also `__init__.py` files and modules an
  `extra_*_modules` exception of `RULE-cli-tool-layout` allows; the layer directions apply to the modules that have
  a layer.
- **Not checked**: imports under `if TYPE_CHECKING:`; layer directions in `features/__init__.py`, a feature's
  `__init__.py` (package management) and modules without a layer; imports of a feature package rather than one of its
  layers (`from pkg.features import scan`, `from pkg.features.scan import Thing`); imports of other packages; which
  lower layer a transport uses; anything a function does beyond its imports.

## 2. Cause of Violation

One violation per import statement, at its line:

- `click is imported outside a CLI module` (or `devkit_cli`): CLI modules are the package-level `cli` and `__main__`
  and each feature's `cli`.
- `<layer> imports the higher layer <layer> of its own feature (...)` (or `of feature <name>`).
- `<package>.cli is the command line; only CLI modules import it` (also `__main__`).
- `base imports the feature module ...` (also `utils` and `errors` at package level): package-level modules sit
  below every feature.
- `the root cli imports <module> at module level; name it in LazyGroup lazy_commands instead`.

## 3. Remediation

There is no autofix.

- Move the code down to the layer that may hold it, or pass what a lower layer needs as an argument instead of
  importing upward.
- Rendering and option parsing belong in the feature's `cli`; a use case returns data and notices.
- Register a feature command in the root group as `lazy_commands={"scan": "<package>.features.scan.cli:scan"}`, or
  import it inside a function.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `include` | list of patterns | `["**/src/**"]` | Source files the rule reads. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out. |

Patterns are workspace-relative; a standalone `**` matches zero or more path segments. Each setting accepts per-path
overrides (`[[rules.settings.RULE-cli-tool-layers.overrides]]`).

## 5. Exceptions

There is no per-import exception. A module that must break a direction is in the wrong layer; leave a generated
module out with `exclude`, with the reason in a comment directly above the setting.
