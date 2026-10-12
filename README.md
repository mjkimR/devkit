# devkit

Personal developer tools monorepo. Its main product is `devkit`: one Python
package with one CLI for agent asset distribution, repository rules, delivery
workflows and commit gates.

## Structure

```text
devkit/
├── packages/
│   ├── devkit/                # The devkit package and its single `devkit` CLI
│   │   └── src/devkit/
│   │       ├── core/          # Shared foundation: frontmatter, receipt, paths, Git, plugins, project root
│   │       ├── advisory/      # Agent Advisory Protocol errors and the `advisory` guide bundle
│   │       ├── rules/         # Repository rule engine (`devkit rules`)
│   │       ├── workflow/      # Delivery workflow engine (`devkit workflow`)
│   │       ├── gate/          # Pluggable Git commit gates (`devkit gate`)
│   │       └── distribution/  # Bundle synchronization (`devkit sync`, `add`, ...) and the `devkit` guide bundle
│   └── devkit-starter/        # Example external content package
├── examples/bundles/          # Example bundles: `starter` (mirror of devkit-starter's bundle) and `delivery-workflow`
├── scripts/                   # Shell logic behind the justfile recipes
└── docs/                      # Documentation per module (see Documentation below)
```

## Development

Python 3.12+, `uv`, and `just` are required (`git` too for `just smoke`).

```bash
just init                  # create the virtualenv with every workspace package
just lint                  # ruff fix + format (just lint-check verifies only, as CI does)
just check                 # pyright
just test                  # pytest; just test-cov adds coverage
just rules-check           # devkit rules check on the working tree
just rules-check --staged  # the exact staged tree
just rules-check --ci --base origin/main
just smoke                 # build the wheels and exercise them from a fresh consumer project
just --list                # every recipe (rules-fix, rules-phases, rules-explain, workflow, gate, ...)
```

Module commands discover projects from `packages/*/pyproject.toml` and
`tools/*/pyproject.toml`; pass a project name (`devkit` or `devkit-starter`) or
`all`. Extra pytest arguments follow the module: `just test devkit -k cache`.
`uv run pytest` from the repository root runs every test.

## Using devkit in another project

No package index hosts these wheels yet. Build them here and install them by
path (or install from Git with `uv add --dev "devkit @ git+<repository URL>#subdirectory=packages/devkit"`):

```bash
# In this repository
uv build --package devkit --wheel --out-dir dist
uv build --package devkit-starter --wheel --out-dir dist

# In the consumer project
uv add --dev /path/to/devkit/dist/devkit-0.1.0-py3-none-any.whl \
  /path/to/devkit/dist/devkit_starter-0.1.0-py3-none-any.whl
uv run devkit sync          # deploys the bundles built into devkit (devkit, advisory)
uv run devkit add starter   # selects a bundle from another package and synchronizes
uv run devkit list
uv run devkit rules check
```

Native skill and subagent copies go to Codex, Claude Code and Antigravity by
default; narrow them with `devkit sync --agent codex` (repeatable). To try a sync
without a consumer project, point `-w` at an existing empty directory:
`uv run --package devkit devkit sync -w /tmp/my-project`.

## Documentation

- [Architecture Overview](docs/architecture/overview.md): modules, interaction model, and the full documentation index.
- [devkit package](packages/devkit/README.md): module map and layering.
- References: [distribution](docs/distribution/reference.md), [rules](docs/rules/reference.md), [workflow](docs/workflow/reference.md), [gate](docs/gate/reference.md), [advisory](docs/advisory/reference.md), [core](docs/core/reference.md).
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
