#!/usr/bin/env bash
# Shared implementation for workspace development commands:
#   module.sh <action> [module|all] [extra args...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

action=${1:?Expected an action}
target=$(resolve_module "${2:-all}")
shift $(($# < 2 ? $# : 2))
validate_module "$target"
# Assigned before the loop so a discovery failure aborts under `set -e`.
modules=$(list_modules)

if [ "$action" = init ]; then
    if [ "$target" = all ]; then
        uv sync --no-active --all-packages
    else
        # --inexact keeps the other workspace packages and the dev tools installed.
        uv sync --no-active --inexact --package "$target"
    fi
    exit 0
fi

# One pytest session over every module: the root configuration lists all test paths.
if [ "$target" = all ]; then
    case "$action" in
        test)
            uv run --no-active pytest "$@"
            exit 0
            ;;
        test-cov)
            cov=()
            for module in $modules; do
                cov+=("--cov=$(resolve_module_path "$module")/src")
            done
            uv run --no-active pytest "${cov[@]}" --cov-config=pyproject.toml "$@"
            exit 0
            ;;
    esac
fi

for module in $modules; do
    should_run "$target" "$module" || continue
    path=$(resolve_module_path "$module")
    case "$action" in
        lint)
            uv run --no-active ruff check --fix "$path"
            uv run --no-active ruff format "$path"
            ;;
        lint-check)
            uv run --no-active ruff check "$path"
            uv run --no-active ruff format --check "$path"
            ;;
        check) uv run --no-active pyright "$path" ;;
        test) uv run --no-active pytest "$path/tests" "$@" ;;
        test-cov)
            COVERAGE_FILE=".coverage.$module" \
                uv run --no-active pytest --cov="$path/src" --cov-config=pyproject.toml "$path/tests" "$@"
            ;;
        *) echo "Unknown action: $action" >&2; exit 1 ;;
    esac
done
