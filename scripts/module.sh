#!/usr/bin/env bash
# Shared implementation for workspace development commands.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

action=${1:?Expected an action}
target=$(resolve_module "${2:-all}")
validate_module "$target"
shift 2

if [ "$action" = init ]; then
    if [ "$target" = all ]; then
        uv sync --no-active --all-packages
    else
        uv sync --no-active --package "$target"
    fi
    exit 0
fi

for module in $(list_modules); do
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
        check) uv run --no-active pyright "$path/src" ;;
        test) uv run --no-active pytest "$path/tests" "$@" ;;
        test-cov)
            uv run --no-active pytest --cov="$path/src" --cov-config=pyproject.toml "$path/tests" "$@"
            ;;
        *) echo "Unknown action: $action" >&2; exit 1 ;;
    esac
done
