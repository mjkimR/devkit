#!/usr/bin/env bash
# Shared implementation for workspace development commands:
#   module.sh <action> [module|all] [selectors...] [extra args...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

action=${1:?Expected an action}
requested_target=${2:-all}
target=$(resolve_module "$requested_target")
shift $(($# < 2 ? $# : 2))
validate_module "$target"
# The arguments as given, for the preflight's [FIX]; selectors are shifted off below.
# `${a[@]+"${a[@]}"}` expands an empty array under `set -u` on macOS's bash 3.2.
given=("$@")

# The directory names under a module's tests/, the areas a selector can name (shared helpers excluded).
areas() {
    local dir names=()
    for dir in "$1"/tests/*/; do
        [ -d "$dir" ] || continue
        dir=$(basename "$dir")
        case "$dir" in
            __pycache__|testsupport|distsupport) ;;
            *) names+=("$dir") ;;
        esac
    done
    echo "${names[*]-}"
}

# Append the test paths one selector names to `selected`: an existing path (a `::` node suffix allowed) from the
# repository root as given, else one from the module directory, else the area's existing `tests/<name>` and
# `src/*/<name>` directories.
add_selector() {
    local base=$1 selector=$2 dir found=0
    if [ -e "${selector%%::*}" ]; then
        selected+=("$selector")
        return 0
    fi
    if [ -e "$base/${selector%%::*}" ]; then
        selected+=("$base/$selector")
        return 0
    fi
    for dir in "$base/tests/$selector" "$base"/src/*/"$selector"; do
        if [ -d "$dir" ]; then
            selected+=("$dir")
            found=1
        fi
    done
    [ "$found" -eq 1 ] && return 0
    echo "Unknown area for $target: $selector" >&2
    echo "Available areas: $(areas "$base")" >&2
    echo "A path is taken from the repository root or from $base." >&2
    return 1
}

# Selectors (`just test devkit gate worktree -k foo`): the arguments before the first option replace a single
# module's default test paths; the rest go to pytest. `all` passes everything on, as pytest's own paths override
# the configured testpaths.
selected=()
if [ "$target" != all ]; then
    case "$action" in
        test|test-cov)
            module_path=$(resolve_module_path "$target")
            while [ $# -gt 0 ] && [ "${1#-}" = "$1" ]; do
                add_selector "$module_path" "$1" || exit 2
                shift
            done
            ;;
    esac
fi
# Assigned before the loop so a discovery failure aborts under `set -e`.
modules=$(list_modules)
# pytest-xdist: worksteal keeps the slow Git-hook tests from piling onto one worker;
# extra arguments come later, so `-n0` runs serially (for pdb or a single test).
xdist=(-n auto --maxprocesses 8 --dist worksteal)

if [ "$action" = init ]; then
    if [ "$target" = all ]; then
        uv sync --no-active --all-packages
    else
        # --inexact keeps the other workspace packages and the dev tools installed.
        uv sync --no-active --inexact --package "$target"
    fi
    exit 0
fi

# Repository dogfooding only: keep a direct path when the runner itself is under repair.
case "${DEVKIT_RUN_MODE:-compact}" in
    compact|raw) ;;
    *) echo "Expected DEVKIT_RUN_MODE=compact or raw" >&2; exit 2 ;;
esac

run_check() {
    if [ "${DEVKIT_RUN_MODE:-compact}" = raw ]; then
        uv run --no-active "$@"
    else
        uv run --no-active devkit run -- uv run --no-active "$@"
    fi
}

# asyncio and the MCP SDK use local sockets to wake their event loops from threads.
# Fail before pytest starts when a sandbox blocks those writes; the caller owns approval and retry.
case "$action" in
    test|test-cov)
        uv run --no-active python scripts/check_test_environment.py -- just "$action" "$requested_target" \
            ${given[@]+"${given[@]}"}
        ;;
esac

# One pytest session over every module: the root configuration lists all test paths.
if [ "$target" = all ]; then
    case "$action" in
        test)
            run_check pytest "${xdist[@]}" "$@"
            exit 0
            ;;
        test-cov)
            cov=()
            for module in $modules; do
                cov+=("--cov=$(resolve_module_path "$module")/src")
            done
            run_check pytest "${xdist[@]}" "${cov[@]}" --cov-config=pyproject.toml "$@"
            exit 0
            ;;
    esac
fi

for module in $modules; do
    should_run "$target" "$module" || continue
    path=$(resolve_module_path "$module")
    # Tests may also live beside the code (each rule's `tests/` folder under src), so src is collected too.
    test_paths=("$path/tests")
    if [ -d "$path/src" ]; then
        test_paths+=("$path/src")
    fi
    if [ ${#selected[@]} -gt 0 ]; then
        test_paths=("${selected[@]}")
    fi
    case "$action" in
        lint)
            run_check ruff check --fix "$path"
            run_check ruff format "$path"
            ;;
        lint-check)
            run_check ruff check "$path"
            run_check ruff format --check "$path"
            ;;
        check) run_check pyright "$path" ;;
        test) run_check pytest "${xdist[@]}" "${test_paths[@]}" "$@" ;;
        test-cov)
            COVERAGE_FILE=".coverage.$module" \
                run_check pytest "${xdist[@]}" --cov="$path/src" --cov-config=pyproject.toml "${test_paths[@]}" "$@"
            ;;
        *) echo "Unknown action: $action" >&2; exit 1 ;;
    esac
done
