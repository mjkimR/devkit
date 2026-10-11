# Print available commands
default:
    @just --list

# Initialize workspace or a specific module
init module="all":
    bash scripts/module.sh init "{{ module }}"
    just hooks-install

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

# Install pre-commit git hooks
hooks-install:
    uv run --no-active pre-commit install

# Run pre-commit hooks on all files
hooks-run:
    uv run --no-active pre-commit run --all-files

# Run rule engine linting checks
rules-check +args="":
    uv run --no-active --package agent-rule-engine agent-rules check {{ args }}

# Run rule engine autofix
rules-fix +args="":
    uv run --no-active --package agent-rule-engine agent-rules fix {{ args }}
