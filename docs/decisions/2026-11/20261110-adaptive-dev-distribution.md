---
id: ADR-adaptive-dev-distribution
title: Ship the adaptive-dev bundle from a dedicated devkit-adaptive distribution
summary: "For adaptive development that is to gain commands, we ship the adaptive-dev bundle from a dedicated devkit-adaptive wheel instead of the content-only devkit-catalog, to let it carry code while the catalog stays dependency-free, accepting one more wheel to release and install."
proposal: SPEC-adaptive-package-extraction
supersedes: [ADR-adaptive-development-and-research]
status: accepted
created_at: 2026-11-10
---

# [ADR-adaptive-dev-distribution] Ship the adaptive-dev bundle from a dedicated devkit-adaptive distribution

- **Status**: Accepted
- **Date**: 2026-11-10
- **Involved Components/Capabilities**: `packages/devkit-adaptive/`, `packages/devkit-catalog/`,
  `CAP-DLV-adaptive-development`, `CAP-HARN-agent-guidance`, `ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-07-deployment`, `guides/`

---

## 1. Context & Problem Statement

`ADR-adaptive-development-and-research` placed the `adaptive-dev` bundle in `devkit-catalog` and rejected a dedicated
wheel because no runtime dependency required one. `MS-adaptive-development-runtime` plans commands that record
delegated assignments and verify returned results (`SPEC-adaptive-assignment-cli`). A command needs Python code, a
`devkit.commands` entry point and runtime requirements.

`devkit-catalog` holds content only and declares no runtime requirement. Projects that never use adaptive
development select its other bundles, and `devkit bundle snapshot` accepts a source only while it has no runtime
requirement and no entry point besides `devkit.bundles` (`CAP-DIST-in-repo-bundles` §8). Code for adaptive
development inside the catalog would end both properties for every catalog bundle.

A project selects the bundle by its name `adaptive-dev` in `.devkit/config.toml`, and the receipt records the
distribution that provides it. The name, presets and asset IDs are consumer-facing; the owning wheel appears only in
the installation command and the receipt. Nothing uses the bundle outside this repository.

Evidence and option tables: `docs/materials/2026-11/20261110-adaptive-package-extraction/planning-evidence.md` of `SPEC-adaptive-package-extraction`.

## 2. Decision Drivers

- Adaptive development can gain commands without a second move.
- The catalog stays content-only, dependency-free and a snapshot source.
- The bundle name, presets, asset IDs and the context file name do not change.
- The bundle installs without `devkit-spec`.
- The move itself changes neither agent behavior nor an installed closure and adds no command.
- No alias distribution, shim module, duplicate registration or migration path while there are no external
  consumers (`ADR-package-ownership-and-release-version`).
- An unchanged bundle keeps its version (`ARCH-07-deployment` §1.1).

## 3. Considered Options

### Owner of the bundle

- **Keep the bundle in `devkit-catalog` and add the commands there**: no move; the catalog gains code, runtime
  requirements and a command group, and stops being a snapshot source for all of its bundles.
- **Keep the bundle in the catalog and put the commands in `devkit-agt`**: no new wheel; guidance and the commands it
  names release from two wheels.
- **Move the bundle into `devkit-spec`**: an existing application package; adaptive development then requires the
  SDD package that `CAP-DLV-adaptive-development` rule 2 excludes.
- **A dedicated `devkit-adaptive` distribution shaped like `devkit-spec`** (selected): one owner for the bundle and
  its later commands; one more wheel in the workspace, the release inventory and the installation commands.

### Contents of the wheel at the move

- **Bundle only: no runtime requirement and only the `devkit.bundles` entry point** (selected): the installed
  closure and every command behave as before; the first command adds what it needs.
- **Declare the requirements and a `devkit.commands` group at the move**: fewer edits later; a visible
  `devkit adaptive` group without subcommands, a changed installed closure and the end of snapshot support, all in
  a change that adds no function.

### Existing selections

- **No migration path** (selected): nothing uses the bundle outside this repository, so the catalog drops it without
  a bridge and the guides describe a fresh installation only.
- **A bridge: `devkit-catalog` requires `devkit-adaptive`, or keeps a second registration or an alias**: a
  requirement ends the catalog's dependency-free, snapshot-source contract for all of its bundles, and two
  registrations of one bundle name are refused by discovery; both serve consumers that do not exist.

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
- The change that adds the first command (`SPEC-adaptive-assignment-cli`) adds the wheel's runtime requirement,
  whose base is `devkit-docs`, and records the effect of that requirement and of the command entry point.
- The move has no migration path for an existing selection, because nothing uses the bundle outside this
  repository: `devkit-catalog` gains no runtime requirement on `devkit-adaptive`, no second registration and no
  alias, and the installation guides name `devkit-adaptive` for fresh installations only.
- Release preparation identifies a moved bundle by its name, so the unchanged bundle keeps its version while the new
  distribution takes the release version. → `ARCH-07-deployment` §1.1 (MUST)
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
- Negative: a selection of `adaptive-dev` made while the catalog shipped it gets no migration path; none exists
  outside this repository.
- Follow-up: when `SPEC-adaptive-assignment-cli` adds the first command, it adds the requirement on `devkit-docs`
  and records what the requirement and the command entry point change for this source.

## 6. Confirmation

- `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py`: the entry point value, the bundle name
  and the presets.
- `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`: built wheels without
  `devkit-spec` and without `devkit-catalog` deploy the three presets.
- `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`: every bundle directory of the catalog is
  registered, so a remaining `adaptive_dev` directory fails.
- `tests/e2e/smoke.sh`: `devkit-adaptive` provides `adaptive-dev` in an installed consumer.
- `RULE-architecture` over `.devkit/architecture.toml`: the declared package root and its data root.
- `packages/devkit/tests/integration/package/test_selective_releases.py`: a bundle moved unchanged to a new package
  keeps its version.
- The guides name `devkit-adaptive` for a fresh installation and hold no step for an existing selection: review.
- The absence of a runtime requirement and of a `devkit.commands` entry point at the move: a package metadata
  assertion in `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` until the first command
  replaces it.
