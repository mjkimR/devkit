# CI/CD Pipeline

Continuous integration and automated verification checks for devkit.

## 1. Automated Verification Checks

The `ci` workflow runs by manual dispatch (`gh workflow run ci`) or through `workflow_call` from the nightly and
release workflows. Pull requests and main branch pushes do not trigger it. The `nightly` wrapper is scheduled at
04:17 Asia/Seoul (`17 19 * * *` UTC) on the default branch. Its cheap gate queries the latest successful `nightly.yml`
run on that branch: when that head equals the scheduled head, it skips the complete CI; otherwise it runs every
CI job. No previous success runs CI. Failures and cancellations do not advance the baseline, so an unverified head
is retried on the next schedule even without new commits. API failures fail the gate. A skipped heavy job can only
reuse the same previously verified head. Manual nightly dispatch (`gh workflow run nightly`), direct manual CI and
release calls always run the complete CI. Scheduled starts can be delayed or dropped by GitHub; 04:17 is not a
completion deadline. See `ADR-nightly-ci-verification`.

Workspace checks run on Linux and macOS;
consumer smoke and the viewer job run on Linux. The workflow executes:

| Step | Command Executed | Purpose |
| :--- | :--- | :--- |
| **Lint & Format** | `just lint-check` | Enforces Ruff formatting and linter invariants. |
| **Type Check** | `just check` | Enforces Pyright static typing across all workspace code. |
| **Test Suite** | `just test` | Runs the full pytest test suite across all workspace packages. |
| **Dist-only Tests** | `just test-dist` | Syncs a separate environment with `devkit-dist` and its extras only (`scripts/dist_only.sh`), refuses to run if any `devkit-agt` module is importable there, and runs the `devkit-dist` tests without the harness. |
| **Governance Rules** | `just rules-check` | Runs devkit governance rules on the working tree. |
| **Consumer Smoke** | `just smoke` | Builds wheels and verifies installation in a clean consumer environment. |
| **Viewer Frontend** | `just viewer install`, `lint`, `check`, `test`, `pack` | With Node 24: formatting, `svelte-check`, the frontend tests and the library tarball's contents and exports. |
| **Viewer Build** | `uv run --no-active devkit generated check viewer-assets` | Rebuilds the page from the lockfile in a clean checkout and fails when the committed build under `packages/devkit-viewer/src/devkit_viewer/static/` differs. |

For cumulative branch verification before integration, also run `just rules-check --ci --base <base-ref>` locally.
The consumer smoke first installs the `devkit-dist` wheel alone (distribution-only sync, the coded answers to harness
command names and to rule assets no engine runs, one owner of the `devkit` executable) and a `uv tool install` of
`devkit-dist` with `devkit-agt`, then installs the base packages, preserving their independent coverage, then installs the
`devkit-spec` and `devkit-docs` wheels and checks that `devkit spec` and `devkit docs` mount, opt-in docs seeding and
seeded document discovery, and finally
installs the `devkit-viewer` wheel, starts `devkit viewer serve` for the consumer project and fetches its bundled
page, a script and `/api/repos`.

## 2. Test Execution and Restricted Environments

Package tests use `tests/unit/`, `tests/integration/` and `tests/e2e/`, creating only tiers they
need. Below each tier, paths mirror source ownership (`features/<feature>/`, `base/`, `core/`,
`adapters/` or `bundles/`); package-wide installation and architecture checks use `package/`.
Shared helper modules live in `tests/support/`, and fixtures live in the narrowest useful
`conftest.py`.

- **Unit** tests isolate a behavior or contract. CLI parsing and output with a substituted use case
  are unit tests.
- **Integration** tests connect real components or exercise filesystem, Git, entry-point discovery
  and other external boundaries. A temporary filesystem still exercises that boundary.
- **E2e** tests exercise an installed product through its public CLI or MCP interface. The
  repository-owned `scripts/smoke*.py` and `scripts/smoke.sh` cover clean wheel installations and
  cross-package consumer combinations; packages do not duplicate that shared suite.

A rule's tests remain under `<rule>/tests/`, where they deploy and can run independently with the
rule (`CAP-GOV-rule-authoring`). These tiers classify the exercised boundary, regardless of whether
the owning package is an application, library or content wheel.

`just test [module]` and `just test-cov [module]` use pytest-xdist with
`-n auto --maxprocesses 8 --dist worksteal`: up to eight workers, sharing work as workers become available.
Extra pytest arguments follow these defaults, so `just test all -n0` runs serially.

Development, review and integration use affected tests without a separate mandatory local `just test`.
Before integration, run `just test-affected --base <base-ref>` on the task branch. Local integration merges a
conflict-free moved base itself and runs only the CI rules on the merged result (`ADR-moved-target-merge`); merge the
base into the task branch, resolve conflicts and refresh the affected tests only after it reports a conflict or a
failing check. Once every unit of a local-orchestrated run is finished, run `just test-affected --base <batch start>`
once on `main`, keeping its `mode=full` fallback; outside such a run, a later batch run or nightly CI tests the
combined head (`ADR-post-batch-test-run`). If the content changes before merging, refresh affected tests and the
checks that cover the new content. Reviewers reuse valid check results and rerun only missing or stale checks. Lint,
types and governance remain required:

- **Selectors**: for a single module, the arguments before the first option are areas or paths that replace the
  module's default paths. A feature name selects its tests across the available tiers together with its
  matching source subtree, including embedded rule tests (`just test devkit gate worktree -k cache`). A tier
  selector such as `unit` selects that category. A path from the repository root is passed as given and one
  from the module directory (`tests/integration/features/gate/test_hooks.py`) is prefixed with it, a `::` node
  suffix included. An unknown area exits `2`, lists the module's areas (shared `support` helpers excluded)
  and says where paths are taken from, before any tool runs. `all` passes its arguments to pytest unchanged.
- **`just test-affected [--base REF] [--list] [-- PYTEST-ARGS]`** (`scripts/affected_tests.py`): collects the paths
  changed since the merge base of `HEAD` and `REF` (default `main`; committed, staged, unstaged, untracked, both
  sides of a rename) and selects tests from them:
  - Shared foundations (`devkit-core`, `devkit-advisory`, `cli.py`, `__main__.py`, any `pyproject.toml` or
    `conftest.py`, `uv.lock`, the shared helpers in `tests/support/`) select the full suite.
  - Repository files that tests read (`docs/`, `examples/`, `models/`, the recipe scripts and `justfile`) select
    those tests from a fixed table.
  - A package source change selects individual `test_*.py` files, including embedded rule tests, through
    transitive static imports. Production nodes remain feature areas and coarse workspace packages by default;
    `devkit_spec` uses module nodes, including package initializers. Fine tests keep their specific dependencies;
    opaque/root imports and known CLI, bundle and source-tree consumers retain broad owner dependencies.
    A `devkit-dist` or `devkit-agt` source change also selects mandatory whole-source-tree checks (layering,
    documented codes, CLI wiring and stdout kinds). MCP changes retain their explicit integration consumers.
  - Dependency discovery includes absolute/relative imports, literal dynamic import/resource calls, re-exports,
    executed initializers, transitive local helpers (including function-local imports), and ancestor conftests.
    Ambiguous static dependencies widen conservatively. Unreadable or unparseable relevant files, ambiguous source
    inventories, unknown sources and deleted/renamed fine modules that cannot be reconstructed select full.
  - A changed `test_*.py` in a `tests` directory selects itself; any other file there selects its directory.
  - The devkit-viewer frontend (`packages/devkit-viewer/frontend/`, `scripts/viewer.sh`) selects no pytest test:
    pytest never exercises it. The result names the frontend checks instead (below); the page they rebuild under
    `src/devkit_viewer/static/` is package source and selects the viewer's tests.
  - Planning records and agent projections (`specs/`, `.claude/`, `.agents/`, `.codex/`, `.devkit/`), `guides/`,
    `.github/`, the smoke and release scripts, `.gitignore`, `.python-version` and Markdown at the repository or a
    package root select nothing.
  - Any other path selects the full suite.
- **Result**: stdout's first line is
  `[TEST_SELECTION: mode=<full|partial|none> base=<ref> changed=<n> paths=<n> reason=<text>]` (`reason=frontend`
  for a frontend-only change). When a frontend path changed, the next line is
  `[FRONTEND_CHECK: just viewer install && just viewer lint && just viewer check && just viewer test && just viewer
  pack && just viewer build]`, the checks of the CI viewer job: the agent runs that command (Node and npm) and
  commits the rebuilt page with the sources. `--list` adds one `[TEST_PATH: <path>]` per path and runs nothing.
  Otherwise `full` and `partial` run `just test all [paths...]`
  with its preflight, options and exit code, and `none` exits `0`. A base without a merge base is the input error
  `TEST_BASE_UNKNOWN` (exit `2`), whose `[FIX]` lists the existing branches; a failing `git diff` or `git ls-files`
  is `TEST_CHANGES_UNREADABLE` (exit `2`), for the user to resolve in the repository before rerunning.
- **Limits**: selection is static and does not execute production modules or pytest. Known subprocess/entry-point
  consumers have explicit mappings; arbitrary runtime discovery is not inferred. Helper modules keep all their real
  imports even when only one helper function is used. Complete nightly/manual/release checks remain the backstop;
  an undetected runtime dependency can leave a regression until complete CI runs. Full-suite fallback is preserved.


Before starting pytest or its workers, both recipes run `scripts/check_test_environment.py` through the
workspace Python environment. The check sends and receives one byte through a local socket pair, with
one-second I/O timeouts. Python's asyncio uses local sockets to wake an event loop from another thread;
blocking these writes can stall MCP initialization and async integration tests even when no internet access
is needed.

When the check fails, it emits the `ASYNC_WAKEUP_BLOCKED` advisory on stderr and exits `2` before pytest starts.
The advisory preserves the original recipe and pytest arguments in `[FIX]`. An agent uses its execution tool's
approval mechanism to rerun that command in a permitted environment; the script never expands permissions or
retries on its own. Tests are neither skipped nor counted as passed. A direct `pytest` invocation bypasses this
recipe check; run `uv run python scripts/check_test_environment.py -- <exact-test-command>` first when using it.
Nightly, manual and release CI run the complete suite through `just test`. Release publication requires CI success.

## 3. Release Automation

Tags matching `v*` trigger the release workflow. It requires a tag on `main` matching root `VERSION` and every
workspace distribution. `just version-sync` updates static versions, versioned internal pins and `uv.lock`;
`just version-check` checks metadata without writes. Release builds also require `uv lock --check` to pass. The workflow
runs the reusable CI workflow on that commit, then calls `just release-build <tag>` to build every workspace
package wheel and generate `SHA256SUMS` and installation notes. It publishes those artifacts in a GitHub Release.
The separately released embedding-model wheel is referenced by URL and is not rebuilt.
Before any wheel build, `just release-build` runs the handbook release check, which verifies the handbook only when
its manifest names the tag being built (`ARCH-07-deployment` §1.2, `CAP-DLV-release-handbook`).

Synchronization also runs `uv run --no-active devkit sync` after locking to refresh deployed bundles and
`.devkit/installation.json`. Commit the refreshed receipt with the release metadata. A sync failure stops release
preparation without a success sentinel; resolve its advisory and rerun `just version-sync`.

Root `VERSION` names the last released version between releases and moves to the next one only in the release
commit; the next number is chosen then, because a breaking change needs a minor bump
(`ARCH-07-deployment` §1). Prepare a release in this order:

1. Finish every `docs/` change the release carries.
2. Set `VERSION` to the release version and run `just version-sync`.
3. When the release carries a handbook refresh, refresh and stamp its pages, then run `just handbook generate` and
   `just handbook verify`; the manifest takes its tag from `VERSION` and its source commit from `HEAD`.
4. Run `just version-check` and `just handbook release-check v<VERSION>`, commit, and tag that commit on `main`.

Between generating the handbook and tagging, change nothing under `docs/`: the release check fails a tag whose
handbook source commit no longer matches the tagged `docs/`.
