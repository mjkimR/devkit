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
`devkit-spec` wheel and checks command mounting, opt-in docs seeding and seeded document discovery, and finally
installs the `devkit-viewer` wheel, starts `devkit viewer serve` for the consumer project and fetches its bundled
page, a script and `/api/repos`.

## 2. Test Execution and Restricted Environments

`just test [module]` and `just test-cov [module]` use pytest-xdist with
`-n auto --maxprocesses 8 --dist worksteal`: up to eight workers, sharing work as workers become available.
Extra pytest arguments follow these defaults, so `just test all -n0` runs serially.

Development, review and integration use affected tests without a separate mandatory local `just test`.
Before integration, incorporate any moved base, resolve conflicts and run `just test-affected --base <base-ref>`
against the actual target branch. A merge of the same verified content needs no additional test run. If the base
or content changes before merging, refresh affected tests and the checks that cover the new content. Reviewers
reuse valid check results and rerun only missing or stale checks. Lint, types and governance remain required:

- **Selectors**: for a single module, the arguments before the first option are areas or paths that replace the
  module's default paths. An area is a directory under the module's `tests/` together with the matching
  `src/<package>/<area>` directory (`just test devkit gate worktree -k cache`); a path from the repository root is
  passed as given and one from the module directory (`tests/gate/test_hooks.py`) is prefixed with it, a `::` node
  suffix included. An unknown area exits `2`, lists the module's areas (shared helpers such as `testsupport` and
  `distsupport` excluded) and says where paths are taken from, before any tool runs. `all` passes its arguments to pytest unchanged.
- **`just test-affected [--base REF] [--list] [-- PYTEST-ARGS]`** (`scripts/affected_tests.py`): collects the paths
  changed since the merge base of `HEAD` and `REF` (default `main`; committed, staged, unstaged, untracked, both
  sides of a rename) and selects tests from them:
  - Shared foundations (`devkit.core`, `devkit-advisory`, `cli.py`, `__main__.py`, any `pyproject.toml` or
    `conftest.py`, `uv.lock`, the shared test helpers `testsupport` and `distsupport`) select the full suite.
  - Repository files that tests read (`docs/`, `examples/`, `models/`, the recipe scripts and `justfile`) select
    those tests from a fixed table.
  - A package source change selects the test groups (a `devkit-dist` or `devkit-agt` area, a top-level test file of
    either, another workspace package) that import its area or an area importing it, transitively by static imports;
    a `devkit-dist` or `devkit-agt` source change also selects the tests over the whole devkit source tree (layering,
    documented codes, CLI wiring, stdout kinds).
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
- **Limits**: a group's dependencies include those of the shared helpers it imports at module level,
  not of helpers imported inside a test function; static imports also do not show tests that run the CLI in a
  subprocess or load entry points. Nightly and release full CI cover these misses; an undetected regression can
  remain on the default branch until a complete CI runs. The selector's full-suite fallback remains in place.

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

Tags matching `v*` trigger the release workflow. It requires a tag on `main` matching the version of `devkit-dist`,
`devkit-agt` and `devkit-advisory` (released in lockstep),
runs the reusable CI workflow on that commit, then calls `just release-build <tag>` to build every workspace
package wheel and generate `SHA256SUMS` and installation notes. It publishes those artifacts in a GitHub Release.
The separately released embedding-model wheel is referenced by URL and is not rebuilt.
