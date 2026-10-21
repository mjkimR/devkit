# devkit-dist

Agent asset distribution in one Python package with the `devkit` command line: bundles, native agent projections,
transactional sync and the installation receipt, context loading, playbooks and native host hooks. The distribution
name is `devkit-dist`; imports are under `devkit_dist`. It owns the sole `devkit` console script, the `.devkit/config.toml` schema and the receipt format.
Requires Python 3.12 or later; runtime dependencies are `click`, `jinja2`, `pyyaml`, `tomlkit`, `devkit-core` and `devkit-advisory`
(the `devkit.advisory` library, same version). The `search` extra (`devkit-dist[search]`) adds `numpy`, `tokenizers`
and the embedding model package for dense and hybrid search. Optional `devkit-mcp` owns native stdio and forms;
dist owns exact project registration and does not import the SDK.

`devkit-dist` alone deploys skills, subagents, instructions, playbooks, guidance, documents and host hooks; it runs
no repository rules, commit gates or delivery workflows. The developer harness (`devkit rules`, `devkit workflow`,
`devkit gate`, `devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`) is the
[`devkit-agt`](../devkit/README.md) package, which depends on `devkit-dist` at the same version and mounts its
commands under the same `devkit` executable. In a standalone installation a harness command name answers with
`HARNESS_COMMAND_UNAVAILABLE`, and deployed rule, gate or workflow assets with a `HARNESS_ENGINE_MISSING` warning; both
name the requirement to add.

## Install

No package index hosts the wheel; install it from Git (which brings `devkit-core` and `devkit-advisory` from the same commit) or by URL
from a GitHub Release with the `devkit-core` and `devkit-advisory` wheels next to it (see the
[root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
uv run devkit sync            # deploys every installed bundle that declares auto_select (built in: devkit, advisory)
uv run devkit add <bundle>    # selects any other bundle: the built-in git-commits or another content package
```

A project that uses the harness declares `devkit-agt` instead, never both (`devkit-agt` brings `devkit-dist` from the
same commit; only a release-wheel installation names the `devkit-dist` wheel next to it, since no index serves it). A tool
installation names the script owner and adds the harness:
`uv tool install 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist' --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'`.

## Package structure

`devkit_dist` is an independently owned regular package. `devkit.advisory` remains the public advisory library
in its own distribution. No application modules share that namespace.

| Area | Responsibility |
| --- | --- |
| `base/errors.py` | Error contracts shared by distribution features and command loading |
| `adapters/` | Shared CLI output boundaries and command workspace bootstrap |
| `features/project/models/` | Immutable receipt records and configuration template contracts |
| `features/project/repositories/` | Project discovery, configuration/receipt readers and live execution-context guards |
| `features/project/services/` | Configuration template rendering and presentation language |
| `features/project/usecases/` | Workspace/configuration queries and invocation revalidation for transport adapters |
| `features/distribution/` | Bundle validation/packaging, installation synchronization, context, playbooks and overrides |
| `features/host/` | Hook models, host adapters, configuration services, dispatch and MCP registration use cases |
| `features/shared/` | Artifact models, local repository, adapter selection use case and CLI/MCP adapters |
| `features/search/` | Search errors and lexical/dense/hybrid search services |
| `bundles/{devkit,advisory,git_commits}/bundle/` | Built-in data bundles |
| `cli.py` | Lazy root command composition and installed command discovery |

Features contain only the layers their implementation uses. `cli` and `mcp` adapt invocations; `usecases`
coordinate operations; `services` implement feature behavior; `repositories` read or write external state;
`models` carry contracts and results. Models never depend on implementations or transports. Services and
repositories never depend on their feature's adapters or use cases. Shared project configuration and receipt
behavior belongs to the project feature. There is no package-level `core` or aggregate compatibility facade.

Distribution depends on project, search and host; host and shared depend on project. This wheel never imports
`devkit_agt`, including lazy module strings and entry points. Bundle rule source is data loaded from a synchronized
copy and may use the public rule API. The repository development bundle checks feature/layer direction; `tests/test_layering.py` independently checks wheel ownership and data-only bundle boundaries, and `tests/test_cli_imports.py`
checks lazy command loading. `just test-dist` runs the package tests without the harness installed.

The independent [devkit-core](../devkit-core/README.md) package owns filesystem/Git/parsing/plugin primitives,
logging, extension dispatch and SDK-free MCP contracts. Its tests prohibit dependencies on this wheel.
