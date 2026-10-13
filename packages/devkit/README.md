# devkit

Agent asset distribution, repository rules, delivery workflows, commit gates,
agent advisories and compact command output in one Python package with one CLI
(`devkit`). Requires Python 3.12 or later; runtime dependencies are `click`,
`pyyaml` and `tomlkit`. The `search` extra (`devkit[search]`) adds `numpy`,
`tokenizers` and the embedding model package for dense and hybrid search.

## Install

No package index hosts the wheel; install it by URL from a GitHub Release (or a
built wheel by path), with `devkit-embed` next to it for the `search` extra (see
the [root README](../../README.md#using-devkit-in-another-project)):

```bash
uv add --dev "devkit @ https://github.com/mjkimR/devkit/releases/download/v0.1.0/devkit-0.1.0-py3-none-any.whl"
uv run devkit sync            # deploys every installed bundle that declares auto_select (built in: devkit, advisory)
uv run devkit add <bundle>    # selects any other bundle: built-in opt-in ones or another content package
```

The built-in opt-in bundles are `authoring` (skill and agent guide size rules
with their playbooks, [docs/rules](../../docs/rules/reference.md#built-in-authoring-bundle))
and `git-commits` (commit message conventions,
[docs/gate](../../docs/gate/reference.md#built-in-git-commits-bundle)).

## Modules

| Module | Purpose | CLI | Reference |
| --- | --- | --- | --- |
| `devkit.core` | Shared foundation: frontmatter grammar, installation receipt, safe paths, Git runner, plugin loading, project discovery, CLI plumbing | none | [docs/core](../../docs/core/reference.md) |
| `devkit.advisory` | Agent Advisory Protocol (errors, warnings, notices), plus the built-in `advisory` guide bundle | none | [docs/advisory](../../docs/advisory/reference.md) |
| `devkit.rules` | Repository rule engine with autofix, project policy and Git snapshot gates | `devkit rules` | [docs/rules](../../docs/rules/reference.md) |
| `devkit.workflow` | Data-driven delivery workflow engine | `devkit workflow` | [docs/workflow](../../docs/workflow/reference.md) |
| `devkit.gate` | Pluggable Git commit gates and managed hook wrappers | `devkit gate` | [docs/gate](../../docs/gate/reference.md) |
| `devkit.distribution` | Bundle packaging and transactional synchronization, plus the built-in `devkit` guide bundle | `devkit sync`, `add`, `remove`, `list`, `status`, ... | [docs/distribution](../../docs/distribution/reference.md) |
| `devkit.search` | Lexical, dense and hybrid document search; dense needs the `devkit[search]` extra | none | [docs/search](../../docs/search/reference.md) |
| `devkit.compact` | Verification commands with the full log on disk and a bounded view for agents | `devkit run` | [docs/compact](../../docs/compact/reference.md) |

Layering (`advisory` < `core` < `rules` < `workflow`/`gate`; `search` and
`compact` use only `core` and `advisory`, `distribution` also `search`, `gate` also `compact`; enforced by a test), the shared CLI
conventions (`-w/--workspace-root`, `--format`, exit codes) and the documentation
index are in the [Architecture Overview](../../docs/architecture/overview.md).
