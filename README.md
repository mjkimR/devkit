# devkit

Personal developer tools monorepo. Its main product is `devkit`: one Python
package with one CLI for agent asset distribution, repository rules, delivery
workflows, commit gates, agent advisories and compact command output.

## Structure

`packages/devkit` is the package, `packages/devkit-advisory` its
`devkit.advisory` library shipped on its own for other repositories' runtime,
`packages/devkit-embed` the embedding model of its `devkit[search]` extra, `packages/devkit-starter` an example content
package, `examples/bundles/` further example bundles, `scripts/` the shell logic
behind the justfile recipes, and `docs/` the documentation per module; see
[Architecture Overview, section 2](docs/architecture/overview.md#2-monorepo-structure).

## Development

Supported platforms: macOS and Linux only (POSIX). Python 3.12+, `uv`, and `just` are required (`git` too for `just smoke`).

```bash
just init                  # create the virtualenv with every workspace package
just model-fetch           # download the embedding model files once (dense search tests, wheel build, smoke)
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
`tools/*/pyproject.toml`; pass a project name (`devkit`, `devkit-advisory` or
`devkit-starter`) or `all`. Extra pytest arguments follow the module: `just test devkit -k cache`.
`uv run pytest` from the repository root runs every test.

## Using devkit in another project

No package index hosts these wheels. Each `vX.Y.Z` tag publishes a GitHub Release
with every package's wheel, `SHA256SUMS` and the install commands; install by URL:

```bash
base=https://github.com/mjkimR/devkit/releases/download/v0.1.0
uv add --dev "devkit @ $base/devkit-0.1.0-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-0.1.0-py3-none-any.whl"
# or, with dense and hybrid search (numpy, tokenizers and the 15 MB embedding model):
uv add --dev "devkit[search] @ $base/devkit-0.1.0-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-0.1.0-py3-none-any.whl" \
  "devkit-embed @ $base/devkit_embed-0.1.0-py3-none-any.whl"

uv run devkit sync          # deploys auto-selected bundles (built in: devkit, advisory)
uv run devkit add git-commits authoring   # opt-in practice bundles built into devkit
uv run devkit list
uv run devkit rules check
```

`devkit` requires `devkit-advisory` of the same version, and no index serves it, so
both wheels are named. A library or service that only raises and renders advisories
at runtime depends on `devkit-advisory` alone (standard library only, no CLI, no
bundles); its development tooling adds `devkit`. The import is `devkit.advisory`
either way: `devkit` is a namespace package that both wheels share.

A wheel built here works the same way by path (`just model-fetch`, then
`uv build --all-packages --wheel --out-dir dist`). Installing from Git
(`[tool.uv.sources]` with `subdirectory = "packages/devkit"`, and
`"packages/devkit-advisory"` at the same `rev`) works without the `search` extra
only: the embedding model is not in the repository. The example content
package `devkit-starter` is in each release too: add its wheel the same way, then
`uv run devkit add starter`.

Native skill and subagent copies go to Codex, Claude Code and Antigravity by
default; narrow them with `devkit sync --agent codex` (repeatable). To try a sync
without a consumer project, point `-w` at an existing empty directory:
`uv run --package devkit devkit sync -w /tmp/my-project`.

## Releasing

Set the new version in `packages/devkit/pyproject.toml`, merge to `main`, then
push a matching tag: `git tag v0.2.0 && git push origin v0.2.0`. The release
workflow runs the full CI on the tagged commit, refuses a tag that is not on
`main` or does not match the devkit version, builds the wheels with
`just release-build <tag>` (try it locally after `just model-fetch`) and
publishes the release. `devkit-advisory` has the devkit version and is bumped
with it (devkit pins it exactly; a test checks both). `devkit-embed` and
`devkit-starter` keep their own versions; bump `devkit-embed` only when its model changes, together with the
`devkit[search]` requirement on it.

## Documentation

- [Architecture Overview](docs/architecture/overview.md): modules, interaction model, and the full documentation index.
- [devkit package](packages/devkit/README.md): module table with links to each module's reference.
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
