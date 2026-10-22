---
name: in-repo-bundle
description: Read before adding repository-specific rules, skills, playbooks, instructions, subagents, workflows or gates, or deciding where such assets belong.
---

# Repository-owned assets as an in-repository bundle

Ship assets that belong to one repository as a content package inside it,
installed as a development dependency and discovered through the
`devkit.bundles` entry point like any other bundle.

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

Give the bundle a name that is unique among the installed bundles and equal to
the entry point name; `devkit add`, `get-context` and `.devkit/config.toml` use
it. Validate before installing, fix what is reported and rerun until both pass:

```bash
uv run devkit bundle validate tools/<repo>-devkit/src/<repo>_devkit/bundle
uv run devkit bundle plan tools/<repo>-devkit/src/<repo>_devkit/bundle
```

## Installation

Install the package as a development dependency, so it never reaches consumers
of the repository's own published package. In a uv workspace, add it to the
members and to the dev group next to the devkit requirement the project already
declares:

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

If the bundle ships rule, gate or workflow assets, or the project runs their
engines, declare `devkit-agt` instead of `devkit-dist`. It brings `devkit-dist`,
so a project never declares both.

In a single project, depend on it by path:

```bash
uv add --dev --editable ./tools/<repo>-devkit
```

Then select and synchronize:

```bash
uv sync
uv run devkit add <repo>
```

## Editing

- Edit sources under `tools/<repo>-devkit/src/<repo>_devkit/bundle/`, then run
  `uv run devkit sync`. Leave the package version unchanged, because the
  editable install exposes the change and sync compares file hashes.
- Change the repository's own bundle at its source, not through an override;
  overrides are for bundles the repository does not own.
- Once other repositories depend on the package (published, or by Git URL with
  `subdirectory`), bump `version` in `bundle.toml` with every change, so their
  receipts record what they run.

## Completion

`uv run devkit bundle validate` passes and `uv run devkit status` exits `0`.
