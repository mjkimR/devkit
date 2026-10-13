#!/usr/bin/env bash
# Consumer smoke test: build every workspace package into wheels, install the
# devkit wheel (with the devkit-advisory wheel it requires) and the starter
# content wheel into a fresh project the way a consumer would, verify the built-in bundles are deployed by default, select the
# starter bundle, verify the workspace converges, exercise every CLI group, run
# deployed and built-in rule tests, and make real commits through the installed
# gate hooks in a fresh Git repository;
# add the released model wheel and run a dense search;
# then install the devkit-advisory wheel alone, as a runtime dependency, and
# verify it brings devkit.advisory and nothing else of devkit.
# The wheels are installed by path, so a same-named package on an index can never
# be picked instead. Runs locally via `just smoke` and in CI; needs `uv` and `git`
# on PATH and network access for third-party dependencies (click, pyyaml, tomlkit)
# and the model wheel unless the uv cache is warm.
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
model_url=$(model_wheel_url)
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
devkit_wheel=$(wheel agt_devkit)
advisory_wheel=$(wheel devkit_advisory)
starter_wheel=$(wheel devkit_starter)

echo "==> creating a fresh consumer project"
(
    cd "$project"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-consumer --no-workspace >/dev/null
    uv add --dev "$devkit_wheel" "$advisory_wheel" "$starter_wheel" >/dev/null
    echo "--- devkit --version"
    uv run devkit --version
    uv run python -c "
from importlib.metadata import PackageNotFoundError, version
from devkit.distribution.installation.discovery import discover_bundles
from devkit.distribution.installation.sync import tool_identity
assert tool_identity().package == 'agt-devkit'
assert tool_identity().version == version('agt-devkit')
try:
    version('devkit')
except PackageNotFoundError:
    pass
else:
    raise AssertionError('the unrelated devkit distribution must not be installed')
with discover_bundles() as bundles:
    assert {item.bundle.name for item in bundles if item.builtin} == {'devkit', 'advisory', 'authoring', 'git-commits'}
    assert all(item.package == 'agt-devkit' for item in bundles if item.builtin)
"
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
    echo "--- fresh clone: devkit sync --locked restores the ignored managed copies"
    rm -rf .devkit/managed
    uv run devkit sync --locked >/dev/null
    test -d .devkit/managed/devkit
    uv run devkit sync --check >/dev/null
    echo "--- devkit rules check"
    uv run devkit rules check
    echo "--- exit codes: a usage error is 2"
    status=0
    uv run devkit rules check --no-such-option 2>/dev/null || status=$?
    test "$status" -eq 2
    echo "--- devkit workflow --help / devkit gate --help"
    uv run devkit workflow --help >/dev/null
    uv run devkit gate --help >/dev/null
    echo "--- devkit sync installs hooks, then commits through them"
    git init -q -b main .
    git config user.email smoke@example.com
    git config user.name "devkit smoke"
    git config commit.gpgsign false
    printf '.venv/\n' > .gitignore
    uv run devkit sync
    test -x .git/hooks/pre-commit.d/20-devkit
    test -d .git/hooks/post-commit.d && test ! -e .git/hooks/post-commit.d/20-devkit
    # Output is captured before grep: `cmd | grep -q` closes the pipe at the first match, and devkit exits 2
    # without output when its stdout is closed (BrokenPipeError), which pipefail turns into a failure.
    gate_status=$(uv run devkit gate status --format json)
    grep -q '"state": "managed"' <<<"$gate_status"
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
    started=$(uv run devkit worktree start smoke-task)
    grep -q 'created=yes setup="uv sync --quiet" synced=yes' <<<"$started"
    task="../$(basename "$PWD")-wt-smoke-task"
    test -d "$task/.devkit/managed/authoring" && test -x "$task/.venv/bin/python"
    printf 'task\n' > "$task/task.md"
    git -C "$task" add task.md
    git -C "$task" commit -q -m "docs: smoke task in a worktree"
    finished=$(uv run devkit worktree finish smoke-task --merge)
    grep -q 'merged=yes push=no-upstream removed=yes branch_deleted=yes' <<<"$finished"
    test ! -e "$task" && test -f task.md
    uv run devkit gate uninstall >/dev/null
    test ! -e .git/hooks/pre-commit
    echo "--- devkit rules test: without pytest RULES_TEST_UNAVAILABLE (exit 2); with it the deployed and built-in tests pass"
    status=0
    uv run devkit rules test RULE-markdown-link >/dev/null 2>"$work/rules-test.err" || status=$?
    test "$status" -eq 2 && grep -q RULES_TEST_UNAVAILABLE "$work/rules-test.err"
    uv add --dev pytest >/dev/null
    tested=$(uv run devkit rules test RULE-skill-document-size RULE-agent-guide-size RULE-markdown-link)
    grep -q 'RULE_TEST: RULE-skill-document-size tests=.devkit/managed/authoring/rules/skill_document_size/tests result=passed' <<<"$tested"
    grep -q 'RULE_TEST: RULE-markdown-link tests=.*/site-packages/devkit/rules/rules/markdown_link/tests result=passed' <<<"$tested"
    grep -q 'SUMMARY: rules=3 passed=3 failed=0 no_tests=0' <<<"$tested"
    test -z "$(find .devkit -name __pycache__ -o -name .pytest_cache)"
    echo "--- dense search with the released model wheel (numpy and tokenizers from the index)"
    uv add --dev "devkit-embed @ $model_url" numpy tokenizers >/dev/null
    uv run python -c "
from devkit.search import SearchDocument, SearchIndex, SearchMode, load_embedder
assert load_embedder().dimensions == 256
index = SearchIndex([SearchDocument('secrets', 'Secrets must not enter the repository'), SearchDocument('length', 'File length warning')])
assert index.search('leaked credentials', mode=SearchMode.HYBRID)[0].id == 'secrets'
"
)

echo "==> runtime-only consumer: the devkit-advisory wheel alone"
runtime="$work/runtime"
mkdir -p "$runtime"
(
    cd "$runtime"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-runtime --no-workspace >/dev/null
    uv add "$advisory_wheel" >/dev/null
    uv run python -c "
import importlib.util
from devkit.advisory import AdvisoryError, Level
assert AdvisoryError('x', code='SMOKE').to_dict()['code'] == 'SMOKE' and Level.NOTICE
assert importlib.util.find_spec('devkit.cli') is None and importlib.util.find_spec('devkit.core') is None
"
    test ! -e .venv/bin/devkit
)
echo "==> smoke passed"
