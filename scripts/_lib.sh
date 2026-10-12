#!/usr/bin/env bash
# Discover workspace modules from package metadata; source from workspace root.

list_modules() {
    python3 - <<'PY'
import tomllib
from pathlib import Path

for parent in (Path("packages"), Path("tools")):
    for metadata in sorted(parent.glob("*/pyproject.toml")):
        with metadata.open("rb") as stream:
            print(tomllib.load(stream)["project"]["name"])
PY
}

resolve_module() {
    case "$1" in
        rule-engine|rules|rule) echo "agent-rule-engine" ;;
        workflow-engine|workflow|wf) echo "agent-workflow-engine" ;;
        *) echo "$1" ;;
    esac
}

resolve_module_path() {
    local requested=$1
    python3 - "$requested" <<'PY'
import sys
import tomllib
from pathlib import Path

for parent in (Path("packages"), Path("tools")):
    for metadata in sorted(parent.glob("*/pyproject.toml")):
        with metadata.open("rb") as stream:
            if tomllib.load(stream)["project"]["name"] == sys.argv[1]:
                print(metadata.parent)
                sys.exit(0)
sys.exit(1)
PY
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
