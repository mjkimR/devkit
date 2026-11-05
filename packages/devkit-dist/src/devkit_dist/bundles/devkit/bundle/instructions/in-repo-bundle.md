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

## Snapshot a shared private content provider

1. Obtain an authorized local content-package checkout.
2. Copy its complete supported provider with a distinct local package name:

       uv run devkit bundle snapshot /checkout/team-assets --to tools/team-assets-copy --package team-assets-copy

3. Follow the returned provider-removal and editable-install commands; remove the original provider from every
   dependency group and resolve transitive requirements that still install it.
4. Run normal selection and sync, then commit the local package, provenance and deliberate dependency changes.

The source must use static metadata, ordinary Hatch src resources and inert initializers with no project runtime
dependencies or other entry-point groups. Self-contained bundle rules/gates/helpers may import standard-library
or documented devkit APIs and copied relative helpers. Unsupported imports, dynamic execution/import syntax and
external declarative handlers refuse before writes. Keep required devkit/harness/build tools separately installed.
The wrapper preserves every bundle of the provider because duplicate bundle names remain a discovery error.

Keep consumer adaptations in project overrides. Do not edit generated snapshot sources. The local wrapper version
stays 0.0.0; source package/bundle versions, content digests and the adoption commit identify the snapshot.

When upstream sources change, preview and inspect the returned file changes:

    uv run devkit bundle refresh tools/team-assets-copy --source /checkout/team-assets --check
    uv run devkit bundle refresh tools/team-assets-copy --source /checkout/team-assets --expect <current-digest> --candidate <reviewed-candidate-digest>

Apply requires both preview digests and refuses authored local changes. Unchanged sources write nothing.
Follow returned reinstall commands when packaging metadata changes and explicitly deselect removed bundles before
normal sync. Refresh changes only the snapshot directory; installation, config, overrides, receipt and Git remain
separate steps. Done when normal sync succeeds and a fresh consumer can install the local provider without fetching
its private origin, given the required runtime/build dependencies.
