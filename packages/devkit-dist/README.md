# devkit-dist

Agent asset distribution in one Python package with the `devkit` command line: bundles, native agent projections,
transactional sync and the installation receipt, context loading, playbooks and native host hooks. The distribution
name is `devkit-dist`; imports are `devkit.*` (`devkit.core`, `devkit.search`, `devkit.host`, `devkit.distribution`,
`devkit.cli`). It owns the sole `devkit` console script, the `.devkit/config.toml` schema and the receipt format.
Requires Python 3.12 or later; runtime dependencies are `click`, `jinja2`, `pyyaml`, `tomlkit` and `devkit-advisory`
(the `devkit.advisory` library, same version). The `search` extra (`devkit-dist[search]`) adds `numpy`, `tokenizers`
and the embedding model package for dense and hybrid search; the `mcp` extra adds the SDK for native stdio services and
confirmation.

`devkit-dist` alone deploys skills, subagents, instructions, playbooks, guidance, documents and host hooks; it runs
no repository rules, commit gates or delivery workflows. The developer harness (`devkit rules`, `devkit workflow`,
`devkit gate`, `devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`) is the
[`devkit-agt`](../devkit/README.md) package, which depends on `devkit-dist` at the same version and mounts its
commands under the same `devkit` executable. In a standalone installation a harness command name answers with
`HARNESS_COMMAND_UNAVAILABLE`, and deployed rule, gate or workflow assets with a `HARNESS_ENGINE_MISSING` warning; both
name the requirement to add.

## Install

No package index hosts the wheel; install it from Git (which brings `devkit-advisory` from the same commit) or by URL
from a GitHub Release with the `devkit-advisory` wheel next to it (see the
[root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
uv run devkit sync            # deploys every installed bundle that declares auto_select (built in: devkit, advisory)
uv run devkit add <bundle>    # selects any other bundle: the built-in git-commits or another content package
```

A project that uses the harness declares `devkit-agt` instead, never both: `devkit-agt` brings `devkit-dist`. A tool
installation names the script owner and adds the harness:
`uv tool install 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist' --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'`.

## Modules

| Module | Purpose | CLI | Reference |
| --- | --- | --- | --- |
| `devkit.core` | Shared foundation: frontmatter grammar, installation receipt, safe paths, atomic writes, Git runner, deadlines, file locks, plugin loading, project discovery, CLI plumbing | none | [core reference](../../docs/development/reference/core.md) |
| `devkit.distribution` | Bundle packaging and transactional synchronization, plus the built-in `devkit` guide bundle | `devkit sync`, `add`, `remove`, `list`, `status`, ... | [distribution reference](../../docs/development/reference/distribution.md) |
| `devkit.host` | Lifecycle hooks, optional MCP transport, native confirmation and service dispatch; distribution owns hook deployment | `devkit host` | [host reference](../../docs/development/reference/host.md) |
| `devkit.search` | Lexical, dense and hybrid document search; dense needs the `search` extra | none | [search reference](../../docs/development/reference/search.md) |
| `devkit.cli` | The root `devkit` group: built-in commands, then `devkit.commands` plugins, then the name-only harness list | `devkit` | `ARCH-05-3-command-plugins` |

The built-in bundles are `devkit` (consumption guidance, auto-selected), `advisory` (the Agent Advisory Protocol guides,
auto-selected; data area `devkit.advisory_guide`) and `git-commits` (commit message conventions, opt-in; data area
`devkit.commits_guide`).

Layering (`advisory` < `core` < `search`/`host` < `distribution`; the data-only bundle areas import nothing) is
enforced by `tests/test_layering.py`, which also refuses any reference to a `devkit-agt` area. The tests run without
`devkit-agt` installed: `just test-dist` syncs an environment with only this package and its extras.
