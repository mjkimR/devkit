---
id: ARCH-05-3-command-plugins
title: Command Plugins
summary: "Entry point mounting of command groups under the devkit CLI of devkit-dist: devkit-agt's harness commands as first-party plugins, external plugins, lookup precedence and the name-only harness list."
status: active
created_at: 2026-10-17
---

# [ARCH-05-3-command-plugins] Command Plugins

An installed package adds a command group to the `devkit` command line through the `devkit.commands` entry-point group, the way a content package adds a bundle through `devkit.bundles` (`CAP-DIST-content-packages`). `devkit-dist` owns the `devkit` console script and its built-in commands; every other command is a plugin (`ADR-dist-command-composition`). `devkit-agt` is the first-party plugin: it mounts `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration` and `run` with their command lines, options, output and codes unchanged, and ships no console script of its own. A methodology layer built on devkit (devkit-spec mounts `devkit spec`) ships its commands, its bundle and its rules in one wheel, and agents reach all of it through the one `devkit` executable of the project environment.

## 1. Declaring a Command

```toml
[project]
dependencies = ["devkit-agt>=0.1,<0.2"]

[project.entry-points."devkit.commands"]
spec = "devkit_spec.cli:cli"
```

- The entry point name is the command name (`devkit spec ...`); its value is the `module:attribute` of a click command, usually a `click.Group`.
- Names follow the bundle slug grammar (`^[a-z][a-z0-9-]*$`) by convention. The built-in command names of `devkit-dist` (`sync`, `add`, `remove`, `list`, `status`, `config`, `recover`, `override`, `bundle`, `get-context`, `playbook`, `host`) are reserved: a plugin that declares one is ignored and the built-in command runs. The harness names are not built in: a third-party plugin declaring one of them next to `devkit-agt` is a second declaration of that name and fails with `COMMAND_PLUGIN_INVALID`.
- The module is imported only when its command is invoked, or when the root `devkit --help` lists every command. Keep its import cheap: import heavy dependencies inside the command functions, as the built-in groups do.

## 2. Loading

A name is looked up in this order:

1. the built-in map of `devkit-dist` (`devkit.cli.COMMANDS`, which names only `devkit-dist` modules);
2. the `devkit.commands` entry points of the installed packages;
3. the name-only harness list (`devkit.cli.HARNESS_COMMANDS`: `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration`, `run`), consulted only when neither of the above has the name. A listed name answers with `HARNESS_COMMAND_UNAVAILABLE` (`INTERACTION`, exit `2`, nothing on stdout; `--format json` among the arguments returns `{"error": {...}}` on stdout instead), whose `[FIX]` adds `devkit-agt` to the installation: in a project, replace the `devkit-dist` requirement with the full Git requirement of `devkit-agt` in the same dependency group; for a tool installation, `uv tool install --reinstall '<devkit-dist requirement>' --with '<devkit-agt requirement>'`. The list holds names only, never a module path or entry point target, and `devkit --help` never shows it. Any other unknown name keeps click's usage error (exit `2`). A `devkit-agt` test keeps the list equal to the `devkit.commands` names `devkit-agt` declares.

- The root group reads the entry points only for a name that is not built in, or for the root `--help`, so a built-in command never pays for the scan. A harness command pays one entry point scan per lookup (about 13 ms of the whole-process median measured in Planning); commit-time gates run `devkit.gate` through the hook bootstrap and never import `devkit.cli`, and native host hooks call `devkit host`, a built-in.
- One target declared twice (one package visible through two paths) counts once.
- A plugin that cannot be used fails only its own command, with `COMMAND_PLUGIN_INVALID` (`MAINTENANCE`, exit `2`): its module fails to import, its attribute is missing or is not a click command, or two packages declare the same name with different targets. The error names each target and the package that declares it. Every other command keeps working, `devkit --help` lists the plugin as `Unusable plugin command (COMMAND_PLUGIN_INVALID)`, and `--format json` among the arguments returns the error as `{"error": {...}}` on stdout.
- Plugins run in the project environment like every devkit command: `uv run devkit <name>`. A tool installed in its own environment sees only the plugins installed there, so a tool installation names the script owner and adds the harness: `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`, each a wheel path or a full Git requirement (`devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist`), never a bare package name the default index would resolve.

## 3. Contract for Plugin Commands

A plugin command is a devkit command, so it keeps the output contract an agent relies on:

- Build every command on `devkit.core.cli`: `boundary`, `FORMAT_OPTION`, `workspace_option`, `echo_json`, `echo_notices`, `exit_on_warnings`, `exit_on_problems`. The boundary gives it the output options, the Agent Advisory Protocol rendering and the exit codes of `ARCH-08-1-agent-output`.
- Raise `AdvisoryError` subclasses with the plugin's own stable codes, prefixed by its domain (`SPEC_...`), and document them in the plugin's own docs; never reuse a devkit code for a different condition.
- `devkit --version` prints only the version of `devkit-dist` (the same number as `devkit-agt` and `devkit-advisory`, released in lockstep). A plugin that reports its own version does so under its group (`devkit spec --version`) with a `[VERSION: <package> <version>]` line.
- Use devkit through each module's public surface (`devkit.<module>` `__init__` exports and `devkit.core.cli`), never its private helpers. devkit makes breaking changes in place while it has no external consumers ([AGENTS.md](../../AGENTS.md#compatibility)), so a plugin pins devkit to a minor range and moves with it.
