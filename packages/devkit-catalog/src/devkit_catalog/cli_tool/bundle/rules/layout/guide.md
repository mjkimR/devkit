# [RULE-cli-tool-layout] Tools Keep the Feature Layout

## 1. Overview

A tool that starts flat (`cli.py` next to `usecases.py` and `services.py`) has to be restructured when its second
feature arrives. Every tool therefore starts with the feature layout, and this rule keeps every module of the package
in it. A module's place is also its layer, which `RULE-cli-tool-layers` checks imports against.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `cli-tool` bundle (`devkit add cli-tool`).
- **What is checked**: the path of every Python file matching `include` and not `exclude` that lies in a package
  below a `src` directory (`src/<package>/...`, the last `src` of the path). Directly in the package, only
  `__init__`, `__main__`, `cli`, `errors`, `base`, `utils` and `features` are allowed; in `features/` only feature
  directories (and `__init__.py`); in `features/<feature>/` only `__init__`, `cli`, `mcp`, `usecases`, `services`,
  `repositories`, `models`, `errors` and `utils`. Each may be a module or a directory.
- **Not checked**: what a layer directory contains (`usecases/run.py`, `services/scan/...` are free), files outside a
  `src/<package>/`, and file contents.

## 2. Cause of Violation

One violation per file, at line 1:

- `<name> is not a package-level module of the feature layout (...)`
- `features/<name> is a module directly in features/; a feature is a directory features/<feature>/`
- `features/<feature>/<name> is not a layer of a feature (...)`

## 3. Remediation

There is no autofix: which feature and layer code belongs to is a design decision.

- Behavior goes to `features/<feature>/` under its layer; a single-command tool still has one feature.
- Contracts several features share go to the package-level `base/`, technical helpers to `utils/` (package-level, or
  the feature's own `utils`), the tool's error classes to `errors`.
- The root `cli` holds only the root group and the tool's `Boundary`; feature commands live in their feature's `cli`.

The `cli-tool-structure` instruction shows the layout.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `include` | list of patterns | `["**/src/**"]` | Source files the rule reads. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out. |
| `extra_root_modules` | list of names | `[]` | Further names allowed directly in the package. |
| `extra_feature_modules` | list of names | `[]` | Further names allowed in a feature directory. |

Patterns are workspace-relative; a standalone `**` matches zero or more path segments. Each setting accepts per-path
overrides (`[[rules.settings.RULE-cli-tool-layout.overrides]]`).

## 5. Exceptions

A module that fits no layer for a stated reason (a plugin registry the tool's entry points name) is added to
`extra_root_modules` or `extra_feature_modules`, with the reason in a comment directly above the setting. A flat
layout is not an exception.
