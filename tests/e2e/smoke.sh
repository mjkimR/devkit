#!/usr/bin/env bash
# Consumer smoke test: build every workspace package into wheels; install the
# devkit-dist wheel alone (with devkit-advisory) into a fresh project and verify
# it syncs distribution guidance only, answers harness command names and assets
# no engine runs with their codes, and owns the one devkit executable; install
# devkit-dist and devkit-agt as a uv tool and run a harness command; install the
# devkit-agt wheel (with the devkit-dist and devkit-advisory wheels it requires), the starter and
# catalog content wheels into a fresh project the way a consumer would, verify the built-in bundles are deployed by default
# and the catalog bundles are not, select the starter and a catalog bundle, verify the workspace converges, exercise every CLI group, run
# deployed and built-in rule tests, and make real commits through the installed
# gate hooks in a fresh Git repository;
# add the released model wheel and run a dense search;
# install the spec wheel and verify its command mount, opt-in docs seed and document index;
# install the viewer wheel, serve the consumer project and fetch its bundled page;
# then install the devkit-advisory wheel alone, as a runtime dependency, and
# verify it brings devkit.advisory and nothing else of devkit.
# The wheels are installed by path, so a same-named package on an index can never
# be picked instead. Runs locally via `just smoke` and in CI; needs `uv` and `git`
# on PATH and network access for third-party dependencies (click, pyyaml, tomlkit)
# and the model wheel unless the uv cache is warm.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source ./scripts/_lib.sh
source_root=$PWD

work=$(mktemp -d "${TMPDIR:-/tmp}/devkit-smoke.XXXXXX")
trap 'rm -rf "$work"' EXIT
dist="$work/dist"
project="$work/consumer"
mkdir -p "$dist" "$project"

# Assigned before the loop so a discovery failure aborts under `set -e`.
modules=$(list_modules)
model_wheel=$(readlink -f "$(model_wheel_path)")
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
core_wheel=$(wheel devkit_core)
cli_wheel=$(wheel devkit_cli)
dist_wheel=$(wheel devkit_dist)
devkit_wheel=$(wheel devkit_agt)
advisory_wheel=$(wheel devkit_advisory)
starter_wheel=$(wheel devkit_starter)
catalog_wheel=$(wheel devkit_catalog)
mcp_wheel=$(wheel devkit_mcp)
docs_wheel=$(wheel devkit_docs)
spec_wheel=$(wheel devkit_spec)
viewer_wheel=$(wheel devkit_viewer)

echo "==> foundation-only consumer: no CLI or application packages"
foundation="$work/foundation"
uv venv "$foundation" >/dev/null
uv pip install --python "$foundation/bin/python" "$core_wheel" "$advisory_wheel" pytest >/dev/null
"$foundation/bin/python" -c '
import importlib.util
from devkit_core.core import Deadline, run_git
from devkit_core.base.mcp import McpTool
assert importlib.util.find_spec("devkit_dist") is None
assert importlib.util.find_spec("devkit_agt") is None
assert importlib.util.find_spec("devkit_dist") is None
assert importlib.util.find_spec("click") is None
assert importlib.util.find_spec("mcp") is None
'
"$foundation/bin/python" -m pytest -c packages/devkit-core/pyproject.toml --rootdir packages/devkit-core \
    -p no:cacheprovider packages/devkit-core/tests -q

echo "==> toolkit-only consumer: a click tool on devkit-cli, without devkit-dist"
toolkit="$work/toolkit"
uv venv "$toolkit" >/dev/null
uv pip install --python "$toolkit/bin/python" "$cli_wheel" "$advisory_wheel" >/dev/null
cat > "$work/toolkit_tool.py" <<'PY'
import importlib.util
import click
from devkit.advisory import AdvisoryError
from devkit_cli import FORMAT_OPTION, Boundary

assert importlib.util.find_spec("devkit_dist") is None and importlib.util.find_spec("devkit_core") is None

@click.command()
@FORMAT_OPTION
@Boundary("smoketool")
def main(output_format: str) -> None:
    raise AdvisoryError("nothing to do", code="SMOKE_FAILED")

main()
PY
status=0
toolkit_out=$("$toolkit/bin/python" "$work/toolkit_tool.py" --format json 2>"$work/toolkit.err") || status=$?
[ "$status" -eq 2 ] || { echo "error: the toolkit tool exited $status, expected 2" >&2; exit 1; }
grep -Eq '"code": ?"SMOKE_FAILED"' <<<"$toolkit_out" || { echo "error: the toolkit tool printed no JSON error" >&2; exit 1; }
[ ! -s "$work/toolkit.err" ] || { echo "error: the toolkit tool wrote stderr in JSON mode" >&2; exit 1; }

echo "==> distribution-only consumer: the devkit-dist wheel without devkit-agt"
standalone="$work/standalone"
mkdir -p "$standalone"
(
    cd "$standalone"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-standalone --no-workspace >/dev/null
    uv add --no-build-package pyyaml --dev "$dist_wheel" "$core_wheel" "$cli_wheel" "$advisory_wheel" >/dev/null
    uv run python -c '
import yaml
from devkit_core.core import YamlBindingUnavailableError, safe_load
assert hasattr(yaml, "CSafeLoader")
del yaml.CSafeLoader
try:
    safe_load("key: value")
except YamlBindingUnavailableError as exc:
    assert exc.code == "YAML_BINDING_UNAVAILABLE"
else:
    raise AssertionError("missing LibYAML binding was not reported")
'
    uv run devkit --version
    uv run python -c "
import importlib.util
from importlib.metadata import entry_points, version
assert importlib.util.find_spec('devkit_agt') is None
assert [entry.dist.name for entry in entry_points(group='console_scripts', name='devkit')] == ['devkit-dist']
assert [entry.name for entry in entry_points(group='devkit.commands')] == []
"
    help_text=$(uv run devkit --help)
    for name in rules workflow gate worktree generated integration run; do
        if grep -qE "^  $name( |$)" <<<"$help_text"; then
            echo "error: devkit --help lists the harness command $name without devkit-agt" >&2
            exit 1
        fi
        status=0
        uv run devkit "$name" --help >/dev/null 2>"$work/harness-$name.err" || status=$?
        # Each condition is its own statement: errexit ignores a failure inside an && list.
        [ "$status" -eq 2 ] || { echo "error: devkit $name exited $status without devkit-agt, expected 2" >&2; exit 1; }
        grep -q HARNESS_COMMAND_UNAVAILABLE "$work/harness-$name.err"
    done
    status=0
    out=$(uv run devkit rules check --format json 2>"$work/harness-json.err") || status=$?
    [ "$status" -eq 2 ] || { echo "error: devkit rules --format json exited $status, expected 2" >&2; exit 1; }
    [ ! -s "$work/harness-json.err" ] || { echo "error: devkit rules --format json wrote to stderr" >&2; exit 1; }
    grep -Eq '"code": ?"HARNESS_COMMAND_UNAVAILABLE"' <<<"$out"
    status=0
    uv run devkit no-such-command >/dev/null 2>"$work/unknown.err" || status=$?
    [ "$status" -eq 2 ] || { echo "error: devkit no-such-command exited $status, expected 2" >&2; exit 1; }
    if grep -q HARNESS_COMMAND_UNAVAILABLE "$work/unknown.err"; then
        echo "error: an unknown command name answered with HARNESS_COMMAND_UNAVAILABLE" >&2
        exit 1
    fi
    echo "--- devkit sync deploys only the distribution bundles"
    uv run devkit sync >/dev/null
    uv run python -c '
import json, pathlib
receipt = json.loads(pathlib.Path(".devkit/installation.json").read_text())
assert receipt["tool"]["package"] == "devkit-dist", receipt["tool"]
assert {item["bundle"]: item["package"] for item in receipt["packages"]} == {"advisory": "devkit-dist", "devkit": "devkit-dist"}
'
    test ! -e .devkit/managed/harness
    context=$(uv run devkit get-context devkit)
    for command in "devkit rules" "devkit gate" "devkit workflow" "devkit run"; do
        if grep -q "$command" <<<"$context" || grep -rq "$command" .devkit/managed/devkit; then
            echo "error: the devkit bundle names $command in a standalone installation" >&2
            exit 1
        fi
    done
    echo "--- a rule asset no engine runs: HARNESS_ENGINE_MISSING, deployed, exit 0"
    uv run devkit add advisory:python >/dev/null 2>"$work/engine.err"
    grep -q HARNESS_ENGINE_MISSING "$work/engine.err"
    test -f .devkit/managed/advisory/rules/unique_code/rule.py
    engine_status=$(uv run devkit status)
    grep -Eq '"code": ?"HARNESS_ENGINE_MISSING"' <<<"$engine_status"
)

echo "==> tool installation: devkit-dist owns the executable, devkit-agt adds the harness"
(
    unset VIRTUAL_ENV
    export UV_TOOL_DIR="$work/tools" UV_TOOL_BIN_DIR="$work/tool-bin"
    uv tool install "$dist_wheel" --no-build-package pyyaml --with "$devkit_wheel" --with "$core_wheel" --with "$cli_wheel" --with "$advisory_wheel" >/dev/null 2>&1
    "$work/tool-bin/devkit" --version
    "$work/tool-bin/devkit" rules --help >/dev/null
    "$work/tool-bin/devkit" run --help >/dev/null
)

echo "==> creating a fresh consumer project"
(
    cd "$project"
    unset VIRTUAL_ENV
    uv init --bare --name smoke-consumer --no-workspace >/dev/null
    uv add --no-build-package pyyaml --dev "$devkit_wheel" "$dist_wheel" "$core_wheel" "$cli_wheel" "$advisory_wheel" "$starter_wheel" "$catalog_wheel" >/dev/null
    uv run python -c '
import yaml
from devkit_core.core import YamlBindingUnavailableError, safe_load
assert hasattr(yaml, "CSafeLoader")
del yaml.CSafeLoader
try:
    safe_load("key: value")
except YamlBindingUnavailableError as exc:
    assert exc.code == "YAML_BINDING_UNAVAILABLE"
else:
    raise AssertionError("missing LibYAML binding was not reported")
'
    echo "--- devkit --version"
    uv run devkit --version
    uv run python -c "
from importlib.metadata import PackageNotFoundError, version
from devkit_dist.features.distribution.services.installation.discovery import discover_bundles
from devkit_dist.features.distribution.usecases.sync import tool_identity
from importlib.metadata import entry_points
assert tool_identity().package == 'devkit-dist'
assert tool_identity().version == version('devkit-dist') == version('devkit-agt')
assert [entry.dist.name for entry in entry_points(group='console_scripts', name='devkit')] == ['devkit-dist']
try:
    version('devkit')
except PackageNotFoundError:
    pass
else:
    raise AssertionError('the unrelated devkit distribution must not be installed')
with discover_bundles() as bundles:
    assert {item.bundle.name: item.package for item in bundles if item.builtin} == {
        'devkit': 'devkit-dist', 'advisory': 'devkit-dist', 'git-commits': 'devkit-dist',
        'authoring': 'devkit-agt', 'harness': 'devkit-agt',
    }
    assert {item.bundle.name for item in bundles if item.package == 'devkit-catalog'} == {'response-style', 'maintenance', 'cli-tool'}
"
    echo "--- devkit sync (built-in bundles are selected by default)"
    uv run devkit sync >/dev/null
    grep -q '"devkit"' .devkit/installation.json
    grep -q '"advisory"' .devkit/installation.json
    grep -q '"harness"' .devkit/installation.json
    test -d .devkit/managed/devkit
    test -f .devkit/managed/harness/instructions/devkit-run.md
    test ! -e .devkit/managed/response-style
    test ! -e .devkit/managed/cli-tool
    echo "--- response templates: lazy imports, configured language and final output"
    uv run python -c '
import sys
from devkit_dist.features.distribution.services.installation.discovery import discover_bundles
with discover_bundles() as bundles:
    assert any(item.bundle.name == "response-style" for item in bundles)
assert "jinja2" not in sys.modules
'
    cat >> .devkit/config.toml <<'TOML'

[bundles.response-style.variables]
language = "ko"
TOML
    uv run devkit add response-style >/dev/null
    uv run python -c '
from pathlib import Path
path = Path(".devkit/managed/response-style/skills/response-style/SKILL.md")
text = path.read_text()
assert "Use ko as the default" in text
assert "→ **Core sentence.** Supporting explanation." in text
assert "Required user and workflow formats take precedence" in text
assert not path.with_suffix(".md.jinja").exists()
assert "read and apply the `response-style` skill" in Path("AGENTS.md").read_text()
'
    uv run devkit sync --check >/dev/null
    uv run devkit remove response-style >/dev/null
    echo "--- cli-tool: the structure rules load from the installed catalog and check a tool"
    uv run devkit add cli-tool >/dev/null
    mkdir -p src/smoketool
    printf 'import click\nimport httpx\n\n\n@click.command()\ndef main():\n    print("x")\n' > src/smoketool/cli.py
    printf 'import click\n' > src/smoketool/usecases.py
    status=0
    uv run devkit rules check --format json src/smoketool/cli.py src/smoketool/usecases.py >"$work/cli-tool.json" 2>/dev/null || status=$?
    [ "$status" -eq 1 ] || { echo "error: devkit rules check exited $status on the cli-tool sample, expected 1" >&2; exit 1; }
    uv run python - "$work/cli-tool.json" <<'PY'
import json, sys
found = {item["rule_id"] for item in json.load(open(sys.argv[1]))["violations"]}
expected = {
    "RULE-cli-tool-command-boundary", "RULE-cli-tool-library-output", "RULE-cli-tool-heavy-imports",
    "RULE-cli-tool-layout", "RULE-cli-tool-layers",
}
assert expected <= found, found
PY
    rm -r src/smoketool
    uv run devkit remove cli-tool >/dev/null
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
    echo "--- every harness command group is mounted under devkit"
    for name in rules workflow gate worktree generated integration run; do
        uv run devkit "$name" --help >/dev/null
    done
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
    grep -Eq '"state": ?"managed"' <<<"$gate_status"
    git add -A
    git commit -q -m "chore: smoke commit through devkit gate"
    if git commit -q --allow-empty --allow-empty-message -m "" 2>/dev/null; then
        echo "error: the commit-msg gate accepted an empty message" >&2
        exit 1
    fi
    echo "--- devkit worktree: start sets up and syncs a fresh checkout, its commits pass the gates, finish merges"
    uv run devkit add authoring >/dev/null
    cat >> .devkit/config.toml <<'TOML'

[worktree]
pull_request = "auto"
setup = "uv sync --quiet"
TOML
    git add -A
    git commit -q -m "chore: verify commits with devkit rules"
    started=$(uv run devkit worktree start dev-smoke-task)
    grep -q 'created=yes existing=no unit=- setup="uv sync --quiet" synced=yes' <<<"$started"
    task="../$(basename "$PWD")-wt-dev-smoke-task"
    test -d "$task/.devkit/managed/authoring" && test -x "$task/.venv/bin/python"
    printf 'task\n' > "$task/task.md"
    git -C "$task" add task.md
    git -C "$task" commit -q -m "docs: smoke task in a worktree"
    finished=$(uv run devkit worktree finish dev-smoke-task --merge)
    grep -q 'merged=yes push=no-upstream removed=yes branch_deleted=yes' <<<"$finished"
    test ! -e "$task" && test -f task.md
    echo "--- optional MCP runtime: absent command, installed transport integrates a Git fixture"
    status=0
    uv run devkit mcp --help >/dev/null 2>"$work/mcp-extra.err" || status=$?
    test "$status" -eq 2
    uv add --dev "$mcp_wheel" 'devkit-agt[mcp]' >/dev/null
    uv run python "$source_root/tests/e2e/smoke_integration.py" "$work"
    uv run devkit gate uninstall >/dev/null
    test ! -e .git/hooks/pre-commit
    echo "--- devkit rules test: without pytest RULES_TEST_UNAVAILABLE (exit 2); with it the deployed and built-in tests pass"
    status=0
    uv run devkit rules test RULE-markdown-link >/dev/null 2>"$work/rules-test.err" || status=$?
    test "$status" -eq 2 && grep -q RULES_TEST_UNAVAILABLE "$work/rules-test.err"
    uv add --dev pytest >/dev/null
    tested=$(uv run devkit rules test RULE-skill-document-size RULE-agent-guide-size RULE-markdown-link)
    grep -q 'RULE_TEST: RULE-skill-document-size tests=.devkit/managed/authoring/rules/skill_document_size/tests result=passed' <<<"$tested"
    grep -q 'RULE_TEST: RULE-markdown-link tests=.*/site-packages/devkit_agt/features/rules/services/builtins/markdown_link/tests result=passed' <<<"$tested"
    grep -q 'SUMMARY: rules=3 passed=3 failed=0 no_tests=0' <<<"$tested"
    test -z "$(find .devkit -name __pycache__ -o -name .pytest_cache)"
    echo "--- dense search with the committed model wheel (numpy and tokenizers from the index)"
    uv add --dev "devkit-embed @ $model_wheel" numpy tokenizers >/dev/null
    uv run python -c "
from devkit_dist.features.search import SearchDocument, SearchIndex, SearchMode, load_embedder
assert load_embedder().dimensions == 256
index = SearchIndex([SearchDocument('secrets', 'Secrets must not enter the repository'), SearchDocument('length', 'File length warning')])
assert index.search('leaked credentials', mode=SearchMode.HYBRID)[0].id == 'secrets'
"
    echo "--- SDD extension: install its wheels, mount the commands and opt into valid docs"
    uv add --dev "$spec_wheel" "$docs_wheel" >/dev/null
    uv run devkit spec --version
    uv run devkit docs --version
    uv run devkit sync >/dev/null
    test ! -e docs
    test -f .devkit/managed/spec/bundle.toml
    uv run devkit add spec:docs-skeleton >/dev/null
    uv run python -c '
from pathlib import Path
from devkit_docs.features.documents import DocumentIndex
index = DocumentIndex.load(Path.cwd())
assert not index.problems, index.problems
for document_id in (
    "ARCH-01-introduction-and-goals", "ARCH-03-context", "ARCH-05-1-containers",
    "ARCH-05-2-components", "ARCH-06-runtime-view", "ARCH-07-deployment", "ARCH-08-cross-cutting",
):
    assert index.resolve(document_id).path == f"docs/architecture/{document_id}.md"
'
    uv run devkit docs resolve ARCH-03-context ARCH-07-deployment ARCH-08-cross-cutting >/dev/null
    uv run devkit sync --check >/dev/null
    uv run devkit rules check
    echo "--- viewer: install its wheel, serve this project and fetch the bundled page"
    uv add --dev "$viewer_wheel" >/dev/null
    uv run devkit viewer --version
    uv run python - <<'PY'
import re, subprocess, sys, urllib.request
server = subprocess.Popen([sys.executable, "-P", "-m", "devkit_dist", "viewer", "serve", "--port", "0"], stdout=subprocess.PIPE, text=True)
try:
    line = server.stdout.readline().strip()
    match = re.fullmatch(r"\[VIEWER: url=(http://127\.0\.0\.1:\d+/) repos=1\]", line)
    assert match, line
    url = match[1]
    page = urllib.request.urlopen(url, timeout=10).read().decode()
    script = re.search(r'src="\./([^"]+\.js)"', page)[1]
    with urllib.request.urlopen(url + script, timeout=10) as response:
        assert response.headers["Content-Type"].startswith("text/javascript")
    repos = urllib.request.urlopen(url + "api/repos", timeout=10).read()
    assert b'"id": "consumer"' in repos, repos
finally:
    server.terminate()
    server.wait(timeout=10)
assert server.returncode == 0, server.returncode
PY
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
assert importlib.util.find_spec('devkit_dist') is None and importlib.util.find_spec('devkit_agt') is None
"
    test ! -e .venv/bin/devkit
)
echo "==> smoke passed"
