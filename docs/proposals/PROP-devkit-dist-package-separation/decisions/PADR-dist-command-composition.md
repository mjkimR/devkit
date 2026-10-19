---
id: PADR-dist-command-composition
title: Harness commands mount through devkit.commands
summary: devkit-dist owns the devkit console script and only its own built-in commands; devkit-agt mounts its command groups through the existing devkit.commands entry point group.
proposal: PROP-devkit-dist-package-separation
status: draft
created_at: 2026-10-19
---

# [PADR-dist-command-composition] Harness commands mount through devkit.commands

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q2 (CLI and entry point aggregation) of `PROP-devkit-dist-package-separation`.

---

## 1. Context & Problem Statement

`devkit.cli` is a lazy click group: a static `COMMANDS` map names each built-in command as `module:attribute`
(the distribution commands, `run`, and the `rules`, `workflow`, `gate`, `worktree`, `generated`, `host` and
`integration` groups) and imports a module only when its command runs. Names that are not built in are looked up in
the `devkit.commands` entry point group (`ARCH-05-3-command-plugins`), which `devkit-spec` already uses for
`devkit spec`; built-in names are reserved and win over plugins, and an unusable plugin fails only its own command
with `COMMAND_PLUGIN_INVALID`. `devkit --version` reads the version of `devkit-agt`.

`PADR-dist-foundation-ownership` gives the sole `devkit` console script to `devkit-dist`, which must not depend on
`devkit-agt`, so the root group can no longer name harness modules.

## 2. Decision Drivers

- One `devkit` executable, owned by `devkit-dist`, with no competing console scripts.
- `devkit-dist` names no `devkit-agt` module (dependency direction).
- Existing command lines, output and codes keep working when `devkit-agt` is installed.
- Reuse the existing extension point rather than add a mechanism.

## 3. Considered Options

- **M1: `devkit-agt` registers its groups under `devkit.commands` (selected).** The root `COMMANDS` map keeps only
  `devkit-dist` commands; `devkit-agt` declares `rules`, `workflow`, `gate`, `worktree`, `generated` and
  `integration` (and `run` if `devkit.compact` stays with it) as entry points, exactly as `devkit-spec` declares
  `spec`. Pros: no new mechanism; laziness and failure isolation already exist; `devkit --help` lists what is
  installed. Cons: harness names lose their built-in reservation, so a third-party plugin declaring the same name
  makes that command fail with `COMMAND_PLUGIN_INVALID` instead of being ignored; a harness command pays one
  entry point scan on lookup.
- **M2: `devkit-dist` keeps the harness module paths in `COMMANDS` and reports a missing install.** Pros: a
  standalone installation could answer `devkit rules` with an install directive. Cons: the foundation hard-codes
  names and module paths of the package above it, breaking the dependency direction the split exists for.
- **M3: a separate first-party group (for example `devkit.builtin_commands`) that keeps reservation.** Pros:
  harness names keep winning over third-party plugins. Cons: a second loading path and precedence rule for a
  collision no package has today.
- **M4: `devkit-agt` ships its own `devkit` console script.** Cons: two wheels installing the same script is the
  competing-entry-point conflict `PADR-dist-foundation-ownership` rules out.

## 4. Decision Outcome

Choose **M1**.

- `devkit-dist` MUST own the `devkit` console script (`devkit.cli:cli`) and `devkit.__main__`; its built-in
  `COMMANDS` map MUST name only modules shipped by `devkit-dist`.
- `devkit-agt` MUST mount each of its command groups through a `devkit.commands` entry point with the command's
  current name and target, so command lines, options, output and codes stay unchanged.
- `devkit --version` MUST read the `devkit-dist` version; with lockstep releases it is the same number
  `devkit-agt` reported before (`PADR-dist-bundles-compatibility`).
- The MCP server's reported version and the receipt's tool record follow the same owner
  (`PADR-dist-config-receipt-ownership`).
- In a standalone installation a harness command name is an unknown command (click's usage error, exit `2`), like
  any other unknown name; no reverse knowledge of harness names is added to `devkit-dist`.

## 5. Consequences

- `ARCH-05-3-command-plugins` describes `devkit-agt` as a first-party plugin, and the layering test's assertion that
  `devkit.commands` is loaded by `cli` holds in `devkit-dist`.
- Verification covers command discovery with `devkit-dist` alone (no harness commands listed), with both wheels
  (every current command listed and runnable) and with `devkit-spec` added, and that exactly one installed
  distribution provides the `devkit` script.
- A harness command now pays one `devkit.commands` scan when it is looked up: about 10 to 13 ms in this workspace
  (61 installed distributions; `materials/20261019-package-split-evidence.md` section 5). Commit-time gates are not
  affected: the managed Git hook entry runs `devkit.gate` through its own bootstrap and never imports `devkit.cli`.
  Native host hooks call `devkit host`, a `devkit-dist` built-in, and pay no scan.
