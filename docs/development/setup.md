# Development Setup

Prerequisites and initial setup for contributing to devkit.

## 1. Prerequisites

- **OS**: macOS or Linux (POSIX).
- **Python**: 3.12+
- **Tooling**: `uv` (>= 0.4.0), `just` (>= 1.35.0), and `git`.

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
just test                  # Run pytest across all workspace packages (the full suite)
just test devkit gate      # Run one module's areas or paths only
just test-affected         # Run the tests the changes since main can affect (--list to only show them)
just test-cov              # Run pytest with coverage report
just rules-check           # Run devkit governance rules check on the working tree
just smoke                 # Build packages and verify fresh consumer installation
```
