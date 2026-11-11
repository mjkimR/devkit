# The project's own bundle

Converted assets live in an ordinary content package inside the repository, installed as a development dependency and selected in `.devkit/config.toml`; `devkit` plans, deploys and records it like any installed bundle.

## Find an existing bundle

1. Run `rg -n 'devkit\.bundles' -g 'pyproject.toml'` from the project root. A match under the repository (by convention `tools/<repo>-devkit/pyproject.toml`) names the package and its bundle.
2. The bundle source is the directory holding that package's `bundle.toml`; `uv run devkit list` shows the bundle and its selected presets.
3. If one exists, add the converted assets to it and skip the next section.

## Create the minimal bundle

`<repo>` is the repository name as a lowercase slug (`[a-z][a-z0-9-]*`) and `<repo_py>` the same name with `_` for `-`.

```text
tools/<repo>-devkit/
  pyproject.toml
  src/<repo_py>_devkit/
    __init__.py            # one docstring line; no code
    bundle/
      bundle.toml
      AGENTS.md            # the constitution: one line per converted role
      roles/<prefix>-<role>.md
```

```toml
# tools/<repo>-devkit/pyproject.toml
[project]
name = "<repo>-devkit"
version = "0.1.0"
description = "Agent assets owned by <repo>"
requires-python = ">=3.12"
dependencies = []

[project.entry-points."devkit.bundles"]
<repo> = "<repo_py>_devkit"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<repo_py>_devkit"]
```

```toml
# tools/<repo>-devkit/src/<repo_py>_devkit/bundle/bundle.toml
schema = 1
name = "<repo>"            # equals the entry point name; unique among installed bundles
version = "0.1.0"
default_preset = "all"

[[assets]]
id = "<prefix>-<role>"
kind = "document"
source = "roles/<prefix>-<role>.md"
```

```markdown
# <Repo> agent assets

- `<prefix>-<role>`: <use> with `swarm-<archetype>`; role path `.devkit/managed/<repo>/roles/<prefix>-<role>.md`. Unmet prerequisites: none.
```

## Install and select it

Run from the project root, in this order:

```bash
uv run devkit bundle validate tools/<repo>-devkit/src/<repo_py>_devkit/bundle
uv add --dev --editable ./tools/<repo>-devkit
uv run devkit add <repo>
uv run devkit get-context <repo>
```

1. `bundle validate` prints the bundle's name, version and asset count before anything is installed; fix a `BUNDLE_INVALID` report first.
2. `uv add` records the package as a development dependency; keep it out of `[project.dependencies]`, or a published wheel of the project would require it.
3. `devkit add` records the selection in `.devkit/config.toml` and synchronizes; the root `AGENTS.md` block then lists the bundle.
4. `get-context` returns the constitution; confirm it lists the converted role.
5. If the project has no `pyproject.toml`, stop and report that prerequisite; creating the project's packaging is outside this procedure.

## Keep it current

- After editing a file under `bundle/`, run `uv run devkit sync`; the editable install exposes the change and sync compares file hashes, so the version stays.
- Commit the bundle source together with the dependency declaration, the lock file, `.devkit/config.toml` and `.devkit/installation.json`, under the project's Git authority.
- `.devkit/managed/` is generated and ignored by Git; a fresh clone runs `uv sync` and `uv run devkit sync` before a managed role path exists.
- Change the project's own assets at their source; overrides are for bundles the project does not own.

## Completion

- `uv run devkit bundle validate <bundle source>` exits `0`.
- `uv run devkit status` exits `0` and its `selection.presets` names the bundle.
- `uv run devkit get-context <repo>` returns a constitution that lists every converted role.
