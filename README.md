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

`packages/devkit-core` owns the independent `devkit_core` foundation; `packages/devkit-cli` the agent-first
command-line boundary (`devkit_cli`) that `devkit` and other repositories' click tools build on;
`packages/devkit-dist` is the distribution package with the CLI, `packages/devkit` the harness package
(`devkit-agt`), `packages/devkit-advisory` the `devkit.advisory` library shipped on its own for other
repositories' runtime,
`packages/devkit-docs` the document system (`devkit docs`, the document model and the document rules),
`packages/devkit-spec` the Spec-Driven Development (SDD) extension built on it,
`tools/devkit-dev` the repository development bundle and its structure rules,
`packages/devkit-adaptive` the opt-in adaptive development bundle,
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
`tools/*/pyproject.toml`; pass a project name (`devkit-core`, `devkit-cli`, `devkit-dist`, `devkit-agt`, `devkit-advisory`,
`devkit-docs`, `devkit-spec`, `devkit-adaptive`, `devkit-starter`, `devkit-catalog` or `devkit-viewer`) or `all`. Short names are accepted too:
`agt` and `devkit` for `devkit-agt`, and `dev`, `core`, `cli`, `dist`, `mcp`, `starter`, `adaptive`, `catalog`, `docs`, `spec` and `viewer` for
`devkit-<name>` (`scripts/_lib.sh` `module_short_names`; an unknown name prints both lists). Feature names select their tests across tiers and matching source subtrees; tier names (`unit`, `integration`, `e2e`) or explicit paths also narrow `test` and `test-cov`, and extra pytest arguments follow them: `just test devkit gate worktree -k cache`. `just test-affected [--base REF] [--list] [-- PYTEST-ARGS]` derives the paths from the changes since the merge base with `main`.

This repository's lint, type-check and test recipes use `devkit run` for bounded output.
When changing or repairing the runner, use `DEVKIT_RUN_MODE=raw just test` (also supported by
the lint, check and coverage recipes) to run tools directly. CI runs the full checks in raw mode
and separately runs the compact tests through `devkit run`.

`uv run pytest` from the repository root runs every test.

The CLI (`devkit`), bundle names and entry-point groups retain their names. Python imports expose
wheel ownership: `devkit_dist`, `devkit_agt`, `devkit_core`, `devkit_cli`, `devkit_docs`, `devkit_spec`, `devkit_mcp` and
`devkit_viewer`. The runtime advisory library preserves `devkit.advisory`. The distributions are
`devkit-dist` and `devkit-agt` to avoid confusion with the unrelated `devkit` project on PyPI.
They are not published to PyPI; install them from Git or an explicit wheel URL/path.

## Using devkit in another project

No package index hosts these wheels. Each `vX.Y.Z` tag publishes a GitHub Release
with changed wheels, `SHA256SUMS`, a complete `release-inventory.json` and install commands. Unchanged wheels retain their original URLs; install the inventory-selected closure:

```bash
# Read each URL from the chosen release-inventory.json or copy its generated release-note command.
uv add --dev "devkit-agt @ <devkit-agt-inventory-wheel-url>" \
  "devkit-dist @ <devkit-dist-inventory-wheel-url>" \
  "devkit-core @ <devkit-core-inventory-wheel-url>" \
  "devkit-cli @ <devkit-cli-inventory-wheel-url>" \
  "devkit-advisory @ <devkit-advisory-inventory-wheel-url>"
# or, with dense and hybrid search (numpy, tokenizers and the 15 MB embedding model):
uv add --dev "devkit-agt[search] @ <devkit-agt-inventory-wheel-url>" \
  "devkit-dist[search] @ <devkit-dist-inventory-wheel-url>" \
  "devkit-core @ <devkit-core-inventory-wheel-url>" \
  "devkit-cli @ <devkit-cli-inventory-wheel-url>" \
  "devkit-advisory @ <devkit-advisory-inventory-wheel-url>" \
  "devkit-embed @ <devkit-embed-inventory-wheel-url>"

uv run devkit sync          # deploys auto-selected bundles (built in: devkit, advisory, harness)
uv run devkit add git-commits authoring   # opt-in practice bundles built into devkit
uv run devkit list
uv run devkit rules check
```

`devkit-agt` requires `devkit-dist`, `devkit-core`, `devkit-cli` and `devkit-advisory` at their actual inventory-selected versions, and no index
serves them, so all five wheels are named. A repository that only deploys agent assets installs `devkit-dist` (with
`devkit-core`, `devkit-cli` and `devkit-advisory`) alone: it gets sync, context loading, playbooks and native hooks, the `devkit` and `advisory`
bundles, and no harness command or guidance (`devkit rules` and the other harness commands answer with
`HARNESS_COMMAND_UNAVAILABLE`). A Git installation declares exactly one of the two, never both (`devkit-agt` brings
`devkit-dist` from the same commit); a release-wheel installation of `devkit-agt` names the `devkit-dist`, `devkit-core`, `devkit-cli`
and `devkit-advisory` wheels next to it only because no index serves them. A library or service that only raises
and renders advisories at runtime depends on `devkit-advisory` alone (standard library only, no CLI, no bundles);
its development tooling adds `devkit-dist` or `devkit-agt`. A click tool that agents run depends at runtime on
`devkit-cli` (with `devkit-advisory`) for devkit's output contract, and its repository can select the opt-in `cli-tool`
bundle of `devkit-catalog` for the structure guide and rules. The import remains `devkit.advisory`; only the advisory wheel contributes to the `devkit` namespace. A tool installation names the owner of the `devkit` executable
and adds the harness: `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`.

A wheel built here works the same way by path
(`uv build --all-packages --wheel --out-dir dist`). Installing from Git
(`[tool.uv.sources]` with `subdirectory = "packages/devkit"`, or `packages/devkit-dist`) brings
`devkit-dist`, `devkit-core`, `devkit-cli` and `devkit-advisory` from the same commit and, with the `search` extra, the model
wheel from the release `packages/devkit-dist/pyproject.toml` pins: uv applies a Git
dependency's own sources. Declare none of them again with another source, or uv
reports conflicting URLs. The example content
package `devkit-starter` is in each release too: add its wheel the same way, then
`uv run devkit add starter`. So is `devkit-catalog`, whose opt-in bundles deploy
only after `uv run devkit add <bundle>`.
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

Edit root `VERSION` (for example, `0.1.7`), then run:

```bash
just version-sync --baseline scripts/releases/baseline-v0.1.6.json
just version-check --baseline scripts/releases/baseline-v0.1.6.json
just release-build v0.1.7 --baseline scripts/releases/baseline-v0.1.6.json
```

First import one completed lockstep release's original wheels and SHA256SUMS explicitly:

```bash
uv run python scripts/version.py --bootstrap v0.1.6 --source v0.1.6 \
  --artifacts dist/original-v0.1.6 --output scripts/releases/baseline-v0.1.6.json --repository mjkimR/devkit
```

These paths and tags illustrate inputs; they do not assert that historical assets are available. Missing or corrupt
originals block bootstrap. Commit the verified baseline, `VERSION`, generated package metadata, `uv.lock`, sync receipt
and `scripts/releases/pending.json` together. Only changed distributions and exact-pin reverse dependents take the
release version; unchanged packages and bundles retain their versions. Repeated preparation compares with the same
completed baseline and logically unwinds recorded generated edits. Lock or sync failure leaves an incomplete plan
and no success sentinel. Resolve the failure and rerun the same command. For the next release, pass that release's completed inventory;
tooling verifies and supersedes its retained committed plan without unwinding published metadata. An older baseline
that disagrees with current package versions refuses. Metadata edited during comparison is preserved and preparation
refuses before generated writes; rerun after editing finishes.

After the metadata reaches `main`, the maintainer authorizes the matching tag. CI verifies main ancestry and the
committed complete plan, builds changed publication wheels, verifies reused originals, then publishes a completed
inventory last. Retry reuses matching uploaded bytes and uploads missing assets only; a mismatch refuses. No wheel
identity is rebuilt and republished. `ARCH-07-deployment` and `ADR-selective-package-versions` own the contract.
The executable version remains installed `devkit-dist`; static package metadata supports standalone Git builds.

To refresh the handbook for this release, run the `devkit-dev/handbook` playbook after editing `VERSION` and before
the metadata commit; only a release whose tag equals `handbook/manifest.json`'s tag checks the handbook
before it builds, through the script behind `just handbook release-check <tag>`.

Synchronization also runs `uv run --no-active devkit sync` after locking to refresh deployed bundles and
`.devkit/installation.json`. Commit the refreshed receipt with the release metadata. A sync failure stops release
preparation without a success sentinel; resolve its advisory and rerun `just version-sync`.

`devkit-embed` keeps its own version too and is not rebuilt by releases: devkit
installs it, in this workspace and from Git, from the committed wheel in
`models/devkit-embed/wheels/` pinned in `[tool.uv.sources]`. When the model changes,
bump its version in `models/devkit-embed/pyproject.toml` and the `devkit-dist[search]`
requirement on it, run `just model-build` (fetches and verifies the files, builds
`dist/model/`), copy the built wheel into `models/devkit-embed/wheels/`, and run `uv lock`.

## Documentation

- `ARCH-01-introduction-and-goals`: modules, interaction model, and the full documentation index.
- [devkit-dist](packages/devkit-dist/README.md) and [devkit-agt](packages/devkit/README.md): module tables with links to each module's reference.
- [devkit-adaptive](packages/devkit-adaptive/README.md): adaptive development guidance and reusable agents.
- [devkit-catalog](packages/devkit-catalog/README.md): opt-in content bundles and how to add one.
- [devkit-viewer](packages/devkit-viewer/README.md): the local repository viewer and its frontend commands (`just viewer ...`).
- Handbook for people: a release snapshot of the Living Spec in English and Korean under `handbook/en/` and
  `handbook/ko/`, written when a release preparation refreshes it on request; each page names the release it
  describes, and `docs/` prevails on any conflict (`CAP-DLV-release-handbook`).
- Examples: [devkit-starter](packages/devkit-starter/README.md), [delivery-workflow bundle](examples/bundles/delivery-workflow/README.md).
