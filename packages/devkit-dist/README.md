# devkit-dist

Agent asset distribution in one Python package with the `devkit` command line: bundles, native agent projections,
transactional sync and the installation receipt, context loading, playbooks and native host hooks. The distribution
name is `devkit-dist`; imports are under `devkit_dist`. It owns the sole `devkit` console script, the `.devkit/config.toml` schema and the receipt format.
Requires Python 3.12 or later; runtime dependencies are `click`, `jinja2`, `pyyaml`, `tomlkit`, `devkit-core`, `devkit-cli` (the
agent-first command-line boundary) and `devkit-advisory` (the `devkit.advisory` library), the devkit ones at the same version. The `search` extra (`devkit-dist[search]`) adds `numpy`, `tokenizers`
and the embedding model package for dense and hybrid search. Optional `devkit-mcp` owns the native stdio transport;
dist owns exact project registration and does not import the SDK.

`devkit-dist` alone deploys skills, subagents, instructions, playbooks, guidance, documents and host hooks; it runs
no repository rules, commit gates or delivery workflows. The developer harness (`devkit rules`, `devkit workflow`,
`devkit gate`, `devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`) is the
[`devkit-agt`](../devkit/README.md) package, which depends on `devkit-dist` at the same version and mounts its
commands under the same `devkit` executable. In a standalone installation a harness command name answers with
`HARNESS_COMMAND_UNAVAILABLE`, and deployed rule, gate or workflow assets with a `HARNESS_ENGINE_MISSING` warning; both
name the requirement to add.

## Install

No package index hosts the wheel; install it from Git (which brings `devkit-core`, `devkit-cli` and `devkit-advisory` from the same commit) or by
URL from a GitHub Release with the `devkit-core`, `devkit-cli` and `devkit-advisory` wheels next to it (see the
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
| `features/shared/` | Artifact models, local repository, execution use cases with adapter selection and CLI/MCP adapters |
| `features/search/` | Search errors and lexical/dense/hybrid search services |
| `bundles/{devkit,advisory,git_commits}/bundle/` | Built-in data bundles |
| `cli.py` | Lazy root command composition and installed command discovery |

Features contain only the layers their implementation uses. `cli` and `mcp` adapt invocations; `usecases`
coordinate operations through typed `BaseUseCase.execute` entrypoints; `services` implement feature behavior; `repositories` read or write external state;
`models` carry contracts and results. Models never depend on implementations or transports. Services and
repositories never depend on their feature's adapters or use cases. Shared project configuration and receipt
behavior belongs to the project feature. There is no package-level `core` or aggregate compatibility facade.

Distribution depends on project, search and host; host and shared depend on project. This wheel never imports
`devkit_agt`, including lazy module strings and entry points. Bundle rule source is data loaded from a synchronized
copy and may use the public rule API. The repository development bundle checks feature/layer direction; `tests/unit/architecture/test_layering.py` independently checks wheel ownership and data-only bundle boundaries, and `tests/integration/cli/test_cli_imports.py`
checks lazy command loading. `just test-dist` runs the package tests without the harness installed.

The independent [devkit-core](../devkit-core/README.md) package owns filesystem/Git/parsing/plugin primitives,
logging, extension dispatch and SDK-free MCP contracts. Its tests prohibit dependencies on this wheel. The output
contract of every command is implemented by [devkit-cli](../devkit-cli/README.md); `adapters/cli.py` binds it to the
`devkit` logger and the `DEVKIT_` environment prefix and adds the workspace options, and the root group is a
`devkit_cli.LazyGroup` extended with plugin lookup.

## Tests

`tests/unit/` covers isolated contracts, algorithms and static architecture checks. `tests/integration/`
covers real filesystem/Git state, command composition, installed plugins and connected feature behavior,
mirroring feature, adapter and bundle areas. Shared fixture helpers live in `tests/support/distsupport/`.
Built-wheel installation and public CLI/MCP end-to-end combinations are verified by the repository smoke suite.

Distribution CLI commands are grouped in `features/distribution/cli/`: bundle packaging, selection/sync,
configuration, context, playbooks and overrides each have a named module. `app.py` composes their command set;
`output.py` owns shared output formatting. `__init__.py` exposes the command set without implementing behavior.

Public selection operations in `features/distribution/usecases/commands.py` own selection replacement,
additive preset merging, persistence and installed-bundle discovery. Adapters supply parsed selections to
`sync_selection` or `add_selection`; they do not construct configuration callbacks. Project listing, status
and override operations keep discovered package resources open until their results have been collected.


Development approach is shared project policy: inspect `uv run devkit config show`. `[development] approach`
accepts `sdd` (the absent default) or explicit `adaptive-dev`; bundle/package selection does not change it.
Adaptive development keeps document and project checks without implicit SDD records. The common reader belongs to
devkit-dist; the `project` readiness provider belongs to devkit-agt, and SDD mutation/applicability consumers to
devkit-spec.
