# devkit

Agent asset distribution, repository rules, delivery workflows and commit gates
in one Python package with one CLI (`devkit`). Requires Python 3.12 or later;
runtime dependencies are `click`, `pyyaml` and `tomlkit`.

## Install

No package index hosts the wheel yet; install a built wheel by path (see the
[root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev /path/to/devkit-0.1.0-py3-none-any.whl
uv run devkit sync            # deploys the built-in bundles (devkit, advisory)
uv run devkit add <bundle>    # selects a bundle from another installed content package
```

Every command takes `-w/--workspace-root`; the default is the enclosing project
root (the nearest directory with `.devkit/`, else the Git top level, else the
current directory); `devkit gate` always acts on the Git work tree's top level.
Architecture and the documentation index:
[Architecture Overview](../../docs/architecture/overview.md).

## Modules

| Module | Purpose | CLI | Reference |
| --- | --- | --- | --- |
| `devkit.core` | Shared foundation: frontmatter grammar, installation receipt, safe paths, Git runner, plugin loading, project discovery | none | [docs/core](../../docs/core/reference.md) |
| `devkit.advisory` | Agent Advisory Protocol errors, plus the built-in `advisory` guide bundle | none | [docs/advisory](../../docs/advisory/reference.md) |
| `devkit.rules` | Repository rule engine with autofix, project policy and Git snapshot gates | `devkit rules` | [docs/rules](../../docs/rules/reference.md) |
| `devkit.workflow` | Data-driven delivery workflow engine | `devkit workflow` | [docs/workflow](../../docs/workflow/reference.md) |
| `devkit.gate` | Pluggable Git commit gates and managed hook wrappers | `devkit gate` | [docs/gate](../../docs/gate/reference.md) |
| `devkit.distribution` | Bundle packaging and transactional synchronization, plus the built-in `devkit` guide bundle | `devkit sync`, `add`, `remove`, `list`, `status`, ... | [docs/distribution](../../docs/distribution/reference.md) |

Layering: `advisory` imports no other module; `core` may import `advisory`;
`rules` may import `core` and `advisory`; `workflow` and `gate` may import
`core`, `advisory` and `rules`; `distribution` may import only `core` and
`advisory`. `devkit.cli` assembles the command line. A test enforces this.

Bundles shipped inside this package (`devkit`, `advisory`) are selected with
their default preset unless `.devkit/config.toml` opts out with
`[presets] <bundle> = false`. Bundles from other packages are deployed only
after `devkit add`.
