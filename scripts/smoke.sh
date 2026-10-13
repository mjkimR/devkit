#!/usr/bin/env bash
# Consumer smoke test: build every workspace package into wheels, install the
# devkit wheel and the starter content wheel into a fresh project the way a
# consumer would, verify the built-in bundles are deployed by default, select the
# starter bundle, verify the workspace converges, exercise every CLI group, and
# make real commits through the installed gate hooks in a fresh Git repository.
# The wheels are installed by path, so a same-named package on an index can never
# be picked instead. Runs locally via `just smoke` and in CI; needs `uv` and `git`
# on PATH and network access for third-party dependencies (click, pyyaml, tomlkit)
# unless the uv cache is warm.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

work=$(mktemp -d "${TMPDIR:-/tmp}/devkit-smoke.XXXXXX")
trap 'rm -rf "$work"' EXIT
dist="$work/dist"
project="$work/consumer"
mkdir -p "$dist" "$project"

# Assigned before the loop so a discovery failure aborts under `set -e`.
modules=$(list_modules)
echo "==> fetching the embedding model files (the model wheel refuses to build without them)"
uv run --no-active python scripts/fetch_model.py packages/devkit-embed/src/devkit_embed
echo "==> building wheels into $dist"
for module in $modules; do
    uv build --package "$module" --wheel --out-dir "$dist" >/dev/null
done
ls -1 "$dist"
wheel() {
    local matches=("$dist/$1"-*.whl)
    if [ "${#matches[@]}" -ne 1 ] || [ ! -f "${matches[0]}" ]; then
        echo "error: expected exactly one $1 wheel in $dist" >&2
        return 1
    fi
    echo "${matches[0]}"
}
devkit_wheel=$(wheel devkit)
starter_wheel=$(wheel devkit_starter)
model_wheel=$(wheel devkit_embed)

echo "==> creating a fresh consumer project"
(
    cd "$project"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-consumer --no-workspace >/dev/null
    uv add --dev "$devkit_wheel" "$starter_wheel" >/dev/null
    echo "--- devkit --version"
    uv run devkit --version
    echo "--- devkit sync (built-in bundles are selected by default)"
    uv run devkit sync >/dev/null
    grep -q '"devkit"' .devkit/installation.json
    grep -q '"advisory"' .devkit/installation.json
    test -d .devkit/managed/devkit
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
    test -d .devkit/managed/devkit
    echo "--- devkit rules check"
    uv run devkit rules check
    echo "--- exit codes: a usage error is 2"
    status=0
    uv run devkit rules check --no-such-option 2>/dev/null || status=$?
    test "$status" -eq 2
    echo "--- devkit workflow --help / devkit gate --help"
    uv run devkit workflow --help >/dev/null
    uv run devkit gate --help >/dev/null
    echo "--- devkit gate install, then commits through the hooks"
    git init -q -b main .
    git config user.email smoke@example.com
    git config user.name "devkit smoke"
    git config commit.gpgsign false
    printf '.venv/\n' > .gitignore
    uv run devkit gate install
    uv run devkit gate status --format json | grep -q '"state": "managed"'
    git add -A
    git commit -q -m "chore: smoke commit through devkit gate"
    if git commit -q --allow-empty --allow-empty-message -m "" 2>/dev/null; then
        echo "error: the commit-msg gate accepted an empty message" >&2
        exit 1
    fi
    echo "--- devkit worktree: start sets up and syncs a fresh checkout, its commits pass the gates, finish merges"
    uv run devkit add authoring >/dev/null
    cat >> .devkit/config.toml <<'TOML'

[gates.settings.verify-commands]
commands = ["uv run devkit rules check --staged"]

[worktree]
pull_request = false
setup = "uv sync --quiet"
TOML
    git add -A
    git commit -q -m "chore: verify commits with devkit rules"
    uv run devkit worktree start smoke-task | grep -q 'created=yes setup="uv sync --quiet" synced=yes'
    task="../$(basename "$PWD")-wt-smoke-task"
    test -d "$task/.devkit/managed/authoring" && test -x "$task/.venv/bin/python"
    printf 'task\n' > "$task/task.md"
    git -C "$task" add task.md
    git -C "$task" commit -q -m "docs: smoke task in a worktree"
    uv run devkit worktree finish smoke-task --merge | grep -q 'merged=yes push=no-upstream removed=yes branch_deleted=yes'
    test ! -e "$task" && test -f task.md
    uv run devkit gate uninstall >/dev/null
    test ! -e .git/hooks/pre-commit
    echo "--- dense search with the model wheel (numpy and tokenizers from the index)"
    uv add --dev "$model_wheel" numpy tokenizers >/dev/null
    uv run python -c "
from devkit.search import SearchDocument, SearchIndex, SearchMode, load_embedder
assert load_embedder().dimensions == 256
index = SearchIndex([SearchDocument('secrets', 'Secrets must not enter the repository'), SearchDocument('length', 'File length warning')])
assert index.search('leaked credentials', mode=SearchMode.HYBRID)[0].id == 'secrets'
"
)
echo "==> smoke passed"
