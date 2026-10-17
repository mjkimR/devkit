# CI/CD Pipeline

Continuous integration and automated verification checks for devkit.

## 1. Automated Verification Checks

Pull requests and main branch pushes execute the following verification steps:

| Step | Command Executed | Purpose |
| :--- | :--- | :--- |
| **Lint & Format** | `just lint-check` | Enforces Ruff formatting and linter invariants. |
| **Type Check** | `just check` | Enforces Pyright static typing across all workspace code. |
| **Test Suite** | `just test` | Runs the full pytest test suite across all workspace packages. |
| **Governance Rules** | `just rules-check --ci --base origin/main` | Runs devkit governance rules against modified files. |
| **Consumer Smoke** | `just smoke` | Builds wheels and verifies installation in a clean consumer environment. |

## 2. Release Automation

Tags matching `v*` trigger the release workflow:
1. Builds wheels for all packages via `uv build --all-packages`.
2. Generates `SHA256SUMS`.
3. Creates a GitHub Release and attaches the built wheel artifacts.
