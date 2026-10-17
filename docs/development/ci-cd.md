# CI/CD Pipeline

Continuous integration and automated verification checks for devkit.

## 1. Automated Verification Checks

The `ci` workflow runs by manual dispatch (`gh workflow run ci`) or through `workflow_call` from the release
workflow. Pull requests and main branch pushes do not trigger it. Workspace checks run on Linux and macOS;
consumer smoke runs on Linux. The workflow executes:

| Step | Command Executed | Purpose |
| :--- | :--- | :--- |
| **Lint & Format** | `just lint-check` | Enforces Ruff formatting and linter invariants. |
| **Type Check** | `just check` | Enforces Pyright static typing across all workspace code. |
| **Test Suite** | `just test` | Runs the full pytest test suite across all workspace packages. |
| **Governance Rules** | `just rules-check` | Runs devkit governance rules on the working tree. |
| **Consumer Smoke** | `just smoke` | Builds wheels and verifies installation in a clean consumer environment. |

For cumulative branch verification before integration, also run `just rules-check --ci --base <base-ref>` locally.
The consumer smoke installs the base packages first, preserving their independent coverage, then installs the
`devkit-spec` wheel and checks command mounting, opt-in docs seeding and seeded document discovery.

## 2. Test Execution and Restricted Environments

`just test [module]` and `just test-cov [module]` use pytest-xdist with
`-n auto --maxprocesses 8 --dist worksteal`: up to eight workers, sharing work as workers become available.
Extra pytest arguments follow these defaults, so `just test all -n0` runs serially.

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
CI continues to run the complete suite through `just test`.

## 3. Release Automation

Tags matching `v*` trigger the release workflow. It requires a tag on `main` matching the `devkit-agt` version,
runs the reusable CI workflow on that commit, then calls `just release-build <tag>` to build every workspace
package wheel and generate `SHA256SUMS` and installation notes. It publishes those artifacts in a GitHub Release.
The separately released embedding-model wheel is referenced by URL and is not rebuilt.
