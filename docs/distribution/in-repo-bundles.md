# In-Repository Bundles (Self-Consumed Content Packages)

**Status**: Architecture Decision & Usage Guide  
**Package**: `devkit`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Bundle Manifest Specification](manifest-spec.md)
- [Transitive Dependencies](transitive-dependencies.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Evaluation Lifecycle: Git Snapshot Gates](../rules/evaluation-lifecycle.md#6-git-snapshot-gates)

---

## 1. Problem

A repository often needs assets that belong only to itself: a governance rule that encodes a project convention, a skill that drives its own release script, a playbook for its on-call procedure. These assets must be versioned with the repository, must not be published to anyone else, and should still participate in everything `devkit` does for distributed assets: planning, hash-tracked projection into agent directories, receipt recording, rule discovery and Git snapshot gates.

## 2. Decision

**A repository ships its own assets as an ordinary content package that lives inside the repository and is installed as a development dependency of that same repository.** There is no separate "local" asset directory under `.devkit/` and no second loader for it.

The package is discovered, planned, synchronized and recorded exactly like a bundle installed from a wheel, because to `devkit` it *is* one: `importlib.metadata.entry_points(group="devkit.bundles")` does not distinguish between a wheel from a registry, a Git dependency, a `path` dependency or a workspace member.

### Why not a `.devkit/local/` directory?

A dedicated local directory was considered and rejected:

| Concern | `.devkit/local/` directory | In-repository bundle |
| --- | --- | --- |
| Discovery, planning, projection | A second code path next to installed bundles | The existing entry-point path |
| Receipt, hashes, drift detection | Needs its own ownership rules and receipt entries | Recorded like any bundle |
| Rule loading and snapshot gates | `devkit rules` needs a second discovery source | Receipt-driven loading already works |
| Asset kinds beyond rules | Each kind needs explicit local support | Every kind in `bundle.toml` works unchanged |
| Overrides vs. additions | Blurs the line with `.devkit/overrides/` | Overrides stay for upstream edits, bundles for additions |
| Setup cost | None | A `pyproject.toml`, an entry point and a `bundle.toml` |

The only cost of the chosen approach is the packaging boilerplate in the last row. It is a few lines and is paid once per repository.

## 3. Layout

The package can live anywhere in the repository. By convention, put it under `tools/` and name it after the repository:

```text
my-repo/
  pyproject.toml                      # the repository's own project
  .devkit/
    config.toml                       # selects the in-repo bundle like any other
    installation.json                 # receipt (Git-tracked)
    managed/                          # Git-ignored projections, written by devkit sync
  tools/
    my-repo-devkit/
      pyproject.toml
      src/
        my_repo_devkit/
          __init__.py                 # empty; no runtime side effects
          bundle/
            bundle.toml
            rules/
              no_todo.py
            skills/
              release/
                SKILL.md
            playbooks/
              on-call.md
```

```toml
# tools/my-repo-devkit/pyproject.toml
[project]
name = "my-repo-devkit"
version = "0.1.0"
description = "Agent assets owned by my-repo"
requires-python = ">=3.12"
dependencies = []

[project.entry-points."devkit.bundles"]
my-repo = "my_repo_devkit"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_repo_devkit"]
```

```toml
# tools/my-repo-devkit/src/my_repo_devkit/bundle/bundle.toml
schema = 1
name = "my-repo"
version = "0.1.0"
default_preset = "all"

[[assets]]
id = "conventions"
kind = "rule"
source = "rules"

[[assets]]
id = "release"
kind = "skill"
source = "skills/release"

[[assets]]
id = "on-call"
kind = "playbook"
source = "playbooks/on-call.md"
```

The manifest follows the [Bundle Manifest Specification](manifest-spec.md) without exception. `devkit bundle validate tools/my-repo-devkit/src/my_repo_devkit/bundle` and `devkit bundle plan <that path>` work on it before it is ever installed.

## 4. Installation

### 4.1 Repository that is a uv workspace

Add the package directory to the workspace members and depend on it from the development group. `uv` records the member as a workspace source:

```toml
# pyproject.toml (repository root)
[tool.uv.workspace]
members = ["packages/*", "tools/*"]

[dependency-groups]
dev = ["devkit", "my-repo-devkit"]

[tool.uv.sources]
my-repo-devkit = { workspace = true }
```

```bash
uv sync
uv run devkit add my-repo        # records [presets] my-repo = "all" in .devkit/config.toml
uv run devkit sync
```

### 4.2 Repository that is a single project

Depend on the package by path, as an editable development dependency:

```bash
uv add --dev --editable ./tools/my-repo-devkit
```

```toml
# pyproject.toml, written by uv add
[dependency-groups]
dev = ["devkit", "my-repo-devkit"]

[tool.uv.sources]
my-repo-devkit = { path = "tools/my-repo-devkit", editable = true }
```

Then `uv run devkit add my-repo` and `uv run devkit sync` as above.

### 4.3 Repository without Python code

Using `devkit` at all requires a `pyproject.toml` with `devkit` as a development dependency, so the in-repository bundle adds no new requirement. The root project needs no build system; a `[project]` table with a name plus `[dependency-groups]` and `[tool.uv.sources]` is enough.

## 5. Dependency Boundary

The bundle package is declared in `[dependency-groups].dev`, never in `[project.dependencies]`. Development groups are not written to a built wheel's `Requires-Dist`, so if the repository is itself published as a package, its consumers never receive the bundle, its rules or its entry point. This is the boundary described in [Transitive Dependencies, section 2](transitive-dependencies.md#2-transitive-bundle-distribution-and-dependency-boundaries): dependency groups isolate tooling to the authoring repository.

Conversely, when a repository wants to *share* an in-repository bundle with other repositories, nothing changes in the bundle: publish the package, or let consumers depend on it with a Git URL and `subdirectory`, and they install it like any other content wheel.

## 6. Editing Lifecycle

1. Edit the asset sources under `tools/my-repo-devkit/src/.../bundle/`.
2. Run `uv run devkit sync`. The editable install exposes the new content immediately, and `sync` replans from the installed resources on every run and compares file hashes against the receipt, so the package version does not need to change for edits to be projected.
3. Commit the source change together with the updated `.devkit/installation.json`.

Never edit `.devkit/managed/<bundle>/` directly: `devkit sync` detects a modified managed file as a conflict and halts, exactly as it would for an upstream bundle. `.devkit/overrides/` exists to replace files of bundles the repository does not own; for an in-repository bundle, edit the source instead.

The bundle `version` in `bundle.toml` is still meaningful: bump it when another repository consumes the bundle, so their receipts record which version they are on.

## 7. Governance Rules and Snapshot Gates

Rules in an in-repository bundle are deployed to `.devkit/managed/my-repo/rules/` and listed in the receipt under their asset's `paths`. `devkit rules check` loads them from there with no flags. They are configured in `[rules]` of `.devkit/config.toml` like any other rule.

Git snapshot gates (`devkit rules check --staged`, `--ci`) evaluate a materialized Git tree, and `.devkit/managed/` is Git-ignored, so the managed rule copies are not in that tree. The gate reads such a file from the working tree only when its SHA-256 matches the `files` entry in the receipt committed to the snapshot. Consequences for an in-repository bundle:

- After editing a rule, run `devkit sync` and stage the updated receipt alongside the rule source. A staged rule source with a stale receipt fails the gate: the working-tree managed copy no longer matches the receipt's hash, and the advisory's `[FIX]` says to run `devkit sync`.
- A fresh clone must run `uv sync` and `uv run devkit sync` before the gate can run; otherwise the gate reports the managed rule as missing. This is identical to upstream bundles.
- The committed receipt pins exactly which rule code a gate executed, which is the property the snapshot gates exist to provide.

### Rule ID precedence

`devkit rules` loads built-in rules first, then rule assets in receipt order, then `--rules-dir`. A rule with the same ID as an earlier one replaces it. An in-repository bundle can therefore deliberately shadow an upstream rule by reusing its ID, but the order between bundles follows bundle name sorting in the receipt, not a declared priority. Prefer unique IDs prefixed with the repository name (for example `RULE-myrepo-no-todo`) unless shadowing is the intent.

## 8. Comparison of Project-Specific Mechanisms

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of a distributed rule | `[rules]` in `.devkit/config.toml` |
| Replace the content of one upstream asset file | `.devkit/overrides/<bundle>/...` with `devkit override create` |
| Add rules, skills, playbooks, subagents, workflows or gates that belong to this repository | In-repository bundle (this document) |
| Try an unfinished rule without recording it anywhere | `devkit rules check --rules-dir <dir>`; with `--staged`/`--ci` a directory inside the repository is read from the snapshot, one outside it or untracked is refused, and the commit gate's staged-rules gate never takes it |

## 9. Delivery to Consumers

This document is the developer-facing specification. The consumer-facing version is the `in-repo-bundle` instruction of the `devkit` guide bundle shipped inside `devkit` (`src/devkit/distribution/guide/bundle/`), delivered to agents through `devkit get-context devkit`. Keep the two in step when the mechanism changes.

## 10. Open Items

- **Scaffolding**: a `devkit bundle init <path>` command that writes the `pyproject.toml`, `__init__.py` and a minimal `bundle.toml` would remove the remaining setup cost. Not implemented.
- **Explicit rule precedence**: if shadowing upstream rules from an in-repository bundle becomes common, a declared load order would replace the implicit bundle name ordering. Not planned until a concrete need appears.
