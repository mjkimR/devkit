---
name: in-repo-bundle
description: Read before adding repository-specific rules, skills, playbooks, instructions, subagents, workflows or gates, or deciding where such assets belong.
---

# Repository-owned assets as an in-repository bundle

Ship assets that belong to one repository as a content package inside it,
installed as a development dependency:

```text
tools/<repo>-devkit/
  pyproject.toml
  src/<repo>_devkit/
    __init__.py                     # empty docstring; no runtime code
    bundle/
      bundle.toml
      AGENTS.md                     # optional constitution
      rules/<slug>/                 # rule.py, guide.md, tests/
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
# bundle/bundle.toml
schema = 1
name = "<repo>"          # unique among installed bundles; equals the entry point name
version = "0.1.0"
default_preset = "all"

[[assets]]
id = "<slug>"
kind = "rule"
source = "rules/<slug>"
```

In a uv workspace, add the package to the dev group next to the devkit
requirement. Declare `devkit-agt` instead of `devkit-dist` when the bundle ships
rule, gate or workflow assets; it brings `devkit-dist`.

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

In a single project, run `uv add --dev --editable ./tools/<repo>-devkit` instead.
Then run `uv sync` and `uv run devkit add <repo>`.

- After editing a source under `bundle/`, run `uv run devkit sync`; the version
  stays, because sync compares file hashes.
- Change the repository's own assets at their source, not through an override.
- Once other repositories depend on the package, bump `version` in `bundle.toml`
  with every change.

Done when `uv run devkit bundle validate tools/<repo>-devkit/src/<repo>_devkit/bundle`
passes and `uv run devkit status` exits `0`.
