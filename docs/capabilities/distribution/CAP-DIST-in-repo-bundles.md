---
id: CAP-DIST-in-repo-bundles
title: "In-Repository Bundles"
summary: "Repository-owned assets packaged and consumed locally without external distribution, with their installation next to the declared devkit requirement and their rules in Git snapshot gates."
area: distribution
status: active
created_at: 2026-10-17
---

# [CAP-DIST-in-repo-bundles] In-Repository Bundles

A repository's own assets (a rule encoding a project convention, a skill driving its release script, an on-call
playbook) must be versioned with it, never published, and still get everything devkit does for distributed assets:
planning, hash-tracked projection, receipt recording, rule discovery and Git snapshot gates. The consumer-facing
version of this document is the `in-repo-bundle` instruction of the [`devkit` guide bundle](../../development/reference/distribution.md#4-bundles-shipped-with-devkit);
keep the two in step. The bundle setup is mirrored by the `devkit` bundle's `in-repo-bundle` instruction (shipped by
`devkit-dist`); rule discovery, rule tests and Git snapshot gates by the `harness` bundle's `harness-assets`
instruction (shipped by `devkit-agt`, which runs the rules).

## 1. Decision

**A repository ships its own assets as an ordinary content package inside the repository, installed as a
development dependency of that same repository.** There is no local asset directory under `.devkit/` and no second
loader: `importlib.metadata.entry_points(group="devkit.bundles")` does not distinguish a registry wheel, a Git or
`path` dependency, or a workspace member.

A `.devkit/local/` directory was rejected. It would need a second discovery and planning path, its own receipt and
ownership rules, a second rule source for `devkit rules`, explicit support per asset kind, and it would blur the line
with `.devkit/overrides/` (overrides change upstream files; bundles add assets). The in-repository bundle costs only a
`pyproject.toml`, an entry point and a `bundle.toml`, paid once.

## 2. Layout

By convention the package lives under `tools/` and is named after the repository:

```text
my-repo/
  pyproject.toml
  .devkit/config.toml                 # selects the in-repo bundle like any other
  tools/my-repo-devkit/
    pyproject.toml
    src/my_repo_devkit/
      __init__.py                     # empty; no runtime side effects
      bundle/
        bundle.toml
        rules/no_todo/rule.py         # one plugin package per rule: rule.py, guide.md, tests/
        skills/release/SKILL.md
        playbooks/on-call.md
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
id = "no-todo"
kind = "rule"
source = "rules/no_todo"

[[assets]]
id = "release"
kind = "skill"
source = "skills/release"

[[assets]]
id = "on-call"
kind = "playbook"
source = "playbooks/on-call.md"
```

The entry point name (`my-repo`) is the bundle name
(`CAP-DIST-content-packages`).
The manifest follows the `CAP-DIST-manifest-spec` without exception; `devkit bundle validate` and
`devkit bundle plan` work on `tools/my-repo-devkit/src/my_repo_devkit/bundle` before it is installed.

## 3. Installation

In a **uv workspace**, add the package to the members and to the dev group next to the devkit requirement the
project already declares: `devkit-agt` when the project uses the harness (and always when the bundle ships rules,
gates or workflows, which only `devkit-agt` runs), otherwise `devkit-dist`. `devkit-agt` depends on `devkit-dist` at
the same version, so a project never declares both (`ADR-package-split-and-namespaces`):

```toml
# pyproject.toml (repository root)
[tool.uv.workspace]
members = ["packages/*", "tools/*"]

[dependency-groups]
dev = ["devkit-agt", "my-repo-devkit"]

[tool.uv.sources]
devkit-agt = { git = "https://github.com/mjkimR/devkit.git", subdirectory = "packages/devkit" }
my-repo-devkit = { workspace = true }
```

In a **single project**, `uv add --dev --editable ./tools/my-repo-devkit` writes the same dev dependency with
`my-repo-devkit = { path = "tools/my-repo-devkit", editable = true }` as its source. A repository **without Python
code** already has a `pyproject.toml` for `devkit`; its root project needs no build system, only `[project]` with a
name, `[dependency-groups]` and `[tool.uv.sources]`.

Then:

```bash
uv sync
uv run devkit add my-repo        # records [presets] my-repo = "all" and synchronizes
```

The package belongs in `[dependency-groups].dev`, never `[project.dependencies]`: dependency groups are not written
to a built wheel, so if the repository is itself published, its consumers never receive the bundle, its rules or its
entry point (`CAP-DIST-content-packages`). To share the bundle later,
publish the package or let other repositories depend on it with a Git URL and `subdirectory`.

## 4. Editing Lifecycle

1. Edit the sources under `tools/my-repo-devkit/src/.../bundle/`.
2. Run `uv run devkit sync`. The editable install exposes the change at once and `sync` compares hashes against the
   receipt on every run, so the package version need not change.
3. Commit the source change with the updated `.devkit/installation.json`.

Never edit `.devkit/managed/<bundle>/`: a modified managed file stops the sync as for any bundle. Overrides are for
bundles the repository does not own. Bump the bundle `version` once another repository consumes the bundle, so
their receipts record which version they run.

## 5. Rules and Snapshot Gates

The bundle's rules deploy to `.devkit/managed/my-repo/rules/`, are listed under their asset's `paths`, load in
`devkit rules check` without flags and are configured in `[rules]` like any rule. They need `devkit-agt`: in an
installation with `devkit-dist` alone they are deployed with a `HARNESS_ENGINE_MISSING` warning
(`CAP-DIST-sync-and-transactions`).

Snapshot gates (`devkit rules check --staged`, `--ci`) evaluate a Git tree whose receipt pins the Git-ignored managed
copies: a materialized tree lacks them, and the gate reads such a file from the working tree only when its SHA-256
matches the `files` entry of the receipt committed to the snapshot; a staged snapshot evaluated in place checks the
same hash
(`CAP-GOV-evaluation-lifecycle`). Hence:

- After editing a rule, run `devkit sync` and stage the receipt with the rule source; a stale receipt fails the gate,
  whose `[FIX]` says to run `devkit sync`.
- A fresh clone runs `uv sync` and `uv run devkit sync --locked` before the gate can run; otherwise it reports the
  managed rule as missing, as for upstream bundles. Run the same in CI: it fails (`RECEIPT_STALE`) when a bundle
  source was committed without the receipt it produces.
- The committed receipt pins exactly which rule code a gate executed.

`devkit rules` loads built-in rules, then rule assets in receipt order (bundle name order), then `--rules-dir`; a
rule with an earlier rule's ID replaces it. An in-repository bundle can shadow an upstream rule that way, but the
order between bundles is not a declared priority, so prefer IDs prefixed with the repository name
(`RULE-myrepo-no-todo`) unless shadowing is the intent.

## 6. Project-Specific Mechanisms

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of a distributed rule | `[rules]` in `.devkit/config.toml` |
| Replace the content of one upstream asset file | `devkit override create` (`.devkit/overrides/<bundle>/...`) |
| Add rules, skills, playbooks, subagents, workflows or gates that belong to this repository | In-repository bundle |
| Try an unfinished rule without recording it | `devkit rules check --rules-dir <dir>`; with `--staged`/`--ci` a directory inside the repository is read from the snapshot, one outside it or untracked is refused, and the commit gate's staged-rules gate never takes it |

## 7. Open Items

- **Scaffolding**: a `bundle init <path>` subcommand writing the `pyproject.toml`, `__init__.py` and a minimal
  `bundle.toml`. Not implemented.
- **Explicit rule precedence**: a declared load order replacing bundle name ordering, if shadowing upstream rules
  becomes common. Not planned until a concrete need appears.
