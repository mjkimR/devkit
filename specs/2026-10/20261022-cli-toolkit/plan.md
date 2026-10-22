---
id: PLAN-cli-toolkit
spec: SPEC-cli-toolkit
---

# Technical Plan: `SPEC-cli-toolkit` Agent-first CLI toolkit package and catalog bundle

## 1. Architecture Overview & Impact

- Target Area: a new workspace package `packages/devkit-cli` (`devkit_cli`), `devkit.advisory`, `devkit_core.base.errors`,
  `devkit_dist.adapters.cli` and `devkit_dist.cli`, a new `cli-tool` bundle in `devkit-catalog`, packaging and
  release wiring, and the Living Spec.
- Dependency direction: `devkit-advisory` ← `devkit-cli` ← `devkit-dist` (and everything above it). `devkit-cli`
  depends on `click` and `devkit-advisory` only and imports nothing else at module level; `devkit-core` does not
  depend on it.
- The move of the boundary is behavior-preserving: `devkit_dist.adapters.cli` keeps its public names and becomes the
  devkit configuration of the toolkit (`Boundary("devkit")`) plus the devkit-only helpers.
- Living Spec: a new capability, CAP-CLI-agent-cli-toolkit (area `cli`), for the package and the bundle;
  `ARCH-05-1-containers`, `ARCH-05-2-components`, `ARCH-07-deployment` and `ARCH-08-1-agent-output` name the new
  container and implementation; `CAP-ADV-agent-advisory-protocol` and the advisory reference gain `ArgumentError`.

## 2. Component Breakdown & Interface Contracts

### 2.1 `devkit.advisory.ArgumentError`

`class ArgumentError(AdvisoryError)`: `code = "ARGUMENT_INVALID"`, `actor = DEVELOPER`, `retry = AFTER_FIX`,
`input_error = True`; exported from `devkit.advisory`. `devkit_core.base.errors.ArgumentError(DevkitCoreError,
advisory.ArgumentError)` keeps its name and redeclares nothing that changes the mode.

### 2.2 `devkit_cli` (public API, all exported from the package root)

| Name | Contract |
| --- | --- |
| `Boundary(name, *, env_prefix=None)` | `name` is the tool's logger root (`logging.getLogger(name)`); `env_prefix` defaults to `name` upper-cased with `-` and `.` as `_`. The instance is the decorator: `@boundary` or `@boundary(json_only=True)`; it adds `-q/-v/--strict` (`<PREFIX>_QUIET`, `<PREFIX>_VERBOSE`, `<PREFIX>_STRICT`) and applies the error, JSON, log, UTF-8 and broken-pipe handling of `ARCH-08-1-agent-output`. `boundary.output_options` and `boundary.resolve_output` are exposed; `quiet_env`, `verbose_env`, `strict_env` name the variables. |
| `FORMAT_OPTION`, `is_json` | `--format text\|json` (parameter `output_format`, case-insensitive). |
| `echo_json`, `echo_notices`, `exit_on_warnings`, `exit_on_problems`, `highest_exit_code`, `report_exit_code` | As in `devkit_dist.adapters.cli` today; they read the running command's settings from a context variable, so they need no `Boundary`. |
| `OutputSettings`, `output_settings` | The running command's options; all off outside a command. |
| `Reported` | An error whose JSON result is already printed. |
| `LazyGroup` | `click.Group` taking `lazy_commands: Mapping[str, str]` (`name -> "module:attribute"`); lists them with the eager ones and imports a module only in `get_command`; a target that is not a click command raises `TypeError`. `resolve_lazy(name)` is the hook a subclass extends (devkit's plugin lookup). |
| `devkit_cli.testing.invoke(command, args, *, env=None)` | Runs `click.testing.CliRunner` with separate streams and returns `Outcome(exit_code, stdout, stderr)` with `json()` (exactly one object, else `AssertionError`) and `codes()` (the `(CODE)` of every `[ERROR]`, `[WARN]` and `[NOTICE]` headline on stderr, in order). Not imported by `devkit_cli/__init__`. |

The boundary logs the traceback of an unexpected error on `<name>.cli` at `DEBUG`, so `-v` shows it as
`[INFO]   cli: unexpected error`. devkit keeps its existing source label by passing its own logger: `Boundary` takes
`log: logging.Logger | None` for that record (default `<name>.cli`).

### 2.3 `devkit_dist.adapters.cli`

`BOUNDARY = Boundary("devkit")`; `boundary = BOUNDARY`, `output_options = BOUNDARY.output_options`,
`resolve_output = BOUNDARY.resolve_output`, `QUIET_ENV`/`VERBOSE_ENV`/`STRICT_ENV` from it; every other output name
re-exported from `devkit_cli`. `workspace_option`, `WORKSPACE_HELP`, `existing_directory` and `resolve_root` stay.
`devkit_dist.cli._LazyGroup` derives from `devkit_cli.LazyGroup` with `COMMANDS` and adds plugin and harness lookup
in `resolve_lazy`.

### 2.4 `cli-tool` bundle (`devkit_catalog/cli_tool/bundle/`)

- Instruction `cli-tool-structure`: when to use it (a new agent-facing CLI tool), dependency lines, package layout
  (`cli/` adapters → use cases → services/repositories; library code never prints), the boundary and output
  contract by example, errors and exit codes, lazy groups and the import budget (`python -X importtime`), tests with
  `devkit_cli.testing`, and the rules.
- `RULE-cli-tool-command-boundary` (linter, error): in CLI modules, a function decorated with `*.command(...)` or
  `*.group(...)` (also `command`/`group` imported from click) needs a decorator named in `boundary_names` (default
  `["boundary"]`), bare, called or as an attribute's last part. Group callbacks are not checked: groups only
  dispatch.
- `RULE-cli-tool-library-output` (linter, error): `print(...)` anywhere outside `exclude`; `click.echo`,
  `click.secho`, `sys.stdout.write` and `sys.stderr.write` outside CLI modules.
- `RULE-cli-tool-heavy-imports` (linter, error): module-level `import`/`from` in CLI modules whose top-level or full
  dotted name is in `heavy_modules` (a default list of heavy third-party libraries, extended by
  `extra_heavy_modules`); imports inside functions and under `if TYPE_CHECKING:` are allowed.
- Settings shared by the three: `cli_modules` (patterns, default `["**/cli.py", "**/cli/**/*.py",
  "**/__main__.py"]`), `exclude` (default the test patterns), per-path overrides through the rules engine.
- Presets: the implicit `all` (default) with the instruction and the three rules; `guide` with the instruction only.
- Each rule is its own plugin package directory (`rules/<name>/rule.py`, `guide.md`, `tests/`).

### 2.5 Packaging

`packages/devkit-cli/pyproject.toml` at the lockstep version `0.1.1`; root workspace (`pyproject.toml` members,
pyright paths, pytest paths), `scripts/_lib.sh` short name `cli`, `scripts/affected_tests.py` full-run prefix,
`scripts/release.sh` lockstep list, wheel variable and every install line, `test_lockstep`, `tests/e2e/smoke.sh`,
README, guides, package READMEs and `ARCH-07-deployment` install lines.

## 3. Verification & Test Plan

- `packages/devkit-cli/tests/`: unit tests for options and settings; integration tests for AC-01 to AC-08 through
  real click commands; an import test in a subprocess for AC-07.
- `packages/devkit-advisory/tests`: AC-09 (`ArgumentError` fields, export, mode); devkit-core test for the
  subclass relation.
- AC-10: the existing `packages/devkit-dist/tests/integration/adapters/test_cli.py` and the command suites, through
  `just test-affected` (adapter changes select the full suite).
- Rules: tests in each rule's `tests/` (AC-13 to AC-15); `devkit-catalog` bundle test for AC-12.
- AC-11: `test_lockstep` and a dry check of the release-notes text in its test.
- `just lint`, `just check`, `just rules-check`, `just test-dist`, `just smoke`.
