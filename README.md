# devkit

Personal developer tools monorepo. Its main product is `devkit`: one Python
package with one CLI for agent asset distribution, repository rules, delivery
workflows, commit gates, agent advisories and compact command output.

## Structure

`packages/devkit` is the package, `packages/devkit-starter` an example content
package, `examples/bundles/` further example bundles, `scripts/` the shell logic
behind the justfile recipes, and `docs/` the documentation per module; see
[Architecture Overview, section 2](docs/architecture/overview.md#2-monorepo-structure).

## Development

Supported platforms: macOS and Linux only (POSIX). Python 3.12+, `uv`, and `just` are required (`git` too for `just smoke`).

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
uv run devkit sync          # deploys auto-selected bundles (built in: devkit, advisory)
uv run devkit add starter   # selects a bundle without auto_select and synchronizes
uv run devkit add git-commits authoring   # opt-in practice bundles built into devkit
uv run devkit list
uv run devkit rules check
```

Native skill and subagent copies go to Codex, Claude Code and Antigravity by
default; narrow them with `devkit sync --agent codex` (repeatable). To try a sync
without a consumer project, point `-w` at an existing empty directory:
`uv run --package devkit devkit sync -w /tmp/my-project`.

## Documentation

- [Architecture Overview](docs/architecture/overview.md): modules, interaction model, and the full documentation index.
- [devkit package](packages/devkit/README.md): module table with links to each module's reference.
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
