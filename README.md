# devkit

Personal developer tools monorepo. Its main product is the `devkit-agt` distribution: one Python
package with one CLI for agent asset distribution, repository rules, delivery
workflows, commit gates, agent advisories and compact command output.

## Installing with an AI agent

Give your coding agent the installation guide and let it take over:

```text
Install devkit in this repository by following
https://github.com/mjkimR/devkit/blob/main/guides/INSTALL_GUIDE.md
```

The agent checks whether the repository is new or existing, analyzes it, proposes a plan and recommended bundles,
and asks before writing anything or committing. The guides live in [`guides/`](guides/INSTALL_GUIDE.md).

## Structure

`packages/devkit` is the package, `packages/devkit-advisory` its
`devkit.advisory` library shipped on its own for other repositories' runtime,
`packages/devkit-starter` an example content package, `packages/devkit-catalog` opt-in content bundles, `models/devkit-embed` the embedding model of the
`devkit-agt[search]` extra (built by hand, outside the workspace), `examples/bundles/` further example bundles, `scripts/` the shell logic
behind the justfile recipes, `guides/` the agent-facing installation guides, and `docs/` the documentation per module; see
[Architecture Overview, section 2](docs/architecture/overview.md#2-monorepo-structure).

## Development

Supported platforms: macOS and Linux only (POSIX). Python 3.12+, `uv`, and `just` are required (`git` too for `just smoke`).

```bash
just init                  # create the virtualenv with every workspace package and the released model wheel
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
`tools/*/pyproject.toml`; pass a project name (`devkit-agt`, `devkit-advisory`,
`devkit-starter` or `devkit-catalog`) or `all`. `devkit` remains a module-command alias for `devkit-agt`. Extra pytest arguments follow the module: `just test devkit -k cache`.
`uv run pytest` from the repository root runs every test.

The repository, CLI (`devkit`), Python namespace (`devkit.*`), bundle names and
entry-point groups retain their names. The distribution is `devkit-agt` to avoid
confusion with the unrelated `devkit` project on PyPI. It is not published to PyPI;
install it from Git or an explicit wheel URL/path.

## Using devkit in another project

No package index hosts these wheels. Each `vX.Y.Z` tag publishes a GitHub Release
with every package's wheel, `SHA256SUMS` and the install commands; install by URL:

```bash
base=https://github.com/mjkimR/devkit/releases/download/v0.1.0
uv add --dev "devkit-agt @ $base/devkit_agt-0.1.0-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-0.1.0-py3-none-any.whl"
# or, with dense and hybrid search (numpy, tokenizers and the 15 MB embedding model):
uv add --dev "devkit-agt[search] @ $base/devkit_agt-0.1.0-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-0.1.0-py3-none-any.whl" \
  "devkit-embed @ $base/devkit_embed-0.1.0-py3-none-any.whl"

uv run devkit sync          # deploys auto-selected bundles (built in: devkit, advisory)
uv run devkit add git-commits authoring   # opt-in practice bundles built into devkit
uv run devkit list
uv run devkit rules check
```

`devkit-agt` requires `devkit-advisory` of the same version, and no index serves it, so
both wheels are named. A library or service that only raises and renders advisories
at runtime depends on `devkit-advisory` alone (standard library only, no CLI, no
bundles); its development tooling adds `devkit-agt`. The import is `devkit.advisory`
either way: `devkit` is a namespace package that both wheels share.

A wheel built here works the same way by path
(`uv build --all-packages --wheel --out-dir dist`). Installing from Git
(`[tool.uv.sources]` with `subdirectory = "packages/devkit"`) brings
`devkit-advisory` from the same commit and, with the `search` extra, the model
wheel from the release `packages/devkit/pyproject.toml` pins: uv applies a Git
dependency's own sources. Declare neither again with another source, or uv
reports conflicting URLs. The example content
package `devkit-starter` is in each release too: add its wheel the same way, then
`uv run devkit add starter`. So is `devkit-catalog`, whose opt-in bundles
(`github-milestones`, ...) deploy only after `uv run devkit add <bundle>`.

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
```

Consumers with a pinned Git source must adopt a pushed commit containing this
rename before changing their dependency to `devkit-agt`; older commits and
release wheels still declare `devkit`. Wheel URLs above require a release built
from the renamed distribution.

Native skill and subagent copies go to Codex, Claude Code and Antigravity by
default; narrow them with `devkit sync --agent codex` (repeatable). To try a sync
without a consumer project, point `-w` at an existing empty directory:
`uv run --package devkit-agt devkit sync -w /tmp/my-project`.

## Releasing

Set the new version in `packages/devkit/pyproject.toml`, merge to `main`, then
push a matching tag: `git tag v0.2.0 && git push origin v0.2.0`. The release
workflow runs the full CI on the tagged commit, refuses a tag that is not on
`main` or does not match the devkit version, builds the wheels with
`just release-build <tag>` (try it locally) and
publishes the release. `devkit-advisory` has the devkit version and is bumped
with it (devkit pins it exactly; a test checks both). `devkit-starter` and `devkit-catalog` keep their own versions.

`devkit-embed` keeps its own version too and is not rebuilt by releases: devkit
installs it, in this workspace and from Git, from the release URL in the
`[tool.uv.sources]` of `packages/devkit/pyproject.toml`. When the model changes,
bump its version in `models/devkit-embed/pyproject.toml` and the `devkit-agt[search]`
requirement on it, run `just model-build` (fetches and verifies the files, builds
`dist/model/`), attach the wheel to a release
(`gh release upload <tag> dist/model/*.whl`), then point the URL at it and
run `uv lock`.

## Documentation

- [Architecture Overview](docs/architecture/overview.md): modules, interaction model, and the full documentation index.
- [devkit package](packages/devkit/README.md): module table with links to each module's reference.
- [devkit-catalog](packages/devkit-catalog/README.md): opt-in content bundles and how to add one.
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
