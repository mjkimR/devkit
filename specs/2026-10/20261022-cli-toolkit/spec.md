---
id: SPEC-cli-toolkit
title: Agent-first CLI toolkit package and catalog bundle
summary: Adds the devkit-cli package with the reusable agent-first CLI boundary that devkit-dist builds on, and an opt-in devkit-catalog cli-tool bundle with the structure guide and rules for new CLI tools.
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-ADV-agent-advisory-protocol
  - CAP-CLI-agent-cli-toolkit
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-cli-toolkit] Agent-first CLI toolkit package and catalog bundle

## 1. Problem Statement & Motivation

New command-line tools in the user's repositories are written by AI agents, and every agent invents its own shape:
argparse in one tool, its own error classes and exit codes in another, every command group imported eagerly in a
third. All of them are used by agents (human → agent → CLI), so they need the agent-first output contract that
`ARCH-08-1-agent-output` defines for `devkit`. That contract is implemented once, in `devkit_dist.adapters.cli`, but
only for `devkit`: its environment names, logger and project lookup are devkit's, and a tool cannot depend on
`devkit-dist` just for its boundary.

Its details (one JSON document even for a failure, no advisory repeated on stderr in JSON mode, a closed stdout
ending the command with exit `2`, UTF-8 regardless of the locale, flags combined with the environment) are not
reproduced reliably from a prose guide. They are delivered as code, and the structure around them as a guide with
rules that check it.

## 2. User Stories

- **US-1**: As an agent building a new CLI tool, I want a small library that gives my commands devkit's output
  contract, so that every tool reports results, advisories and exit codes the same way without reimplementing them.
- **US-2**: As the user, I want an opt-in bundle that tells agents how to structure a CLI tool and checks the
  structure, so that new tools stop diverging.
- **US-3**: As a devkit maintainer, I want `devkit` itself to run on that library, so that there is one
  implementation of the contract.

## 3. Non-Goals

1. **Scope Excluded**: changing existing consumer tools (app-tools, rside, agentkit, resource-indexer). The bundle
   applies to tools created after it.
2. **Scope Excluded**: a use case base class, dependency injection, configuration loading, workspace discovery,
   command plugin discovery or an MCP adapter in `devkit-cli`. The use case convention is stated in the guide only;
   tools do not depend on `devkit-core`.
   - **When to Reconsider**: two tools copy the same piece of wiring outside the boundary.
3. **Scope Excluded**: selecting the `cli-tool` bundle in this repository. devkit's own structure is governed by
   the `devkit-dev` bundle.
4. **Scope Excluded**: any change to the output contract of `devkit` commands. Moving the implementation preserves
   every byte, exit code and option of `ARCH-08-1-agent-output`.
5. **Scope Excluded**: human-oriented output (colour, tables, progress, interactive prompts) in the toolkit.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The toolkit renders a failure as one advisory and exits with its code
- **Given** a click command decorated with a `devkit_cli.Boundary("mytool")` instance that raises an
  `AdvisoryError` with code `THING_MISSING` and exit code `1`
- **When** it runs without `--format json`
- **Then** stdout is empty, stderr is the error's rendered advisory block once, and the exit code is `1`

### [AC-02] JSON mode carries the error and the collected notices in one document
- **Given** the same command taking `--format` through `devkit_cli.FORMAT_OPTION`, which passes a `NOTICE` to
  `echo_notices` before raising
- **When** it runs with `--format json`
- **Then** stdout is exactly one JSON object with `error.code == "THING_MISSING"` and one entry under `notices`,
  stderr is empty, and the exit code is `1`

### [AC-03] Output options follow the tool's own environment prefix
- **Given** a command under `Boundary("mytool")` that returns one `WARNING` and one `NOTICE` through `echo_notices`
  and `exit_on_warnings`
- **When** it runs with `MYTOOL_QUIET=1`, then with `MYTOOL_STRICT=1`, then with `-q -v`
- **Then** the first run prints the `[WARN]` block and no `[NOTICE]` block and exits `0`; the second exits `1`; the
  third exits `2` with an `ARGUMENT_INVALID` advisory

### [AC-04] Verbose output shows the tool's log records
- **Given** a command under `Boundary("mytool")` that logs `checked 3 files` at `DEBUG` on the `mytool.scan` logger
- **When** it runs with `-v`
- **Then** stderr contains the line `[INFO]   scan: checked 3 files`; without `-v` stderr contains no `[INFO]` line

### [AC-05] An unexpected exception and a closed reader keep the contract
- **Given** a command under a boundary
- **When** it raises `RuntimeError`, and separately when its stdout reader closes early
- **Then** the first exits `2` with an `UNEXPECTED_ERROR` advisory, and the second exits `2` with nothing written to
  stderr

### [AC-06] Lazy groups import a command only when it runs
- **Given** a `devkit_cli.LazyGroup` declaring `scan` as `"pkg.scan:command"` and `report` as `"pkg.report:command"`
- **When** `scan` is invoked
- **Then** `pkg.scan` is in `sys.modules` and `pkg.report` is not; a declared target that is not a click command
  raises `TypeError` naming the target

### [AC-07] Importing the toolkit stays within its dependencies
- **Given** a fresh interpreter
- **When** it imports `devkit_cli`
- **Then** every newly imported top-level module is from the standard library, `click`, `devkit` (the advisory
  namespace) or `devkit_cli`

### [AC-08] Tests can assert the contract through the testing helper
- **Given** a command under a boundary taking `--format` that raises `THING_MISSING` (exit code `1`) and returns no
  notice
- **When** a test calls `devkit_cli.testing.invoke(command, ["--format", "json"])`
- **Then** the returned outcome's `exit_code` is `1`, `json()` returns the one object, and `codes()` on a text-mode
  run returns `["THING_MISSING"]`

### [AC-09] The argument error is part of the advisory library
- **Given** `devkit.advisory`
- **When** a caller raises `devkit.advisory.ArgumentError("--limit must be positive")`
- **Then** its code is `ARGUMENT_INVALID`, its mode is `INPUT_ERROR`, its exit code is `2`, and
  `devkit_core.base.errors.ArgumentError` is a subclass of it

### [AC-10] devkit keeps its output contract on the toolkit
- **Given** `devkit_dist.adapters.cli` built on `devkit_cli` with the `devkit` logger and the `DEVKIT_` prefix
- **When** the existing adapter and command test suites run
- **Then** they pass unchanged in behavior: the same options, environment names, stdout, stderr and exit codes

### [AC-11] The toolkit is released with the lockstep packages
- **Given** the release script and the lockstep test
- **When** a release is built for a tag
- **Then** `devkit-cli` is checked against the tag version with `devkit-core`, `devkit-dist`, `devkit-agt`,
  `devkit-advisory` and `devkit-mcp`, and every install command that names the `devkit-dist` wheel also names the
  `devkit-cli` wheel

### [AC-12] The catalog bundle is opt-in and complete
- **Given** `devkit-catalog` installed in a project
- **When** the project runs `devkit sync` without selecting it, and then `devkit add cli-tool`
- **Then** the first deploys nothing of `cli-tool`; the second deploys the `cli-tool-structure` instruction and the
  rules `RULE-cli-tool-command-boundary`, `RULE-cli-tool-library-output` and `RULE-cli-tool-heavy-imports`

### [AC-13] Commands without a boundary are reported
- **Given** `RULE-cli-tool-command-boundary` with default settings and a CLI module `src/pkg/cli.py` containing one
  function decorated with `@click.command()` and `@boundary` and one decorated with `@group.command()` only
- **When** the rule runs
- **Then** it reports exactly one `error` violation, at the second function's line

### [AC-14] Printing outside the CLI layer is reported
- **Given** `RULE-cli-tool-library-output` with default settings
- **When** `src/pkg/services/scan.py` calls `print(...)` and `click.echo(...)`, and `src/pkg/cli.py` calls
  `click.echo(...)` and `print(...)`
- **Then** it reports the two calls in `services/scan.py` and the `print` in `cli.py`, and not the `click.echo` in
  `cli.py`

### [AC-15] Heavy imports at CLI module level are reported
- **Given** `RULE-cli-tool-heavy-imports` with default settings
- **When** `src/pkg/cli.py` has `import httpx` at module level and `import numpy` inside a command function
- **Then** it reports only the module-level `httpx` import; adding `"pkg.models"` to `heavy_modules` also reports a
  module-level `from pkg.models import Model`

## 5. Assumptions

- The package is `devkit-cli` with the independent import package `devkit_cli` (not a `devkit` namespace member),
  depending on `click` and `devkit-advisory` only, versioned and released in lockstep with `devkit-dist` and
  `devkit-agt`, and treated as a semver contract like `devkit-advisory` because tools outside this repository will
  depend on it at runtime.
- `ARGUMENT_INVALID` moves to `devkit.advisory.ArgumentError`, an additive change to the advisory API:
  `devkit-cli` raises it for conflicting output options without depending on `devkit-core`, and
  `devkit_core.base.errors.ArgumentError` derives from both `DevkitCoreError` and it, so the code keeps one owner
  (`RULE-advisory-unique-code`).
- The bundle is named `cli-tool` (not `cli`) so its rule IDs do not read as part of the built-in
  `RULE-cli-contract`.
- `devkit_dist.adapters.cli` stays the import path devkit's own commands use; it configures the toolkit for devkit
  and keeps the devkit-only helpers (`workspace_option`, `resolve_root`, `existing_directory`).
- The rules read source files statically and select CLI modules by path patterns (default `**/cli.py`,
  `**/cli/**/*.py`, `**/__main__.py`), with per-path overrides, as the other bundled rules do.
