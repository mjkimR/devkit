# Print available commands
default:
    @just --list

# Initialize workspace or a specific module (all, agent-rule-engine)
init module="all":
    #!/usr/bin/env bash
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    if [ "$target" = "all" ]; then
        echo "Initializing workspace..."
        uv sync --no-active
    else
        echo "Initializing $target..."
        uv sync --no-active --package "$target"
    fi

    just hooks-install

# Run ruff format and lint with automatic fixes
lint module="all":
    #!/usr/bin/env bash
    set -e
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    for m in agent-rule-engine; do
        if should_run "$target" "$m"; then
            path=$(resolve_module_path "$m")
            if [ -d "$path" ]; then
                echo "Linting $m ($path)..."
                uv run --no-active ruff check --fix "$path"
                uv run --no-active ruff format "$path"
            fi
        fi
    done

# Check linting and formatting without modifying files
lint-check module="all":
    #!/usr/bin/env bash
    set -e
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    for m in agent-rule-engine; do
        if should_run "$target" "$m"; then
            path=$(resolve_module_path "$m")
            if [ -d "$path" ]; then
                echo "Checking lint for $m ($path)..."
                uv run --no-active ruff check "$path"
                uv run --no-active ruff format --check "$path"
            fi
        fi
    done

# Run pyright static type checking
check module="all":
    #!/usr/bin/env bash
    set -e
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    for m in agent-rule-engine; do
        if should_run "$target" "$m"; then
            path=$(resolve_module_path "$m")
            if [ -d "$path/src" ]; then
                echo "Type checking $m ($path)..."
                uv run --no-active pyright "$path/src"
            fi
        fi
    done

# Run pytest for a specific module or all modules
test module="all" +args="":
    #!/usr/bin/env bash
    set -e
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    for m in agent-rule-engine; do
        if should_run "$target" "$m"; then
            path=$(resolve_module_path "$m")
            if [ -d "$path/tests" ]; then
                echo "Testing $m ($path)..."
                uv run --no-active pytest "$path/tests" {{ args }}
            fi
        fi
    done

# Run pytest with test coverage report
test-cov module="all":
    #!/usr/bin/env bash
    set -e
    source ./scripts/_lib.sh
    target=$(resolve_module "{{ module }}")
    validate_module "$target"

    for m in agent-rule-engine; do
        if should_run "$target" "$m"; then
            path=$(resolve_module_path "$m")
            if [ -d "$path/tests" ]; then
                echo "Testing with coverage for $m ($path)..."
                uv run --no-active pytest --cov="$path/src" --cov-config=pyproject.toml "$path/tests"
            fi
        fi
    done

# Install pre-commit git hooks
hooks-install:
    uv run --no-active pre-commit install

# Run pre-commit hooks on all files
hooks-run:
    uv run --no-active pre-commit run --all-files

# Run rule engine linting checks
rules-check +args="":
    uv run --no-active agent-rules check {{ args }}

# Run rule engine autofix
rules-fix +args="":
    uv run --no-active agent-rules fix {{ args }}
