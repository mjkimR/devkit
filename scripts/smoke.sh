#!/usr/bin/env bash
# Consumer smoke test: build every workspace package into wheels, install the
# distribution CLI and the starter content wheel into a fresh project the way a
# consumer would, select the starter bundle, and verify the workspace converges.
# Runs locally via `just smoke` and in CI; needs `uv` on PATH and network access
# for third-party dependencies (click, pyyaml, tomlkit) unless the uv cache is warm.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

work=$(mktemp -d "${TMPDIR:-/tmp}/devkit-smoke.XXXXXX")
trap 'rm -rf "$work"' EXIT
dist="$work/dist"
project="$work/consumer"
mkdir -p "$dist" "$project"

echo "==> building wheels into $dist"
for module in $(list_modules); do
    uv build --package "$module" --wheel --out-dir "$dist" >/dev/null
done
ls -1 "$dist"

echo "==> creating a fresh consumer project"
(
    cd "$project"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-consumer --no-workspace >/dev/null
    uv add --dev --find-links "$dist" devkit-distribution devkit-starter >/dev/null
    echo "--- devkit --version"
    uv run devkit --version
    echo "--- devkit add starter"
    uv run devkit add starter
    echo "--- devkit sync --check (must exit 0)"
    uv run devkit sync --check >/dev/null
    echo "--- devkit status"
    uv run devkit status
    echo "--- AGENTS.md"
    cat AGENTS.md
    test -f .devkit/installation.json
    test -d .devkit/managed/starter
    grep -q "DEVKIT:START" AGENTS.md
    echo "--- devkit remove starter, then sync --check (must exit 0)"
    uv run devkit remove starter >/dev/null
    uv run devkit sync --check >/dev/null
)
echo "==> smoke passed"
