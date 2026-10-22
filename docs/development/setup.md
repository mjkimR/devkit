# Development Setup

Prerequisites and initial setup for contributing to devkit.

## 1. Prerequisites

- **OS**: macOS or Linux (POSIX).
- **Python**: 3.12+
- **Tooling**: `uv` (>= 0.4.0), `just` (>= 1.35.0), and `git`.
- **Frontend changes only**: Node (^22.22.2, ^24.15.0 or >= 26) and npm, for the `devkit-viewer` page and library under
  `packages/devkit-viewer/frontend/`. Installing and testing the Python packages never needs Node.

## 2. Workspace Initialization

Run the initialization recipe to create the virtual environment and install workspace packages:

```bash
git clone https://github.com/mjkimR/devkit.git
cd devkit
just init
```

`just init` resolves all workspace members (`packages/*`), installs test and development dependencies, and links the local packages.

## 3. Common Verification Commands

```bash
just lint                  # Run ruff check --fix and ruff format
just lint-check            # Verify linting without modifying files (as in CI)
just check                 # Run Pyright static type checker
just test                  # Full suite: nightly/release CI, manual checks, or selector fallback
just test devkit gate      # Run one module's areas or paths only
just test-affected         # Run the tests the changes since main can affect (--list to only show them)
just test-dist             # Run the devkit-dist tests in a separate environment without devkit-agt
just test-cov              # Run pytest with coverage report
just rules-check           # Run devkit governance rules check on the working tree
just smoke                 # Build packages and verify fresh consumer installation
```

After changing `packages/devkit-viewer/frontend/` (see [viewer](reference/viewer.md)):

```bash
just viewer install        # npm ci
just viewer lint           # prettier --check
just viewer check          # svelte-check, warnings fail
just viewer test           # vitest
just viewer build          # rebuild the committed page; commit it with the sources
just viewer pack           # the library tarball a host vendors, checked for its exports
```
