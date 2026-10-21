#!/usr/bin/env bash
# Dist-only check: run the devkit-dist tests in an environment that installs devkit-dist (with its search
# extra and its dev group) and not devkit-agt, as ADR-dist-module-split requires. The workspace environment installs
# every package, so devkit-agt entry points would stay visible there; this one is a separate environment synced
# exactly with devkit-dist from uv.lock, in a temporary directory removed on exit.
#   dist_only.sh [pytest args...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

env_dir=$(mktemp -d "${TMPDIR:-/tmp}/devkit-dist-only.XXXXXX")
trap 'rm -rf "$env_dir"' EXIT

echo "==> syncing an environment with devkit-dist only into $env_dir"
UV_PROJECT_ENVIRONMENT="$env_dir" uv sync --no-active --frozen --exact --package devkit-dist --all-extras --no-default-groups --group dist-test --quiet
python="$env_dir/bin/python"

# The check means nothing if the harness leaked in: refuse to run instead of reporting a pass.
"$python" - <<'PY'
import importlib.util
import sys
from importlib.metadata import PackageNotFoundError, version

leaked = ["devkit_agt"] if importlib.util.find_spec("devkit_agt") else []
try:
    version("devkit-agt")
except PackageNotFoundError:
    pass
else:
    leaked.append("the devkit-agt distribution")
if leaked or importlib.util.find_spec("devkit_dist.features.distribution") is None:
    sys.exit(f"error: the dist-only environment is not standalone: {', '.join(leaked) or 'devkit-dist is missing'}")
PY

echo "==> devkit-dist tests without devkit-agt"
"$python" -m pytest -c packages/devkit-dist/pyproject.toml --rootdir packages/devkit-dist -p no:cacheprovider \
    -n auto --maxprocesses 8 --dist worksteal packages/devkit-dist/tests "$@"
