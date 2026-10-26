# Recipe parameters reach the shell as positional arguments, so quoting survives ("$@").
set positional-arguments

# Print available commands
default:
    @just --list

# Initialize workspace or a specific module
init module="all":
    bash scripts/module.sh init "$1"

# Run ruff format and lint with automatic fixes
lint module="all":
    bash scripts/module.sh lint "$1"

# Check linting and formatting without modifying files
lint-check module="all":
    bash scripts/module.sh lint-check "$1"

# Run pyright static type checking over sources and tests
check module="all":
    bash scripts/module.sh check "$1"

# Run pytest for a module or all; areas or paths after a module narrow it (just test devkit gate -k foo)
test module="all" *args:
    bash scripts/module.sh test "$@"

# Run e2e tests for a module or all; areas or paths after a module narrow it (just test-e2e [module])
test-e2e module="all" *args:
    bash scripts/module.sh test-e2e "$@"

# Run only the tests the changes since a base can affect (just test-affected [--base REF] [--list] [--e2e] [-- PYTEST-ARGS])
test-affected *args:
    uv run --no-active python scripts/affected_tests.py "$@"

# Run the devkit-dist tests in a separate environment without devkit-agt (dist-only check)
test-dist *args:
    bash scripts/dist_only.sh "$@"

# Run pytest with test coverage report (same module, area and path selection as test)
test-cov module="all" *args:
    bash scripts/module.sh test-cov "$@"

# Run the rule engine check (devkit rules check)
rules-check *args:
    uv run --no-active --package devkit-agt devkit rules check "$@"

# Run rule engine autofix (devkit rules fix)
rules-fix *args:
    uv run --no-active --package devkit-agt devkit rules fix "$@"

# Show each rule's default/effective phase, project overrides, and pending promotions
rules-phases *args:
    uv run --no-active --package devkit-agt devkit rules phases "$@"

# Describe one rule: phase, severity, effective settings and guide
rules-explain *args:
    uv run --no-active --package devkit-agt devkit rules explain "$@"

# Run the tests in each rule's folder (devkit rules test [RULE-ID...] [-- PYTEST-ARGS...])
rules-test *args:
    uv run --no-active --package devkit-agt devkit rules test "$@"

# Run the workflow engine CLI (new, bind, next, show, checks, validate, list, requests, answer, return, handoff, envelope)
workflow *args:
    uv run --no-active --package devkit-agt devkit workflow "$@"

# Run the commit gate CLI (install, uninstall, status, run)
gate *args:
    uv run --no-active --package devkit-agt devkit gate "$@"

# Frontend of devkit-viewer (needs Node): install, lint, check, test, build (the committed page) or pack [dir]
viewer action *args:
    bash scripts/viewer.sh "$@"

# Serve the Living Spec and repository documents locally (devkit viewer serve)
viewer-serve *args:
    uv run --no-active --package devkit-viewer devkit viewer serve "$@"

# Build all wheels and exercise them from a fresh consumer project (needs git)
smoke:
    bash scripts/smoke.sh

# Fetch, verify and convert the embedding model files, then build the devkit-embed wheel into dist/model
# (only when the model changes; see README, Releasing)
model-build:
    uv run --no-active python scripts/fetch_model.py models/devkit-embed/src/devkit_embed
    uv build --wheel models/devkit-embed --out-dir dist/model

# Synchronize package versions and internal pins from root VERSION, then refresh uv.lock
version-sync:
    python3 scripts/version.py

# Check release metadata against root VERSION without writing files
version-check:
    python3 scripts/version.py --check

# Refresh tooling of the release handbook: status, stamp PAGE..., generate [--preview], verify [--preview], release-check TAG
handbook *args:
    uv run --no-active python scripts/handbook.py "$@"

# Build the release wheels, SHA256SUMS and notes for a vX.Y.Z tag into dist/
release-build tag:
    bash scripts/release.sh "$1"
