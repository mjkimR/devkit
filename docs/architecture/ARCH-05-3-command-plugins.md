---
id: ARCH-05-3-command-plugins
title: Command Plugins
summary: Entry point mounting specification for external command plugins mounted under the devkit CLI.
status: active
created_at: 2026-10-17
---

# [ARCH-05-3-command-plugins] Command Plugins

An installed package adds a command group to the `devkit` command line through the `devkit.commands` entry-point group, the way a content package adds a bundle through `devkit.bundles` (`CAP-DIST-content-packages`). A methodology layer built on devkit (devkit-spec mounts `devkit spec`) ships its commands, its bundle and its rules in one wheel, and agents reach all of it through the one `devkit` executable of the project environment.

## 1. Declaring a Command

```toml
[project]
dependencies = ["devkit>=0.1,<0.2"]

[project.entry-points."devkit.commands"]
spec = "devkit_spec.cli:cli"
```

- The entry point name is the command name (`devkit spec ...`); its value is the `module:attribute` of a click command, usually a `click.Group`.
- Names follow the bundle slug grammar (`^[a-z][a-z0-9-]*$`) by convention. The built-in command names (`sync`, `rules`, `worktree`, ...) are reserved: a plugin that declares one is ignored and the built-in command runs.
- The module is imported only when its command is invoked, or when the root `devkit --help` lists every command. Keep its import cheap: import heavy dependencies inside the command functions, as the built-in groups do.

## 2. Loading

- The root group reads the entry points only for a name that is not built in, or for the root `--help`, so a built-in command never pays for the scan.
- One target declared twice (one package visible through two paths) counts once.
- A plugin that cannot be used fails only its own command, with `COMMAND_PLUGIN_INVALID` (`MAINTENANCE`, exit `2`): its module fails to import, its attribute is missing or is not a click command, or two packages declare the same name with different targets. The error names each target and the package that declares it. Every other command keeps working, `devkit --help` lists the plugin as `Unusable plugin command (COMMAND_PLUGIN_INVALID)`, and `--format json` among the arguments returns the error as `{"error": {...}}` on stdout.
- Plugins run in the project environment like every devkit command: `uv run devkit <name>`. A tool installed in its own environment (`uv tool install <wheel-path>`) sees only the plugins installed there.

## 3. Contract for Plugin Commands

A plugin command is a devkit command, so it keeps the output contract an agent relies on:

- Build every command on `devkit.core.cli`: `boundary`, `FORMAT_OPTION`, `workspace_option`, `echo_json`, `echo_notices`, `exit_on_warnings`, `exit_on_problems`. The boundary gives it the output options, the Agent Advisory Protocol rendering and the exit codes of `ARCH-08-1-agent-output`.
- Raise `AdvisoryError` subclasses with the plugin's own stable codes, prefixed by its domain (`SPEC_...`), and document them in the plugin's own docs; never reuse a devkit code for a different condition.
- `devkit --version` prints only devkit's version. A plugin that reports its own version does so under its group (`devkit spec --version`) with a `[VERSION: <package> <version>]` line.
- Use devkit through each module's public surface (`devkit.<module>` `__init__` exports and `devkit.core.cli`), never its private helpers. devkit makes breaking changes in place while it has no external consumers ([AGENTS.md](../../AGENTS.md#compatibility)), so a plugin pins devkit to a minor range and moves with it.
