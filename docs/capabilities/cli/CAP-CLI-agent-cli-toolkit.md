---
id: CAP-CLI-agent-cli-toolkit
title: Agent-First CLI Toolkit
summary: "The devkit-cli runtime library that gives any click tool devkit's agent-first output contract, and the opt-in cli-tool bundle that guides and checks the structure of such tools."
area: cli
status: active
entrypoints:
  - packages/devkit-cli/
  - packages/devkit-dist/src/devkit_dist/adapters/cli.py
  - packages/devkit-catalog/src/devkit_catalog/cli_tool/
---

# [CAP-CLI-agent-cli-toolkit] Agent-First CLI Toolkit

## 1. Summary

Command-line tools in the user's repositories are run by AI agents on the user's behalf, so each needs the output
contract of `ARCH-08-1-agent-output`: results on stdout, Agent Advisory Protocol blocks on stderr, exit codes `0`,
`1` and `2`, and the same output options. `devkit-cli` (`devkit_cli`) implements that contract once for any click
tool; `devkit` itself runs on it. The opt-in `cli-tool` bundle of `devkit-catalog` tells agents how to structure a
tool around it and checks the structure with five rules.

## 2. Scope & Boundary

- **In-Scope**:
  - The command boundary (`devkit_cli.Boundary`): output options, error rendering, JSON error documents, `-v` log
    lines, UTF-8 output and the closed-reader exit.
  - Output helpers (`FORMAT_OPTION`, `echo_json`, `echo_notices`, `exit_on_warnings`, `exit_on_problems`,
    `report_exit_code`), lazily loaded subcommands (`LazyGroup`) and the test helper (`devkit_cli.testing`).
  - The `cli-tool` bundle: the `cli-tool-structure` instruction and `RULE-cli-tool-layout`, `RULE-cli-tool-layers`,
    `RULE-cli-tool-command-boundary`, `RULE-cli-tool-library-output` and `RULE-cli-tool-heavy-imports`.
- **Out-of-Scope**:
  - The advisory model, codes, modes and rendering: `CAP-ADV-agent-advisory-protocol` (`devkit.advisory`).
  - Command-specific results, project discovery and the `devkit` command tree: each devkit area and
    `CAP-HARN-command-mount`.
  - Use case base classes, dependency injection, configuration loading and plugin discovery: a tool owns them; the
    instruction states the use case convention only.
  - Human-oriented output (colour, tables, progress, prompts): not provided.

## 3. Business Rules & Policies

1. **Dependencies**: `devkit-cli` MUST depend on `click` and `devkit-advisory` only, and importing `devkit_cli` MUST
   load no module outside the standard library, `click`, `devkit.advisory` and `devkit_cli`
   (`packages/devkit-cli/tests/integration/test_lazy_and_package.py`).
2. **One boundary per tool**: `Boundary(name)` MUST read `<PREFIX>_QUIET`, `<PREFIX>_VERBOSE` and `<PREFIX>_STRICT`,
   where `<PREFIX>` is `name` upper-cased with `-` and `.` as `_` unless `env_prefix` is given, and MUST print the
   records of the `name` logger hierarchy as `[INFO]   <logger without name.>: <message>` under `-v`.
3. **Output options**: the boundary MUST apply section 6 of `ARCH-08-1-agent-output` to every command it wraps: a flag
   wins over the environment, a variable is on only when exactly `1`, and quiet together with verbose is
   `ARGUMENT_INVALID` with exit `2`.
4. **Errors**: WHEN a wrapped command raises an `ERROR` advisory, the boundary MUST render it once and exit with its
   `exit_code`: on stderr in text mode, as `{"error": {...}}` on stdout with the notices passed to `echo_notices`
   under `notices` in JSON mode (`--format json` or `json_only`), with nothing on stderr.
5. **Unexpected exceptions**: IF a wrapped command raises anything other than an `ERROR` advisory, `Reported` (its
   error is rendered on stderr in text mode only, since its result is already on stdout, and its `exit_code` used), a
   click exit, abort or usage error, `SystemExit` or `BrokenPipeError` (rule 6), THEN the boundary MUST report it as
   `UNEXPECTED_ERROR` with exit `2` and log its traceback at `DEBUG`.
6. **Closed reader**: IF the reader of stdout closes before the command finishes, THEN the boundary MUST exit `2`
   without writing an advisory.
7. **Locale independence**: the boundary MUST make stdout and stderr UTF-8 with `backslashreplace` before the command
   runs.
8. **Lazy commands**: `LazyGroup` MUST import a lazy command's module only when the command is looked up, and IF its
   target is not a click command, THEN it MUST raise `TypeError` naming the target.
9. **Argument errors**: a semantic argument check MUST raise `devkit.advisory.ArgumentError` (`ARGUMENT_INVALID`), or
   a subclass of it; no other class declares that code (`RULE-advisory-unique-code`).
10. **Semver contract**: `devkit-cli` MUST be released at the version of `devkit-dist`, `devkit-agt` and
    `devkit-advisory`, and a removed or renamed public name MUST bump the minor version within `0.x`
    (`packages/devkit/tests/integration/package/test_lockstep.py` for the version, and the pinned public names in
    `packages/devkit-cli/tests/integration/test_lazy_and_package.py`).
11. **Opt-in bundle**: the `cli-tool` bundle MUST deploy nothing until a project selects it; its default preset deploys
    the instruction and the five rules, and its `guide` preset the instruction only
    (`packages/devkit-catalog/tests/integration/bundles/test_bundles.py`).
12. **Command boundary**: WHERE `cli-tool` is selected, a function in a CLI module with a decorator named `command`
    MUST also carry a decorator named in `boundary_names` below it; group callbacks are not checked
    (`RULE-cli-tool-command-boundary`).
13. **No print**: WHERE `cli-tool` is selected, a module MUST NOT call `print` (`RULE-cli-tool-library-output`).
14. **Library output**: WHERE `cli-tool` is selected, a module other than a CLI module MUST NOT call `click.echo`,
    `click.secho`, `sys.stdout.write` or `sys.stderr.write` (`RULE-cli-tool-library-output`).
15. **Heavy imports**: WHERE `cli-tool` is selected, a CLI module MUST NOT import a module of `heavy_modules` or
    `extra_heavy_modules` at import time; imports inside functions and under `if TYPE_CHECKING:` are allowed
    (`RULE-cli-tool-heavy-imports`).
16. **Feature layout**: WHERE `cli-tool` is selected, a module of a package below `src/` MUST be one of `__init__`,
    `__main__`, `__about__`, `_version`, `cli`, `errors`, `base`, `utils` or `features`, and below
    `features/<feature>/` one of `__init__`, `cli`, `mcp`, `usecases`, `services`, `repositories`, `models`, `errors`
    or `utils`, each a module or a directory; a flat layout is not allowed (`RULE-cli-tool-layout`).
17. **Command line confined**: WHERE `cli-tool` is selected, only CLI modules (the package-level `cli` and
    `__main__`, a feature's `cli`) MUST import `click`, `devkit_cli`, or the package-level `cli` or `__main__`
    (`RULE-cli-tool-layers`).
18. **Layer direction**: WHERE `cli-tool` is selected, a feature layer module MUST import only feature layers of its
    own rank or lower (`models`, `errors`, `utils` < `repositories` < `services` < `usecases` < `cli`, `mcp`), and the
    package-level `base`, `utils` and `errors` MUST import no feature (`RULE-cli-tool-layers`).
19. **Lazy root group**: WHERE `cli-tool` is selected, the package-level `cli` MUST NOT import a feature layer module
    at module level (`RULE-cli-tool-layers`).

Rules 17 to 19 do not check imports under `if TYPE_CHECKING:`, imports of a feature package rather than one of its
layers (`from pkg.features import scan`), and the direction of imports in `features/__init__.py`, a feature's
`__init__.py` and modules without a layer; those files are still checked for `click` and `devkit_cli` (rule 17).

## 4. Interfaces & Data Contracts

- **`devkit_cli` (package root)**:

  | Name | Contract |
  | --- | --- |
  | `Boundary(name, *, env_prefix=None, log=None)` | Decorator, `@boundary` or `@boundary(json_only=True)`, placed below the click decorators; adds `-q/--quiet`, `-v/--verbose`, `--strict`. Attributes `name`, `quiet_env`, `verbose_env`, `strict_env`; methods `output_options(fn)`, `resolve_output(quiet, verbose, strict)`. `log` receives the unexpected-error traceback (default the `<name>.cli` logger). `ValueError` for an empty or padded name or an invalid prefix. |
  | `FORMAT_OPTION`, `is_json(value)` | `--format text\|json`, parameter `output_format`, case-insensitive. |
  | `echo_json(data)` | One JSON object on stdout, UTF-8, indented by 2. |
  | `echo_notices(notices)`, `exit_on_warnings(notices)` | Warnings, then notices, on stderr after the result (none under `-q` for notices; none in JSON mode); exit `1` under `--strict` when a warning was reported. |
  | `exit_on_problems(problems, *, report=False)`, `highest_exit_code`, `report_exit_code` | Render collected problems and exit with the highest `exit_code`, or `1` for a status or show command. |
  | `OutputSettings`, `output_settings()`, `Reported(error)` | The running command's `quiet`, `verbose`, `strict`, `json`; an error whose JSON result is already printed. |
  | `LazyGroup(..., lazy_commands={name: "module:attribute"})` | Lazy subcommands; `resolve_lazy(ctx, name)` is the extension point. |

- **`devkit_cli.testing`** (tests only, not imported by the package root): `invoke(command, args=(), *, env=None)`
  returns `Outcome(exit_code, stdout, stderr, exception)`; `Outcome.json()` returns the one JSON object on stdout
  (else `AssertionError`), `Outcome.codes()` the codes of the `[ERROR]`, `[WARN]` and `[NOTICE]` blocks on stderr.
- **`devkit.advisory.ArgumentError`**: `code = "ARGUMENT_INVALID"`, mode `INPUT_ERROR`, exit `2`.
- **`cli-tool` bundle**: assets `cli-tool-structure` (instruction), `layout`, `layers`, `command-boundary`,
  `library-output` and `heavy-imports` (rules); presets `all` (default) and `guide`. Every rule takes `include`
  (default `["**/src/**"]`) and `exclude` (default the test file patterns); the three output rules take
  `cli_modules` (default `["**/cli.py", "**/cli/**", "**/__main__.py"]`); `RULE-cli-tool-layout` adds
  `extra_root_modules` and `extra_feature_modules`, `RULE-cli-tool-command-boundary` `boundary_names` (default
  `["boundary"]`) and `RULE-cli-tool-heavy-imports` `heavy_modules` and `extra_heavy_modules`. Each rule's guide documents its
  messages and settings.
- **devkit's configuration**: `devkit_dist.adapters.cli` binds the toolkit as `Boundary("devkit")` (variables
  `DEVKIT_QUIET`, `DEVKIT_VERBOSE`, `DEVKIT_STRICT`), and the `devkit` root group extends `LazyGroup` with
  `devkit.commands` plugins (`ARCH-05-3-command-plugins`).
