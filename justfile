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

# Run pytest for a specific module or all modules
test module="all" *args:
    bash scripts/module.sh test "$@"

# Run pytest with test coverage report
test-cov module="all" *args:
    bash scripts/module.sh test-cov "$@"

# Run the rule engine check (devkit rules check)
rules-check *args:
    uv run --no-active --package devkit devkit rules check "$@"

# Run rule engine autofix (devkit rules fix)
rules-fix *args:
    uv run --no-active --package devkit devkit rules fix "$@"

# Show each rule's default/effective phase, project overrides, and pending promotions
rules-phases *args:
    uv run --no-active --package devkit devkit rules phases "$@"

# Describe one rule: phase, severity, effective settings and guide
rules-explain *args:
    uv run --no-active --package devkit devkit rules explain "$@"

# Run the workflow engine CLI (new, bind, next, show, checks, validate, list, requests, answer, return, handoff, envelope)
workflow *args:
    uv run --no-active --package devkit devkit workflow "$@"

# Run the commit gate CLI (install, uninstall, status, run)
gate *args:
    uv run --no-active --package devkit devkit gate "$@"

# Build all wheels and exercise them from a fresh consumer project (needs git)
smoke:
    bash scripts/smoke.sh
