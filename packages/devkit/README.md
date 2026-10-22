# devkit-agt

The devkit developer harness: repository rules, delivery workflows, commit gates, task worktrees, tracked generated
files, approval-bound integration and compact command output, mounted under the `devkit` command line of
[`devkit-dist`](../devkit-dist/README.md). The distribution name is `devkit-agt`; imports use the regular `devkit_agt` package. It
depends on `devkit-dist` and `devkit-advisory` at its own version (the three are released in lockstep), so installing
`devkit-agt` installs the whole CLI: every distribution command of `devkit-dist` plus `devkit rules`,
`devkit workflow`, `devkit gate`, `devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`. It
ships no console script of its own: its commands are `devkit.commands` plugins (`ARCH-05-3-command-plugins`).
Requires Python 3.12 or later; runtime dependencies are `devkit-core`, `click`, `pyyaml`, `tomlkit`, `devkit-dist` and
`devkit-advisory` (`devkit-dist` brings `devkit-cli`). The `search` extra selects `devkit-dist[search]` for dense/hybrid search. The `mcp` extra selects the same-version
`devkit-mcp` wheel for optional transport and forms. Domain integration imports only dependency-free core contracts.

## Install

No package index hosts the wheel; install it from Git, which brings `devkit-dist`, `devkit-core`, `devkit-cli` and
`devkit-advisory` from the same commit, or by URL from a GitHub Release with those wheels next to it (see the
[root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit sync            # deploys every installed bundle that declares auto_select (built in: devkit, advisory, harness)
uv run devkit add <bundle>    # selects any other bundle: built-in opt-in ones or another content package
```

A Git installation declares `devkit-agt` or `devkit-dist`, never both; a release-wheel installation of `devkit-agt`
names the `devkit-dist`, `devkit-core`, `devkit-cli` and `devkit-advisory` wheels next to it only because no index serves them. A tool installation names the owner of the executable
and adds this package: `uv tool install 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist' --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'`.

The bundles built into this package are `harness` (auto-selected: the guidance for rules, commit gates, workflows
and `devkit run`; its opt-in `run` preset adds the `AGENTS.md` pointer to `devkit run`) and `authoring` (opt-in: skill
and agent guide size rules with their playbooks, and the `agent-asset-writing` instruction,
[rules reference](../../docs/development/reference/rules.md#built-in-authoring-bundle)). `devkit-dist` builds in
`devkit`, `advisory` and `git-commits`
([gate reference](../../docs/development/reference/gate.md#built-in-git-commits-bundle)).

## Modules

| Module | Purpose | CLI | Reference |
| --- | --- | --- | --- |
| `devkit_agt.features.rules` | Repository rule engine with autofix, project policy and Git snapshot gates | `devkit rules` | [rules reference](../../docs/development/reference/rules.md) |
| `devkit_agt.features.workflow` | Data-driven delivery workflow engine | `devkit workflow` | [workflow reference](../../docs/development/reference/workflow.md) |
| `devkit_agt.features.gate` | Pluggable Git commit gates and extensible hook dispatchers installed by sync | `devkit gate` | [gate reference](../../docs/development/reference/gate.md) |
| `devkit_agt.features.worktree` | Activity branches (`plan-<slug>`, `dev-<slug>`) and one Git worktree per task: start (new, without a worktree, or attached to an existing branch), finish (integrate, remove, delete the branch), status, stale branches | `devkit worktree` | [worktree reference](../../docs/development/reference/worktree.md) |
| `devkit_agt.features.integration` | Approval-bound local/GitHub PR integration, readiness providers, verified landing and resumable cleanup | `devkit integration` and host MCP tools | [integration reference](../../docs/development/reference/integration.md) |
| `devkit_agt.features.generated` | Tracked generated files: settle their merge conflicts by regenerating, check and regenerate them | `devkit generated` | [generated reference](../../docs/development/reference/generated.md) |
| `devkit_agt.features.compact` | Verification commands with the full log on disk and a bounded view for agents | `devkit run` | [compact reference](../../docs/development/reference/compact.md) |
| `devkit_agt.bundles.harness`, `devkit_agt.bundles.authoring` | Data-only areas of the built-in `harness` and `authoring` bundles | none | [distribution reference](../../docs/development/reference/distribution.md) |

Each wheel owns a regular package: `devkit_agt` for the harness, `devkit_dist` for distribution and `devkit_core` for shared primitives. `devkit.advisory` remains the advisory library's public namespace.

## Package structure

`features/<feature>/` owns each harness capability. Its `cli` or `mcp` adapter exposes application operations in
`usecases/` through concrete `devkit_core.base.usecase.BaseUseCase` implementations with typed `execute` methods.
Internal helpers remain functions. Constructors only wire dependencies; operations over a shared `Workspace` or
`IntegrationService` retain that engine instance and its caches, authority records and locks. The base introduces
no approval hooks, mandatory DTOs or service/repository inheritance.
`services/` contains reusable domain logic, `repositories/` reads and writes configuration, records,
Git state or provider data, and `models/` defines contracts, values and errors. Layers exist only when the feature
has code for them. Workflow definition parsing and layout calculations stay in models; the definition and layout
repositories own definition file loading and existing unit discovery. Feature `__init__.py` files provide explicit public library facades. The package has no `core/`;
shared low-level primitives live in `devkit_core`. Package-level `base/` and `utils/` may be introduced when needed.

The `bundles/authoring/` and `bundles/harness/` resource packages retain their `bundle/` content. They load without
importing feature implementations; authoring rule files use the public harness rule API when loaded as plugins.

The repository `devkit-dev` architecture rule checks layering; package tests verify namespace, entry points and bundle isolation. Transports depend on use cases, services depend on repositories
and models, and feature dependencies remain explicit. `compact` and `worktree` are independent harness features;
`rules` and `generated` use `compact`; `workflow` uses `rules`; `gate` uses `rules` and `compact`; `integration` uses
`worktree` and distribution host contracts. The rule context currently constructs its default workspace cache; that exact repository edge is documented in the repository architecture rule.

The shared CLI conventions (`-w/--workspace-root`, `--format`, exit codes) and the documentation index are in
`ARCH-01-introduction-and-goals`.

## Tests

`tests/unit/` checks isolated parsing, models and policies; `tests/integration/` exercises real files, Git,
command wiring and bundle deployment. Both follow `features/<feature>/` for feature-owned tests; bundle tests
live under `integration/bundles/`, and package metadata and repository tooling checks under
`integration/package/`. Shared fixtures and helpers live in `tests/support/testsupport/`. Rules keep their
shipped tests beside each rule. Installed-wheel CLI and MCP end-to-end scenarios run in the repository smoke suite.
