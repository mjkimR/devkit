# devkit

Personal developer tools monorepo. Its main product is the `devkit` CLI in two distributions released
together: `devkit-dist` (agent asset distribution: bundles, native projections, sync, context loading,
playbooks, native hooks and the `devkit` executable) and `devkit-agt` (the developer harness on top of it:
repository rules, delivery workflows, commit gates, task worktrees and compact command output), with
`devkit-advisory` for agent advisories.

## Installing with an AI agent

Give your coding agent the installation guide and let it take over:

```text
Install devkit in this repository by following
https://github.com/mjkimR/devkit/blob/main/guides/INSTALL_GUIDE.md
```

The agent checks whether the repository is new or existing, analyzes it, proposes a plan and recommended bundles,
and asks before writing anything or committing. The guides live in [`guides/`](guides/INSTALL_GUIDE.md).

## Structure

`packages/devkit-core` owns the independent `devkit_core` foundation;
`packages/devkit-dist` is the distribution package with the CLI, `packages/devkit` the harness package
(`devkit-agt`), `packages/devkit-advisory` the `devkit.advisory` library shipped on its own for other
repositories' runtime,
`packages/devkit-spec` the Spec-Driven Development (SDD) extension,
`tools/devkit-dev` the repository development bundle and its structure rules,
`packages/devkit-starter` an example content package, `packages/devkit-catalog` opt-in content bundles,
`packages/devkit-viewer` the local repository viewer (`devkit viewer serve`, with its Svelte frontend), `models/devkit-embed` the embedding model of the
`search` extra of `devkit-dist` and `devkit-agt` (built by hand, outside the workspace), `examples/bundles/` further example bundles, `scripts/` the shell logic
behind the justfile recipes, `guides/` the agent-facing installation guides, and `docs/` the Living Spec documentation; see
`ARCH-05-1-containers`.

Application packages place behavior in `features/<feature>/`, with transport adapters, use cases,
services, repositories and models added as needed. Shared contracts and technical helpers belong in
optional `base/` and `utils/`; `devkit_core` uses `base/` and `core/` for the shared foundation.
Application-owned content lives in `bundles/<name>/bundle/`, including single-bundle packages.
Content packages and `tools/devkit-dev` can remain bundle-only. Package initializers manage exports,
imports and loading; business logic lives in named modules. See `ARCH-05-2-components` for dependencies.

Package tests use `tests/unit/`, `tests/integration/` and `tests/e2e/` as needed, mirroring source
ownership within each tier, with helpers in `tests/support/`. Rule tests stay beside their rules.
The repository's wheel-installation consumer smoke is cross-package e2e coverage; see
[CI/CD](docs/development/ci-cd.md#2-test-execution-and-restricted-environments).

## Development

Supported platforms: macOS and Linux only (POSIX). Python 3.12+, `uv`, and `just` are required (`git` too for `just smoke`).

```bash
just init                  # create the virtualenv with every workspace package and the released model wheel
just lint                  # ruff fix + format (just lint-check verifies only, as CI does)
just check                 # pyright
just test                  # pytest; just test-cov adds coverage
just test-dist             # the devkit-dist tests in a separate environment without devkit-agt
just test devkit gate      # one module's areas or paths
just test-affected         # the tests the changes since main can affect
just rules-check           # devkit rules check on the working tree
just rules-check --staged  # the exact staged tree
just rules-check --ci --base origin/main
just smoke                 # build the wheels and exercise them from a fresh consumer project
just --list                # every recipe (rules-fix, rules-phases, rules-explain, workflow, gate, ...)
```

Module commands discover projects from `packages/*/pyproject.toml` and
`tools/*/pyproject.toml`; pass a project name (`devkit-core`, `devkit-dist`, `devkit-agt`, `devkit-advisory`,
`devkit-spec`, `devkit-starter`, `devkit-catalog` or `devkit-viewer`) or `all`. Short names are accepted too:
`agt` and `devkit` for `devkit-agt`, and `dev`, `core`, `dist`, `mcp`, `starter`, `catalog`, `spec` and `viewer` for
`devkit-<name>` (`scripts/_lib.sh` `module_short_names`; an unknown name prints both lists). Feature names select their tests across tiers and matching source subtrees; tier names (`unit`, `integration`, `e2e`) or explicit paths also narrow `test` and `test-cov`, and extra pytest arguments follow them: `just test devkit gate worktree -k cache`. `just test-affected [--base REF] [--list] [-- PYTEST-ARGS]` derives the paths from the changes since the merge base with `main`.

This repository's lint, type-check and test recipes use `devkit run` for bounded output.
When changing or repairing the runner, use `DEVKIT_RUN_MODE=raw just test` (also supported by
the lint, check and coverage recipes) to run tools directly. CI runs the full checks in raw mode
and separately runs the compact tests through `devkit run`.

`uv run pytest` from the repository root runs every test.

The CLI (`devkit`), bundle names and entry-point groups retain their names. Python imports expose
wheel ownership: `devkit_dist`, `devkit_agt`, `devkit_core`, `devkit_spec`, `devkit_mcp` and
`devkit_viewer`. The runtime advisory library preserves `devkit.advisory`. The distributions are
`devkit-dist` and `devkit-agt` to avoid confusion with the unrelated `devkit` project on PyPI.
They are not published to PyPI; install them from Git or an explicit wheel URL/path.

## Using devkit in another project

No package index hosts these wheels. Each `vX.Y.Z` tag publishes a GitHub Release
with every package's wheel, `SHA256SUMS` and the install commands; install by URL:

```bash
base=https://github.com/mjkimR/devkit/releases/download/v<version>
uv add --dev "devkit-agt @ $base/devkit_agt-<version>-py3-none-any.whl" \
  "devkit-dist @ $base/devkit_dist-<version>-py3-none-any.whl" \
  "devkit-core @ $base/devkit_core-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl"
# or, with dense and hybrid search (numpy, tokenizers and the 15 MB embedding model):
uv add --dev "devkit-agt[search] @ $base/devkit_agt-<version>-py3-none-any.whl" \
  "devkit-dist[search] @ $base/devkit_dist-<version>-py3-none-any.whl" \
  "devkit-core @ $base/devkit_core-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl" \
  "devkit-embed @ $base/devkit_embed-0.1.0-py3-none-any.whl"

uv run devkit sync          # deploys auto-selected bundles (built in: devkit, advisory, harness)
uv run devkit add git-commits authoring   # opt-in practice bundles built into devkit
uv run devkit list
uv run devkit rules check
```

`devkit-agt` requires `devkit-dist`, `devkit-core` and `devkit-advisory` of the same version, and no index serves them, so
all four wheels are named. A repository that only deploys agent assets installs `devkit-dist` (with
`devkit-core` and `devkit-advisory`) alone: it gets sync, context loading, playbooks and native hooks, the `devkit` and `advisory`
bundles, and no harness command or guidance (`devkit rules` and the other harness commands answer with
`HARNESS_COMMAND_UNAVAILABLE`). A Git installation declares exactly one of the two, never both (`devkit-agt` brings
`devkit-dist` from the same commit); a release-wheel installation of `devkit-agt` names the `devkit-dist`, `devkit-core` and
`devkit-advisory` wheels next to it only because no index serves them. A library or service that only raises
and renders advisories at runtime depends on `devkit-advisory` alone (standard library only, no CLI, no bundles);
its development tooling adds `devkit-dist` or `devkit-agt`. The import remains `devkit.advisory`; only the advisory wheel contributes to the `devkit` namespace. A tool installation names the owner of the `devkit` executable
and adds the harness: `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`.

A wheel built here works the same way by path
(`uv build --all-packages --wheel --out-dir dist`). Installing from Git
(`[tool.uv.sources]` with `subdirectory = "packages/devkit"`, or `packages/devkit-dist`) brings
`devkit-dist` and `devkit-advisory` from the same commit and, with the `search` extra, the model
wheel from the release `packages/devkit-dist/pyproject.toml` pins: uv applies a Git
dependency's own sources. Declare none of them again with another source, or uv
reports conflicting URLs. The example content
package `devkit-starter` is in each release too: add its wheel the same way, then
`uv run devkit add starter`. So is `devkit-catalog`, whose opt-in bundles
(such as `host-observer`) deploy only after `uv run devkit add <bundle>`.
So is `devkit-viewer`, which mounts `devkit viewer serve`.

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
# or distribution only:
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
```

Upgrading from a `devkit-agt` that predates `devkit-dist` deploys the new auto-selected `harness` bundle and moves
the `devkit:run` preset to `harness:run`; the
[installation guide](guides/install/existing-repository.md#upgrading-across-the-package-split) lists every change.

Native skill and subagent copies go to Codex, Claude Code and Antigravity by
default; narrow them with `devkit sync --agent codex` (repeatable). To try a sync
without a consumer project, point `-w` at an existing empty directory:
`uv run --package devkit-agt devkit sync -w /tmp/my-project`.

## Releasing

Set the new version in `packages/devkit-dist/pyproject.toml`, `packages/devkit/pyproject.toml` and
`packages/devkit-advisory/pyproject.toml` (with the exact pins between them), merge to `main`, then
push a matching tag: `git tag v0.2.0 && git push origin v0.2.0`. The release
workflow runs the full CI on the tagged commit, refuses a tag that is not on
`main` or does not match all three versions, builds the wheels with
`just release-build <tag>` (try it locally) and
publishes the release. `devkit-dist`, `devkit-agt` and `devkit-advisory` are released in lockstep:
`devkit-agt` pins `devkit-dist` and `devkit-advisory` exactly, `devkit-dist` pins `devkit-advisory`, and a test
checks all three. `devkit-spec`, `devkit-starter`, `devkit-catalog` and `devkit-viewer` keep their own versions.

`devkit-embed` keeps its own version too and is not rebuilt by releases: devkit
installs it, in this workspace and from Git, from the committed wheel in
`models/devkit-embed/wheels/` pinned in `[tool.uv.sources]`. When the model changes,
bump its version in `models/devkit-embed/pyproject.toml` and the `devkit-dist[search]`
requirement on it, run `just model-build` (fetches and verifies the files, builds
`dist/model/`), copy the built wheel into `models/devkit-embed/wheels/`, and run `uv lock`.

## Documentation

- `ARCH-01-introduction-and-goals`: modules, interaction model, and the full documentation index.
- [devkit-dist](packages/devkit-dist/README.md) and [devkit-agt](packages/devkit/README.md): module tables with links to each module's reference.
- [devkit-catalog](packages/devkit-catalog/README.md): opt-in content bundles and how to add one.
- [devkit-viewer](packages/devkit-viewer/README.md): the local repository viewer and its frontend commands (`just viewer ...`).
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
