#!/usr/bin/env bash
# Build an inventory-selected release; require an explicit completed --baseline FILE.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
uv run --no-active python scripts/releases/cli.py build "$@"
