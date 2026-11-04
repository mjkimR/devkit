---
id: ARCH-05-3-command-plugins
title: Command Plugins
summary: "Entry point mounting of command groups under the devkit CLI of devkit-dist: devkit-agt's harness commands as first-party plugins, external plugins, lookup precedence and the name-only harness list."
status: active
created_at: 2026-10-17
---

# [ARCH-05-3-command-plugins] Command Plugins

An installed package adds a command group to the `devkit` command line through the `devkit.commands` entry-point group, the way a content package adds a bundle through `devkit.bundles` (`CAP-DIST-content-packages`). `devkit-dist` owns the `devkit` console script and its built-in commands; every other command is a plugin (`ADR-package-ownership-and-release-version`). `devkit-agt` is the first-party plugin: it mounts `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration` and `run` with their command lines, options, output and codes unchanged, and ships no console script of its own. A layer built on devkit ships its commands in its own wheel and mounts them the same way: devkit-docs mounts `devkit docs`, and the methodology layer devkit-spec, which depends on devkit-docs, mounts `devkit spec` and ships its bundle and its rules with it (`ADR-document-system`). Agents reach all of it through the one `devkit` executable of the project environment. Rules that bind an agent, a host or a playbook step are checked by review only unless they name a check.

## 1. Declaring a Command

```toml
[project]
dependencies = ["devkit-agt>=0.1,<0.2"]

[project.entry-points."devkit.commands"]
spec = "devkit_spec.cli:cli"
```

- The entry point name is the command name (`devkit spec ...`); its value is the `module:attribute` of a click command, usually a `click.Group`.
- Names SHOULD follow the bundle slug grammar (`^[a-z][a-z0-9-]*$`). The built-in command names of `devkit-dist` (`sync`, `add`, `remove`, `list`, `status`, `config`, `recover`, `override`, `bundle`, `get-context`, `playbook`, `host`) are reserved: a plugin that declares one is ignored and the built-in command runs. The harness names are not built in: a third-party plugin declaring one of them next to `devkit-agt` is a second declaration of that name and fails with `COMMAND_PLUGIN_INVALID`.
- The module is imported only when its command is invoked, or when the root `devkit --help` lists every command. Keep its import cheap: a plugin module SHOULD import heavy dependencies inside the command functions, as the built-in groups do.

## 2. Loading

A name is looked up in this order:

1. the built-in map of `devkit-dist` (`devkit_dist.cli.COMMANDS`, which names only `devkit-dist` modules);
2. the `devkit.commands` entry points of the installed packages;
3. the name-only harness list (`devkit_dist.cli.HARNESS_COMMANDS`: `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration`, `run`, `maintenance`), consulted only when neither of the above has the name. A listed name answers with `HARNESS_COMMAND_UNAVAILABLE` (`INTERACTION`, exit `2`, nothing on stdout; `--format json` among the arguments returns `{"error": {...}}` on stdout instead), whose `[FIX]` adds `devkit-agt` to the installation: in a project, replace the `devkit-dist` requirement with the full Git requirement of `devkit-agt` in the same dependency group; for a tool installation, `uv tool install --reinstall '<devkit-dist requirement>' --with '<devkit-agt requirement>'`. The list MUST hold names only, never a module path or entry point target, and `devkit --help` never shows it.
4. the name-only extra list (`devkit_dist.cli.EXTRA_COMMANDS`: `mcp`, from the `mcp` extra), consulted the same way. A listed name answers with `EXTRA_COMMAND_UNAVAILABLE` (`INTERACTION`, exit `2`), whose `[FIX]` for `mcp` is `MCP_INSTALL_FIX`: `devkit-agt[mcp]` when the project depends on devkit-agt, else `devkit-mcp` itself (devkit-dist declares no `mcp` extra).

Any other unknown name keeps click's usage error (exit `2`). The harness list MUST equal the `devkit.commands` names `devkit-agt` declares (a `devkit-agt` test checks it).

- The root group reads the entry points only for a name that is not built in, or for the root `--help`, so a built-in command never pays for the scan. A harness command pays one entry point scan per lookup (about 13 ms of the whole-process median, `ADR-package-ownership-and-release-version`); commit-time gates run `devkit_agt.features.gate` through the hook bootstrap and MUST NOT import `devkit_dist.cli`, and native host hooks call `devkit host`, a built-in.
- One target declared twice (one package visible through two paths) counts once.
- A plugin that cannot be used fails only its own command, with `COMMAND_PLUGIN_INVALID` (`MAINTENANCE`, exit `2`): its module fails to import, its attribute is missing or is not a click command, or two packages declare the same name with different targets. The error names each target and the package that declares it. Every other command keeps working, `devkit --help` lists the plugin as `Unusable plugin command (COMMAND_PLUGIN_INVALID)`, and `--format json` among the arguments returns the error as `{"error": {...}}` on stdout.
- Plugins run in the project environment like every devkit command: `uv run devkit <name>`. A tool installed in its own environment sees only the plugins installed there, so a tool installation MUST name the script owner and add the harness: `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`, each a wheel path or a full Git requirement (`devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist`), never a bare package name the default index would resolve.

## 3. Contract for Plugin Commands

A plugin command is a devkit command, so it keeps the output contract an agent relies on:

- Every plugin command MUST build on `devkit_dist.adapters.cli`: `boundary`, `FORMAT_OPTION`, `workspace_option`, `echo_json`, `echo_notices`, `exit_on_warnings`, `exit_on_problems`. The boundary gives it the output options, the Agent Advisory Protocol rendering and the exit codes of `ARCH-08-1-agent-output`.
- A plugin MUST raise `AdvisoryError` subclasses with its own stable codes, prefixed by its domain (`DOCS_...`, `SPEC_...`), and document them in its own docs. It MUST NOT reuse a devkit code for a different condition.
- `devkit --version` prints only the version of `devkit-dist` (the same number as `devkit-agt`, `devkit-core`, `devkit-cli`, `devkit-advisory` and `devkit-mcp`, released in lockstep; `ARCH-07-deployment`). A plugin that reports its own version MUST do so under its group (`devkit docs --version`, `devkit spec --version`) with a `[VERSION: <package> <version>]` line.
- A plugin MUST use devkit through each module's public surface (the owning independent namespace's documented exports and `devkit_dist.adapters.cli`), never its private helpers. Within `0.x` devkit can make breaking changes in any minor release, so a plugin SHOULD pin devkit to a minor range and move with it.

`devkit-mcp` contributes the `mcp` command group. It supplies `setup`, `remove`, `status` (including `--descriptor`) and the hidden `serve` entry point;
The former MCP subgroup under host and the dist MCP extra are absent. `serve` requires an explicit configuration workspace separate
from the retained executor root. Its stdout MUST carry only native MCP protocol traffic.
