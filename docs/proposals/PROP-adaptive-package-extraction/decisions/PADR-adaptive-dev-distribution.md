---
id: PADR-adaptive-dev-distribution
title: Ship the adaptive-dev bundle from a dedicated devkit-adaptive distribution
summary: "For adaptive development that is to gain commands, we ship the adaptive-dev bundle from a dedicated devkit-adaptive wheel instead of the content-only devkit-catalog, to let it carry code while the catalog stays dependency-free, accepting one more wheel to release and install."
proposal: PROP-adaptive-package-extraction
supersedes: [ADR-adaptive-development-and-research]
status: draft
created_at: 2026-11-10
---

# [PADR-adaptive-dev-distribution] Ship the adaptive-dev bundle from a dedicated devkit-adaptive distribution

- **Status**: Draft
- **Date**: 2026-11-10
- **Involved Components/Capabilities**: `packages/devkit-adaptive/`, `packages/devkit-catalog/`,
  `CAP-DLV-adaptive-development`, `CAP-HARN-agent-guidance`, `ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-07-deployment`, `guides/`

---

## 1. Context & Problem Statement

`ADR-adaptive-development-and-research` placed the `adaptive-dev` bundle in `devkit-catalog` and rejected a dedicated
wheel because no runtime dependency required one. `MS-adaptive-development-runtime` plans commands that record
delegated assignments and verify returned results (`PROP-adaptive-assignment-cli`). A command needs Python code, a
`devkit.commands` entry point and runtime requirements.

`devkit-catalog` holds content only and declares no runtime requirement. Projects that never use adaptive
development select its other bundles, and `devkit bundle snapshot` accepts a source only while it has no runtime
requirement and no entry point besides `devkit.bundles` (`CAP-DIST-in-repo-bundles` §8). Code for adaptive
development inside the catalog would end both properties for every catalog bundle.

A project selects the bundle by its name `adaptive-dev` in `.devkit/config.toml`, and the receipt records the
distribution that provides it. The name, presets and asset IDs are consumer-facing; the owning wheel appears only in
the installation command and the receipt.

Evidence and option tables: `materials/planning-evidence.md` of `PROP-adaptive-package-extraction`.

## 2. Decision Drivers

- Adaptive development can gain commands without a second move.
- The catalog stays content-only, dependency-free and a snapshot source.
- The bundle name, presets, asset IDs and the context file name do not change.
- The bundle installs without `devkit-spec`, and its `agents` and `import` presets install without `devkit-agt`.
- The move itself changes no agent behavior and adds no command.
- No alias distribution, shim module or duplicate registration (`ADR-package-ownership-and-release-version`).

## 3. Considered Options

### Owner of the bundle

- **Keep the bundle in `devkit-catalog` and add the commands there**: no move; the catalog gains code, runtime
  requirements and a command group, and stops being a snapshot source for all of its bundles.
- **Keep the bundle in the catalog and put the commands in `devkit-agt`**: no new wheel; guidance and the commands it
  names release from two wheels, and a project that uses the `agents` or `import` preset on `devkit-dist` alone
  never gets the commands.
- **Move the bundle into `devkit-spec`**: an existing application package; adaptive development then requires the
  SDD package that `CAP-DLV-adaptive-development` rule 2 excludes.
- **A dedicated `devkit-adaptive` distribution shaped like `devkit-spec`** (selected): one owner for the bundle and
  its later commands; one more wheel in the workspace, the release inventory and the installation commands.

### Contents of the wheel at the move

- **Bundle only: no runtime requirement and only the `devkit.bundles` entry point** (selected): the installed
  closure and every command behave as before; the first command adds what it needs.
- **Declare the requirements and a `devkit.commands` group at the move**: fewer edits later; a visible
  `devkit adaptive` group without subcommands, a harness installed for consumers that had none when the requirement
  is `devkit-agt`, and the end of snapshot support, all in a change that adds no function.

## 4. Decision Outcome

The `adaptive-dev` bundle ships from a dedicated `devkit-adaptive` distribution that holds the bundle alone at the
move, because this is the only option that lets adaptive development carry code while the catalog stays
content-only, the bundle stays independent of `devkit-spec` and the move changes no behavior.

This decision replaces these parts of `ADR-adaptive-development-and-research`: in its "Adaptive-dev bundle" outcome,
the bundle's place "in devkit-catalog" with the entry point `devkit_catalog.adaptive_dev`, and "content-only catalog
ownership" and "independent docs/catalog installation" as far as they concern `adaptive-dev`; the rejection of "Add a
dedicated wheel"; and the driver "without another release wheel". Its approach, SDD adoption, current-context,
discovery, materials and deep-research decisions stay in force, as do the names `adaptive-dev`, `/adaptive-dev` and
`.devkit/adaptive-dev.md`. `deep-research` stays a catalog bundle.

- The `devkit-adaptive` distribution owns the `adaptive-dev` bundle; `devkit-catalog` neither registers nor ships it.
- The distribution owns the regular package `devkit_adaptive` and places the bundle at
  `devkit_adaptive/bundles/adaptive_dev/bundle/`, registered as
  `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`.
- The bundle name `adaptive-dev`, the presets `core`, `agents` and `import` and every asset ID are unchanged. →
  `CAP-DLV-adaptive-development` rule 1 (MUST)
- The bundle installs with devkit-docs and `devkit-adaptive` without a `devkit-spec` distribution. →
  `CAP-DLV-adaptive-development` rule 2 (MUST)
- At the move the wheel declares no runtime requirement and no entry point besides `devkit.bundles`, and holds no
  feature, command or runtime module.
- The change that adds the first command adds its requirements and decides their base (`devkit-dist` or
  `devkit-agt`) together with the effect on the `agents` and `import` presets and on snapshot support.
- A runtime scheduler, an agent bus and model routing stay excluded.

`ARCH-05-2-components` §1.1 and the `adaptive-dev` paragraph of `ARCH-07-deployment` describe the owner, layout and
registration;
`CAP-DLV-adaptive-development` §2 keeps the remaining exclusions.

## 5. Consequences

- Positive: commands for adaptive development have an owning package with `bundles/` and room for `features/`, and
  the catalog keeps its content-only contract.
- Positive: no asset, projection or guidance text changes, so the move is verifiable as an unchanged bundle tree.
- Negative: the workspace, the release inventory, the consumer smoke and the installation guides carry one more
  wheel.
- Negative: a project that selected `adaptive-dev` while the catalog shipped it needs `devkit-adaptive` in its
  environment after the move.
- Risk: an environment that holds a catalog release that still registers the bundle beside `devkit-adaptive` fails
  every command with `BUNDLE_PACKAGE_INVALID`. Installing both from one commit or one release inventory avoids it
  (`ARCH-07-deployment` §1.1).
- Follow-up: when `PROP-adaptive-assignment-cli` adds the first command, it records the base requirement and the
  loss of snapshot support for this source.

## 6. Confirmation

- `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py`: the entry point value, the bundle name
  and the presets.
- `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`: built wheels without
  `devkit-spec` and without `devkit-catalog` deploy the three presets.
- `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`: every bundle directory of the catalog is
  registered, so a remaining `adaptive_dev` directory fails.
- `tests/e2e/smoke.sh`: `devkit-adaptive` provides `adaptive-dev` in an installed consumer.
- `RULE-architecture` over `.devkit/architecture.toml`: the declared package root and its data root.
- The absence of a runtime requirement and of a `devkit.commands` entry point at the move: a package metadata
  assertion in `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` until the first command
  replaces it.
