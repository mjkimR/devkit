# Print available commands
default:
    @just --list

# Initialize workspace or a specific module
init module="all":
    bash scripts/module.sh init "{{ module }}"

# Run ruff format and lint with automatic fixes
lint module="all":
    bash scripts/module.sh lint "{{ module }}"

# Check linting and formatting without modifying files
lint-check module="all":
    bash scripts/module.sh lint-check "{{ module }}"

# Run pyright static type checking
check module="all":
    bash scripts/module.sh check "{{ module }}"

# Run pytest for a specific module or all modules
test module="all" +args="":
    bash scripts/module.sh test "{{ module }}" {{ args }}

# Run pytest with test coverage report
test-cov module="all" +args="":
    bash scripts/module.sh test-cov "{{ module }}" {{ args }}

# Run rule engine linting checks
rules-check +args="":
    uv run --no-active --package agent-rule-engine agent-rules check {{ args }}

# Run rule engine autofix
rules-fix +args="":
    uv run --no-active --package agent-rule-engine agent-rules fix {{ args }}

# Show each rule's default/effective phase, project overrides, and pending promotions
rules-phases +args="":
    uv run --no-active --package agent-rule-engine agent-rules phases {{ args }}

# Describe one rule: phase, severity, effective settings and guide
rules-explain +args="":
    uv run --no-active --package agent-rule-engine agent-rules explain {{ args }}

# Run the workflow engine CLI (new, bind, next, show, checks, validate, list, envelope)
workflow +args="":
    uv run --no-active --package agent-workflow-engine agent-workflow {{ args }}

# Run the commit gate CLI (install, uninstall, status, run)
gate +args="":
    uv run --no-active --package agent-commit-gate commit-gate {{ args }}

# Build all wheels and exercise them from a fresh consumer project
smoke:
    bash scripts/smoke.sh
