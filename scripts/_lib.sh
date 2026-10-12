#!/usr/bin/env bash
# Discover workspace modules from package metadata; source from the workspace root.
# Pure bash and awk, so discovery does not depend on whichever python3 is on PATH.
# Every function fails (nonzero status, message on stderr) instead of printing nothing.

# The [project] name of one pyproject.toml.
project_name() {
    awk -F'"' '
        /^\[/ { in_project = ($0 == "[project]") }
        in_project && /^name[[:space:]]*=/ { print $2; found = 1; exit }
        END { if (!found) exit 1 }
    ' "$1"
}

# "<name> <path>" for every module, in path order.
module_table() {
    local metadata name found=0
    for metadata in packages/*/pyproject.toml tools/*/pyproject.toml; do
        [ -f "$metadata" ] || continue
        if ! name=$(project_name "$metadata") || [ -z "$name" ]; then
            echo "error: no [project] name in $metadata" >&2
            return 1
        fi
        echo "$name ${metadata%/pyproject.toml}"
        found=1
    done
    if [ "$found" -eq 0 ]; then
        echo "error: no modules under packages/ or tools/ (run from the workspace root)" >&2
        return 1
    fi
}

list_modules() {
    local table
    table=$(module_table) || return 1
    echo "$table" | cut -d' ' -f1
}

resolve_module() {
    case "$1" in
        starter) echo "devkit-starter" ;;
        *) echo "$1" ;;
    esac
}

resolve_module_path() {
    local table
    table=$(module_table) || return 1
    echo "$table" | awk -v name="$1" '$1 == name { print $2; found = 1 } END { if (!found) exit 1 }'
}

should_run() {
    [ "$1" = all ] || [ "$1" = "$2" ]
}

validate_module() {
    if [ "$1" != all ] && ! resolve_module_path "$1" >/dev/null; then
        echo "Unknown module: $1" >&2
        echo "Available modules: all $(list_modules | tr '\n' ' ')" >&2
        return 1
    fi
}
