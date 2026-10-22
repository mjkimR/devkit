---
name: in-repo-bundle
description: Read before adding repository-specific rules, skills, playbooks, instructions, subagents, workflows or gates, or deciding where such assets belong.
---

# Repository-owned assets as an in-repository bundle

Assets that belong to one repository ship like shared ones: as a content
package inside the repository, installed as its development dependency and
discovered through the same entry point as any other bundle.

## Layout

```text
<repo>/
  pyproject.toml
  .devkit/config.toml                 # selects the bundle like any other
  tools/<repo>-devkit/
    pyproject.toml
    src/<repo>_devkit/
      __init__.py                     # empty docstring; no runtime code
      bundle/
        bundle.toml
        AGENTS.md                     # optional constitution
        rules/<slug>/rule.py          # one directory per rule: rule.py, guide.md, tests/
        skills/<slug>/SKILL.md
        playbooks/<slug>.md
        instructions/<slug>.md
```

```toml
# tools/<repo>-devkit/pyproject.toml
[project]
name = "<repo>-devkit"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.entry-points."devkit.bundles"]
<repo> = "<repo>_devkit"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<repo>_devkit"]
```

```toml
# tools/<repo>-devkit/src/<repo>_devkit/bundle/bundle.toml
schema = 1
name = "<repo>"
version = "0.1.0"
default_preset = "all"

[[assets]]
id = "<slug>"
kind = "rule"
source = "rules/<slug>"                # a directory; a file source is refused
```

The bundle name (used by `devkit add`, `get-context` and `.devkit/config.toml`)
must be unique among the installed bundles and equal the entry point name.
Validate before installing:

```bash
uv run devkit bundle validate tools/<repo>-devkit/src/<repo>_devkit/bundle
uv run devkit bundle plan tools/<repo>-devkit/src/<repo>_devkit/bundle
```

## Installation

In a uv workspace, add the package to the members and to the dev group next to
the devkit requirement the project already declares:

```toml
# pyproject.toml at the repository root
[tool.uv.workspace]
members = ["tools/*"]

[dependency-groups]
dev = ["devkit-dist", "<repo>-devkit"]

[tool.uv.sources]
devkit-dist = { git = "https://github.com/mjkimR/devkit.git", subdirectory = "packages/devkit-dist" }
"<repo>-devkit" = { workspace = true }
```

If the project uses the harness, or its bundle ships rule, gate or workflow
assets, declare `devkit-agt` instead (see the `harness` bundle's
`harness-assets` instruction). It brings `devkit-dist`, so a project
never declares both.

In a single project, depend on it by path:

```bash
uv add --dev --editable ./tools/<repo>-devkit
```

Then select and synchronize:

```bash
uv sync
uv run devkit add <repo>
```

As a development dependency, the bundle never reaches consumers of the
repository's own published package.

## Editing lifecycle

Edit sources under `tools/<repo>-devkit/src/<repo>_devkit/bundle/`, then run
`uv run devkit sync`. The editable install exposes the change at once and sync
compares file hashes, so the package version need not change.

Edit the repository's own bundle at its source, not through an override; overrides
are for bundles the repository does not own.

## Sharing later

Publish the package, or let other repositories depend on it with a Git URL
and `subdirectory`. From then on, bump the bundle `version` in `bundle.toml` so
consumers' receipts record what they run.
