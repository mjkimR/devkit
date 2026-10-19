# devkit-agt

The devkit developer harness: repository rules, delivery workflows, commit gates, task worktrees, tracked generated
files, approval-bound integration and compact command output, mounted under the `devkit` command line of
[`devkit-dist`](../devkit-dist/README.md). The distribution name is `devkit-agt`; imports remain `devkit.*`. It
depends on `devkit-dist` and `devkit-advisory` at its own version (the three are released in lockstep), so installing
`devkit-agt` installs the whole CLI: every distribution command of `devkit-dist` plus `devkit rules`,
`devkit workflow`, `devkit gate`, `devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`. It
ships no console script of its own: its commands are `devkit.commands` plugins (`ARCH-05-3-command-plugins`).
Requires Python 3.12 or later; runtime dependencies are `click`, `pyyaml`, `tomlkit`, `devkit-dist` and
`devkit-advisory`. The `search` and `mcp` extras (`devkit-agt[search]`, `devkit-agt[mcp]`) are those of
`devkit-dist`: dense and hybrid search with the embedding model, and the SDK for native stdio services and
confirmation.

## Install

No package index hosts the wheel; install it from Git, which brings `devkit-dist` and `devkit-advisory` from the same
commit, or by URL from a GitHub Release with the `devkit-dist` and `devkit-advisory` wheels next to it (see the
[root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit sync            # deploys every installed bundle that declares auto_select (built in: devkit, advisory, harness)
uv run devkit add <bundle>    # selects any other bundle: built-in opt-in ones or another content package
```

A Git installation declares `devkit-agt` or `devkit-dist`, never both; a release-wheel installation of `devkit-agt`
names the `devkit-dist` and `devkit-advisory` wheels next to it only because no index serves them. A tool installation names the owner of the executable
and adds this package: `uv tool install 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist' --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'`.

The bundles built into this package are `harness` (auto-selected: the guidance for rules, commit gates, workflows
and `devkit run`; its opt-in `run` preset adds the `AGENTS.md` pointer to `devkit run`) and `authoring` (opt-in: skill
and agent guide size rules with their playbooks,
[rules reference](../../docs/development/reference/rules.md#built-in-authoring-bundle)). `devkit-dist` builds in
`devkit`, `advisory` and `git-commits`
([gate reference](../../docs/development/reference/gate.md#built-in-git-commits-bundle)).

## Modules

| Module | Purpose | CLI | Reference |
| --- | --- | --- | --- |
| `devkit.rules` | Repository rule engine with autofix, project policy and Git snapshot gates | `devkit rules` | [rules reference](../../docs/development/reference/rules.md) |
| `devkit.workflow` | Data-driven delivery workflow engine | `devkit workflow` | [workflow reference](../../docs/development/reference/workflow.md) |
| `devkit.gate` | Pluggable Git commit gates and extensible hook dispatchers installed by sync | `devkit gate` | [gate reference](../../docs/development/reference/gate.md) |
| `devkit.worktree` | Activity branches (`plan-<slug>`, `dev-<slug>`) and one Git worktree per task: start (new, without a worktree, or attached to an existing branch), finish (integrate, remove, delete the branch), status, stale branches | `devkit worktree` | [worktree reference](../../docs/development/reference/worktree.md) |
| `devkit.integration` | Approval-bound local FF integration, readiness providers, exact cleanup scope and partial recovery | `devkit integration` and host MCP tools | [integration reference](../../docs/development/reference/integration.md) |
| `devkit.generated` | Tracked generated files: settle their merge conflicts by regenerating, check and regenerate them | `devkit generated` | [generated reference](../../docs/development/reference/generated.md) |
| `devkit.compact` | Verification commands with the full log on disk and a bounded view for agents | `devkit run` | [compact reference](../../docs/development/reference/compact.md) |
| `devkit.harness_guide`, `devkit.authoring_guide` | Data-only areas of the built-in `harness` and `authoring` bundles | none | [distribution reference](../../docs/development/reference/distribution.md) |

`devkit.core`, `devkit.search`, `devkit.host`, `devkit.distribution` and the root command line are
[`devkit-dist`](../devkit-dist/README.md) modules; `devkit.advisory` is the `devkit-advisory` distribution.

Layering is checked per wheel. Here: `compact` and `worktree` use only `core` and `advisory`; `rules` also uses
`compact`; `workflow` and `gate` build on `rules` (`gate` also on `compact`); `generated` uses `compact`;
`integration` uses `host` and `worktree`; the data-only bundle areas import nothing (`authoring_guide`'s rule
content uses the public rule API); enforced by `tests/test_layering.py`, which also keeps the harness command names
`devkit-dist` holds equal to the commands mounted here. The shared CLI conventions (`-w/--workspace-root`,
`--format`, exit codes) and the documentation index are in the `ARCH-01-introduction-and-goals`.
