---
name: in-repo-bundle
description: Read before adding repository-specific rules, skills, playbooks, instructions, subagents, workflows or gates, or when asked where such assets belong. Explains shipping a repository's own assets as a devkit bundle installed from the same repository, its layout, installation, edit lifecycle and how its rules reach Git snapshot gates.
---

# Repository-owned assets as an in-repository bundle

Assets that belong to one repository are shipped the same way as shared ones:
as a content package that lives inside the repository and is installed as a
development dependency of that repository. devkit discovers it through the
same entry point as any other bundle. There is no special local directory under
`.devkit/`, and nothing in the repository's own guidance files needs to list
the assets by hand.

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
        rules/<slug>.py
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

[project.entry-points."devkit_distribution.bundles"]
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
id = "conventions"
kind = "rule"
source = "rules"
```

The bundle name is the identifier used in `devkit add`, `get-context` and
`.devkit/config.toml`; it must be unique among the bundles the repository
installs. Validate before installing:

```bash
uv run devkit bundle validate tools/<repo>-devkit/src/<repo>_devkit/bundle
uv run devkit plan tools/<repo>-devkit/src/<repo>_devkit/bundle
```

## Installation

In a uv workspace, add the package to the members and the dev group:

```toml
# pyproject.toml at the repository root
[tool.uv.workspace]
members = ["tools/*"]

[dependency-groups]
dev = ["devkit-distribution", "<repo>-devkit"]

[tool.uv.sources]
"<repo>-devkit" = { workspace = true }
```

In a single project, depend on it by path:

```bash
uv add --dev --editable ./tools/<repo>-devkit
```

Then select and synchronize:

```bash
uv sync
uv run devkit add <repo>
```

The package is a development dependency, so if the repository is itself
published as a package its consumers never receive the bundle, its rules or
its entry point.

## Editing lifecycle

1. Edit sources under `tools/<repo>-devkit/src/<repo>_devkit/bundle/`.
2. Run `uv run devkit sync`. The editable install exposes the change at once,
   and `sync` compares file hashes on every run, so the package version does
   not need to change.
3. Commit the source change together with the updated
   `.devkit/installation.json`.

Never edit `.devkit/managed/<repo>/`; `sync` treats a modified managed file as
a conflict. `.devkit/overrides/` is for files of bundles the repository does
not own. For the repository's own bundle, edit the source.

## Rules in Git snapshot gates

`agent-rules check --staged` and `--ci` evaluate a Git tree. The managed rule
copies are Git-ignored, so the gate reads them from the working tree only when
their SHA-256 matches the committed receipt. Therefore:

- Stage the updated receipt with every rule change; a stale receipt fails the
  gate and names `devkit sync` as the fix.
- A fresh clone runs `uv sync` and `uv run devkit sync` before gates can pass.
- Prefer rule ids prefixed with the repository name
  (`RULE-<repo>-<topic>`) unless the intent is to shadow an upstream rule.

## When to use what

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of an installed rule | `[rules]` in `.devkit/config.toml` |
| Replace one file an upstream bundle ships | `devkit override create <bundle>:<asset>` |
| Add assets that belong to this repository | In-repository bundle |
| Try an unfinished rule without recording it | `agent-rules check --rules-dir <dir>` (invisible to snapshot gates) |

## Sharing later

To share the bundle with other repositories, publish the package or let them
depend on it with a Git URL and `subdirectory`. Bump the bundle `version` in
`bundle.toml` from then on so consumers' receipts record what they run.
