# Content Packages

Bundles reach a project as Python packages installed with `uv`; `devkit` relies on standard packaging instead of a
registry, resolver or download cache of its own. The bundle itself is specified in the
[Manifest Specification](manifest-spec.md); repository-owned bundles in [In-Repository Bundles](in-repo-bundles.md).

## 1. Content Wheel Contract

A content wheel registers a resource module under the `devkit.bundles` entry-point group:

```toml
[project.entry-points."devkit.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

```text
src/package_b_playbooks/
  __init__.py               # empty; no runtime side effects
  bundle/                   # the bundle: bundle.toml, optional AGENTS.md, asset sources
```

- The entry point value names an importable module, not a callable; the bundle lives in its `bundle/` directory.
- The entry point name is the bundle name (`team` above registers the bundle `name = "team"`); a mismatch makes the
  package unusable (`BUNDLE_PACKAGE_INVALID`). The name identifies the bundle even when the package cannot be loaded.
- Loading the module runs ordinary module initialization, so `__init__.py` must have no runtime side effects.
- A sync reads files only through `importlib.resources.as_file`; it never executes or imports rule code.
- Bundle names are unique across the installed packages; two packages declaring the same name are an error
  (`BUNDLE_PACKAGE_INVALID`) for every command.
- An installed package that cannot be used (its module fails to import, its bundle is invalid, its entry point is
  malformed or misnamed) stops only what needs it: when the project selects its bundle, `sync`, `add`, `list` and the
  override commands fail with `BUNDLE_PACKAGE_INVALID` and `devkit status` reports it under `errors`; otherwise each
  of them reports it as a `BUNDLE_PACKAGE_INVALID` warning and continues, so `devkit remove <bundle>` can still
  deselect it while the package is upgraded or uninstalled.
- A repository without Python code (a prompt collection, a Go tool) can map its own layout into a content wheel at
  build time with Hatch `force-include`.

## 2. Installation and Lifecycle

```bash
uv add --dev devkit devkit-starter
uv run devkit add starter        # records the selection in .devkit/config.toml and synchronizes
```

Run `devkit` through `uv run` from the project's environment. A globally installed tool
(`uv tool install devkit`) runs in an isolated environment where `importlib.metadata` cannot see the content
packages of the project.

- **Upgrade**: `uv lock --upgrade-package <package>`, then `uv run devkit sync`.
- **Teardown**: `uv run devkit remove <bundle>`, then `uv remove --dev <package>`. Deselect first: a bundle still
  selected but no longer installed is a sync error.
- **Clean checkout**: `uv sync`, then `uv run devkit sync`, which rebuilds ignored managed and native files from the
  installed wheels.

## 3. Dependency Boundaries

Availability follows Python dependency resolution; deployment follows the consumer's `.devkit/config.toml`. When a
content package `packageB` depends on `packageA`:

- **`[project.dependencies]`** puts `packageA` in the wheel's `Requires-Dist`. A consumer that adds `packageB` gets
  `packageA` installed transitively, so its bundle becomes **available**, never selected: `devkit sync` lists it
  under `unselected` until the consumer runs `devkit add <bundle>`. Use this to layer bundles (a `team-backend`
  bundle on top of a `company-base` bundle).
- **`[dependency-groups].dev`** is omitted from the built wheel, so `packageA` is neither installed nor discovered
  downstream. Use this for tooling and tests local to the authoring repository.

There is no opt-out list for content packages, since opt-in is their default; `<bundle> = false` applies only to the
auto-selected built-in bundles ([selection model](sync-and-transactions.md#2-asset-selection-model)).
