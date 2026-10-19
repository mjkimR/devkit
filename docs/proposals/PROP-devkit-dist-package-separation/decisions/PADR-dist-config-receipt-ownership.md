---
id: PADR-dist-config-receipt-ownership
title: Configuration and receipt schema ownership
summary: devkit-dist owns the .devkit/config.toml schema and the installation receipt; harness tables stay reserved pass-through names, and their commented templates are contributed by devkit-agt through an entry point.
proposal: PROP-devkit-dist-package-separation
status: draft
created_at: 2026-10-19
---

# [PADR-dist-config-receipt-ownership] Configuration and receipt schema ownership

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q3 (configuration schema ownership) of `PROP-devkit-dist-package-separation`.

---

## 1. Context & Problem Statement

`.devkit/config.toml` is read by `devkit.distribution.installation.config`. It accepts a closed set of top-level
fields (`FIELDS`): distribution's own (`schema`, `agents`, `presets`, `playbooks`, `guidance_block`,
`override_drift`, `bundles`), the harness tables `rules`, `workflow`, `gates`, `worktree` and `integration`, which it
passes through unread for the engines that own them, and `[tool.<name>]` tables, validated only as tables of tables.
Any other top-level key is refused so typos are caught. The commented template that `devkit config template` and
the first selection command write holds distribution's keys, three harness tables hard-coded in distribution
(`[workflow.approvals]`, `[workflow.stages]`, `[worktree]`, kept there "so distribution does not import higher
layers") and the `[tool.<name>]` tables that installed tools register under the `devkit.config_template` entry point
group (devkit-spec registers `[tool.spec]`).

The receipt `.devkit/installation.json` is defined in `devkit.core.receipt` (read by distribution, host, rules, gate,
workflow and worktree) and written by distribution. It records the writing tool (`tool.package`, now `devkit-agt`)
and, per deployed bundle, the distribution that shipped it.

## 2. Decision Drivers

- One owner per file format: the package that writes it.
- A project's configuration stays valid whether or not `devkit-agt` is installed, and keeps catching typos.
- `devkit-dist` holds no harness defaults that can drift from the engines that apply them.
- No new mechanism beyond what the split needs.

## 3. Considered Options

- **C1: status quo inside `devkit-dist`.** `devkit-dist` keeps the closed field list and the three hard-coded
  harness template tables. Pros: no code change. Cons: a standalone project's template advertises
  `[workflow.approvals]` and `[worktree]` for engines it does not have, and the harness defaults (`ask`, `on`,
  `14d`, ...) live in a package that does not apply them.
- **C2: reserved names in `devkit-dist`, harness templates contributed by `devkit-agt` (selected).** The closed
  field list keeps the harness table names as reserved pass-through names. `devkit-agt` registers the commented
  templates of its tables through a `devkit.config_tables` entry point group whose entry name is a reserved
  top-level table; `devkit-dist` renders them like `[tool.<name>]` templates and refuses (with the existing
  `CONFIG_TEMPLATE_EXTENSION_FAILED` warning) an entry whose name is not reserved. Pros: validation and typo
  detection unchanged in both installations; each template lives with the engine that applies it; a standalone
  template shows only what is installed. Cons: one more small entry point group; `devkit-dist` still knows the five
  reserved names.
- **C3: open field list, top-level names registered by entry point.** Pros: `devkit-dist` knows no harness name.
  Cons: a configuration with `[workflow]` becomes invalid the moment `devkit-agt` is absent, so removing or not yet
  installing the harness breaks `devkit sync`; typo detection depends on the installed set.
- **C4: move harness settings under `[tool.devkit-agt]`.** Cons: breaks every configuration, policy reader and
  document that names `[workflow.*]`, `[worktree]`, `[rules]` and `[gates]`, for no functional gain.

## 4. Decision Outcome

Choose **C2**.

- `devkit-dist` MUST own the `.devkit/config.toml` schema (`SCHEMA`, the closed top-level field list, the
  `[tool.<name>]` table rule) and the commented-template renderer, and the receipt format (`devkit.core.receipt`)
  and its writer.
- The field list MUST keep `rules`, `workflow`, `gates`, `worktree` and `integration` as reserved names passed
  through unread, so a configuration reads the same with or without `devkit-agt`.
- The commented templates of `[workflow.approvals]`, `[workflow.stages]` and `[worktree]` MUST move to
  `devkit-agt`, registered under a `devkit.config_tables` entry point group named after the reserved table; an entry
  whose name is not reserved is left out with `CONFIG_TEMPLATE_EXTENSION_FAILED`.
- Tools keep contributing `[tool.<name>]` tables through `devkit.config_template` unchanged (devkit-spec's
  `[tool.spec]`).
- The receipt's `tool.package` MUST name the running distributor, `devkit-dist`. Each bundle's package record names
  the wheel that ships it. The receipt schema version does not change; an existing receipt written by `devkit-agt`
  stays readable, and the next writing sync records the new names (the existing tool-version notice reports the
  change).

## 5. Consequences

- `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions` and `CAP-DIST-workspace-ownership` state the owner of
  each format and the new entry point group; `ARCH-05-4-distribution-components` lists it.
- A project that installs only `devkit-dist` gets a template without harness tables; adding `devkit-agt` and running
  `devkit config template` adds them without changing a line.
- Snapshot gates (`devkit rules check --staged`, `--ci`) keep trusting the committed receipt: file hashes and paths
  are unchanged by the split, only the package names it records.
