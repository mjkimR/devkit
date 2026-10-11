#!/usr/bin/env bash
# Shared helpers for devkit module resolution.
# Source this file from scripts or justfile recipes: source ./scripts/_lib.sh

AVAILABLE_MODULES="all agent-rule-engine"

resolve_module() {
    case "$1" in
        agent-rule-engine|rule-engine|rules|rule) echo "agent-rule-engine" ;;
        all) echo "all" ;;
        *) echo "$1" ;;
    esac
}

resolve_module_path() {
    case "$1" in
        agent-rule-engine) echo "packages/agent-rule-engine" ;;
        *) echo "$1" ;;
    esac
}

should_run() {
    [ "$1" = "all" ] || [ "$1" = "$2" ]
}

validate_module() {
    case "$1" in
        all|agent-rule-engine) ;;
        *)
            echo "Unknown module: $1" >&2
            echo "Available modules: $AVAILABLE_MODULES" >&2
            return 1
            ;;
    esac
}
