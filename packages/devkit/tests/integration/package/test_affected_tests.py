"""`just test-affected` selects the tests a change can affect and hands them to the module script."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from click.testing import CliRunner
from devkit.advisory import AdvisoryError

ROOT = Path(__file__).resolve().parents[5]
TESTS = "packages/devkit/tests"
DIST_TESTS = "packages/devkit-dist/tests"


@pytest.fixture(scope="module")
def affected() -> ModuleType:
    spec = importlib.util.spec_from_file_location("affected_tests", ROOT / "scripts/affected_tests.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["affected_tests"] = module  # dataclasses resolve their module while the class is created
    spec.loader.exec_module(module)
    return module


def test_a_change_selects_its_area_and_the_areas_that_import_it(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py"])
    assert selection.mode == "partial"
    assert selection.reason == "devkit_agt.features.worktree"
    assert {
        f"{TESTS}/integration/features/worktree/test_lifecycle.py",
        "packages/devkit-spec/tests/integration/features/delivery/test_integration.py",
    } <= set(selection.paths)
    assert not any(path.startswith(f"{TESTS}/integration/features/gate/") for path in selection.paths)


def test_a_leaf_area_selects_no_unrelated_area(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit/src/devkit_agt/features/gate/usecases/runner.py"])
    assert selection.mode == "partial"
    assert f"{TESTS}/integration/features/gate/test_hooks.py" in selection.paths
    assert not any(
        path.startswith(
            (
                f"{TESTS}/integration/features/worktree/",
                f"{TESTS}/integration/features/integration/",
                f"{DIST_TESTS}/integration/features/distribution/",
            )
        )
        for path in selection.paths
    )
    assert set(affected.SOURCE_TREE_TESTS) <= set(selection.paths)
    assert (
        f"{DIST_TESTS}/integration/adapters/test_cli.py" in selection.paths
    )  # scans every source file for stdout kinds


def test_a_devkit_dist_area_selects_the_devkit_agt_areas_that_import_it(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit-dist/src/devkit_dist/features/host/services/configuration.py"])
    assert selection.mode == "partial"
    assert selection.reason == "devkit_dist.features.host"
    assert {
        f"{DIST_TESTS}/integration/features/host/test_hooks.py",
        "packages/devkit-spec/tests/integration/features/delivery/test_integration.py",
    } <= set(selection.paths)
    assert set(affected.SOURCE_TREE_TESTS) <= set(selection.paths)


def test_a_devkit_dist_helper_carries_its_dependencies(affected: ModuleType) -> None:
    # tests/distribution imports distsupport.distribution at module level.
    selection = affected.select(
        ROOT, ["packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/engines.py"]
    )
    assert any(path.startswith(f"{DIST_TESTS}/integration/features/distribution/test_") for path in selection.paths)


def test_a_shared_helper_imported_at_module_level_carries_its_dependencies(affected: ModuleType) -> None:
    # tests/workflow imports testsupport.gate at module level, which imports devkit_agt.features.gate.
    selection = affected.select(ROOT, ["packages/devkit/src/devkit_agt/features/gate/usecases/runner.py"])
    assert f"{TESTS}/integration/features/workflow/test_hygiene_authoring.py" in selection.paths


@pytest.mark.parametrize(
    "path",
    [
        "packages/devkit-core/src/devkit_core/core/git.py",
        "packages/devkit-dist/src/devkit_dist/adapters/cli.py",
        "packages/devkit-advisory/src/devkit/advisory/error.py",
        "packages/devkit-dist/src/devkit_dist/cli.py",
        "packages/devkit-dist/src/devkit_dist/__main__.py",
        "packages/devkit-spec/pyproject.toml",
        "pyproject.toml",
        "uv.lock",
        "packages/devkit-spec/tests/conftest.py",
        "packages/devkit/tests/support/testsupport/gate.py",
        "packages/devkit-dist/tests/support/distsupport/distribution.py",
    ],
)
def test_shared_foundations_select_the_full_suite(affected: ModuleType, path: str) -> None:
    selection = affected.select(ROOT, ["docs/README.md", path])
    assert (selection.mode, selection.paths, selection.reason) == ("full", (), path)


def test_an_unmapped_path_selects_the_full_suite(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["new-directory/tool.py", "specs/x.md"])
    assert (selection.mode, selection.reason) == ("full", "new-directory/tool.py")


@pytest.mark.parametrize(
    "path", ["specs/2026-10/x/spec.md", ".claude/skills/x/SKILL.md", ".agents/skills/x.md", "guides/install.md"]
)
def test_files_no_test_reads_select_nothing(affected: ModuleType, path: str) -> None:
    selection = affected.select(ROOT, [path, "README.md", "packages/devkit-spec/README.md"])
    assert (selection.mode, selection.paths, selection.reason) == ("none", (), "untested")


def test_docs_select_the_tests_that_read_them(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["docs/capabilities/gate/CAP-GATE-commit-gates.md"])
    assert selection.paths == tuple(
        sorted(
            (
                "packages/devkit-spec/tests/integration/package/test_documented_codes.py",
                f"{TESTS}/integration/features/rules/test_docs.py",
                f"{TESTS}/integration/package/test_documented_codes.py",
                f"{TESTS}/integration/features/workflow/test_library.py",
            )
        )
    )


def test_architecture_config_alone_selects_structure_rule_and_integration_tests(affected: ModuleType) -> None:
    selection = affected.select(ROOT, [".devkit/architecture.toml"])
    assert selection.mode == "partial"
    assert selection.reason == ".devkit/architecture.toml"
    assert selection.paths == (
        "tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/tests",
        "tools/devkit-dev/tests",
    )
    assert (ROOT / "tools/devkit-dev/tests/integration/test_architecture.py").is_file()
    assert affected.select(ROOT, [".devkit/config.toml"]).mode == "none"


def test_changed_tests_select_themselves_and_helpers_their_directory(affected: ModuleType) -> None:
    selection = affected.select(
        ROOT,
        [
            "packages/devkit-spec/tests/integration/features/scope/fixture.json",
            f"{TESTS}/integration/features/gate/test_hooks.py",
            f"{TESTS}/integration/features/gate/test_deleted_meanwhile.py",
        ],
    )
    assert selection.paths == (
        "packages/devkit-spec/tests/integration/features/scope",
        f"{TESTS}/integration/features/gate/test_hooks.py",
    )


def test_paths_inside_a_selected_directory_are_covered(affected: ModuleType) -> None:
    scope = "packages/devkit-spec/tests/integration/features/scope"
    selection = affected.select(ROOT, [f"{scope}/support.py", f"{scope}/test_flow.py"])
    assert selection.paths == (scope,)


def git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    command = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args]
    return subprocess.run(command, capture_output=True, text=True, check=True, env=env).stdout


def test_every_kind_of_change_is_collected(affected: ModuleType, tmp_path: Path) -> None:
    git(tmp_path, "init", "-q", "-b", "main")
    for name in ("kept", "renamed", "deleted", "staged", "unstaged"):
        (tmp_path / name).write_text(name)
    (tmp_path / ".gitignore").write_text("ignored\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "switch", "-q", "-c", "dev")
    (tmp_path / "committed").write_text("new")
    git(tmp_path, "mv", "renamed", "moved")
    git(tmp_path, "rm", "-q", "deleted")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "work")
    git(tmp_path, "switch", "-q", "main")
    (tmp_path / "main-only").write_text("later")
    git(tmp_path, "add", "main-only")
    git(tmp_path, "commit", "-q", "-m", "base moves on")
    git(tmp_path, "switch", "-q", "dev")
    (tmp_path / "staged").write_text("changed")
    git(tmp_path, "add", "staged")
    (tmp_path / "unstaged").write_text("changed")
    (tmp_path / "untracked").write_text("new")
    (tmp_path / "ignored").write_text("new")

    assert affected.changed_paths(tmp_path, "main") == [
        "committed",
        "deleted",
        "moved",
        "renamed",
        "staged",
        "unstaged",
        "untracked",
    ]


def test_an_unknown_base_is_refused(affected: ModuleType, tmp_path: Path) -> None:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "base")
    with pytest.raises(AdvisoryError) as raised:
        affected.changed_paths(tmp_path, "nosuch")
    assert raised.value.code == "TEST_BASE_UNKNOWN"
    assert raised.value.fix == "git branch --all --list"
    assert raised.value.input_error


def test_the_command_reports_an_unknown_base_and_runs_nothing() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/affected_tests.py"), "--base", "refs/heads/no-such-base-ref"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 2
    assert "[ERROR]" in result.stderr
    assert "TEST_BASE_UNKNOWN" in result.stderr
    assert result.stdout == ""


@pytest.fixture
def command(affected: ModuleType, monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Runs of the command record their hand-off instead of replacing the test process."""
    handed: list[list[str]] = []
    monkeypatch.setattr(affected, "_replace_process", handed.append)
    return handed


def invoke(affected: ModuleType, monkeypatch: pytest.MonkeyPatch, changed: list[str], *args: str) -> list[str]:
    monkeypatch.setattr(affected, "changed_paths", lambda root, base: changed)
    result = CliRunner().invoke(affected.main, list(args))
    assert result.exit_code == 0, result.output
    return result.output.splitlines()


def test_list_prints_the_selection_without_running(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    lines = invoke(affected, monkeypatch, ["docs/x.md"], "--list", "--base", "dev")
    assert lines[0] == "[TEST_SELECTION: mode=partial base=dev changed=1 paths=4 reason=docs/]"
    assert lines[1:] == [f"[TEST_PATH: {path}]" for path in affected.select(ROOT, ["docs/x.md"]).paths]
    assert command == []


def test_a_partial_selection_runs_its_paths_with_the_pytest_arguments(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    lines = invoke(affected, monkeypatch, ["scripts/module.sh"], "--", "-k", "foo", "-n0")
    assert lines == ["[TEST_SELECTION: mode=partial base=main changed=1 paths=1 reason=scripts/module.sh]"]
    script = str(ROOT / "scripts/module.sh")
    assert command == [
        ["bash", script, "test", "all", f"{TESTS}/integration/package/test_module_script.py", "-k", "foo", "-n0"]
    ]


def test_a_full_selection_runs_the_whole_suite(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    lines = invoke(affected, monkeypatch, ["uv.lock"], "-n0")
    assert lines == ["[TEST_SELECTION: mode=full base=main changed=1 paths=0 reason=uv.lock]"]
    assert command == [["bash", str(ROOT / "scripts/module.sh"), "test", "all", "-n0"]]


def test_an_empty_selection_runs_nothing(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    lines = invoke(affected, monkeypatch, ["specs/x.md"])
    assert lines == ["[TEST_SELECTION: mode=none base=main changed=1 paths=0 reason=untested]"]
    assert command == []


FRONTEND = "packages/devkit-viewer/frontend/src/lib/App.svelte"
FRONTEND_LINE = (
    "[FRONTEND_CHECK: just viewer install && just viewer lint && just viewer check && just viewer test"
    " && just viewer pack && just viewer build]"
)


@pytest.mark.parametrize("path", [FRONTEND, "scripts/viewer.sh"])
def test_a_frontend_only_change_runs_no_pytest(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]], path: str
) -> None:
    selection = affected.select(ROOT, [path])
    assert (selection.mode, selection.paths, selection.reason, selection.frontend) == ("none", (), "frontend", True)
    lines = invoke(affected, monkeypatch, [path])
    assert lines == ["[TEST_SELECTION: mode=none base=main changed=1 paths=0 reason=frontend]", FRONTEND_LINE]
    assert command == []


def test_a_mixed_change_keeps_the_other_selection(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    gate = "packages/devkit/src/devkit_agt/features/gate/usecases/runner.py"
    alone = affected.select(ROOT, [gate])
    mixed = affected.select(ROOT, [gate, FRONTEND])
    assert (mixed.mode, mixed.paths, mixed.frontend) == ("partial", alone.paths, True)
    assert mixed.reason == "devkit_agt.features.gate,frontend"
    lines = invoke(affected, monkeypatch, [gate, FRONTEND], "--list")
    assert lines[1] == FRONTEND_LINE
    assert lines[2:] == [f"[TEST_PATH: {path}]" for path in alone.paths]


def test_a_full_suite_change_still_names_the_frontend_checks(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    lines = invoke(affected, monkeypatch, [FRONTEND, "uv.lock"], "--list")
    assert lines == ["[TEST_SELECTION: mode=full base=main changed=2 paths=0 reason=uv.lock]", FRONTEND_LINE]


def test_other_changes_print_no_frontend_line(
    affected: ModuleType, monkeypatch: pytest.MonkeyPatch, command: list[list[str]]
) -> None:
    assert not affected.select(ROOT, ["packages/devkit/src/devkit_agt/features/gate/usecases/runner.py"]).frontend
    lines = invoke(affected, monkeypatch, ["docs/x.md"], "--list")
    assert not any(line.startswith("[FRONTEND_CHECK:") for line in lines)


def test_the_rebuilt_page_selects_the_viewer_tests(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit-viewer/src/devkit_viewer/static/index.html"])
    assert any(path.startswith("packages/devkit-viewer/tests/integration/") for path in selection.paths)
    assert not selection.frontend


@pytest.fixture
def graph_root(tmp_path: Path) -> Path:
    """Authored miniature workspace: expectations below do not derive from the selector graph."""
    files = {
        "packages/devkit/src/devkit_agt/features/gate/usecases/runner.py": "VALUE = 1\n",
        "packages/devkit/src/devkit_agt/features/workflow/runner.py": "VALUE = 2\n",
        "packages/devkit/tests/gate/test_owner.py": "def test_owner(): pass\n",
        "packages/devkit-spec/src/devkit_spec/__init__.py": "VERSION = 1\n",
        "packages/devkit-spec/src/devkit_spec/features/scope/__init__.py": "from .models.registry import register\n",
        "packages/devkit-spec/src/devkit_spec/features/scope/models/registry.py": "def register(): pass\n",
        "packages/devkit-spec/src/devkit_spec/features/documents.py": "VALUE = 3\n",
        "packages/devkit-spec/tests/test_scope.py": "from devkit_spec.features.scope import register\n",
        "packages/devkit-spec/tests/test_documents.py": "from devkit_spec.features.documents import VALUE\n",
        "packages/devkit-spec/tests/test_root.py": "import devkit_spec\n",
        "packages/devkit-spec/tests/test_cli.py": "from devkit_dist.cli import cli\n",
        "packages/devkit/tests/external/test_consumer.py": "import devkit_spec.features.scope.models.registry\n",
        "packages/devkit/tests/external/test_unrelated.py": "import devkit_spec.features.documents\n",
    }
    for name, content in files.items():
        put(tmp_path, name, content)
    return tmp_path


def put(root: Path, name: str, content: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


SCOPE_SOURCE = "packages/devkit-spec/src/devkit_spec/features/scope/models/registry.py"
SPEC_TESTS = "packages/devkit-spec/tests"


def test_fine_modules_and_reexports_isolate_external_siblings(affected: ModuleType, graph_root: Path) -> None:
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert selection.mode == "partial"
    assert set(selection.paths) == {
        f"{SPEC_TESTS}/test_scope.py",
        f"{SPEC_TESTS}/test_root.py",
        f"{SPEC_TESTS}/test_cli.py",
        f"{TESTS}/external/test_consumer.py",
    }
    assert f"{SPEC_TESTS}/test_documents.py" not in selection.paths
    assert f"{TESTS}/external/test_unrelated.py" not in selection.paths


@pytest.mark.parametrize("initializer", ["__init__.py", "features/scope/__init__.py"])
def test_executed_initializers_select_descendant_consumers(
    affected: ModuleType, graph_root: Path, initializer: str
) -> None:
    selection = affected.select(graph_root, [f"packages/devkit-spec/src/devkit_spec/{initializer}"])
    assert f"{SPEC_TESTS}/test_scope.py" in selection.paths
    assert (f"{SPEC_TESTS}/test_documents.py" in selection.paths) == (initializer == "__init__.py")


@pytest.mark.parametrize(
    "statement",
    [
        "from devkit_spec.features import scope",
        "from devkit_spec.features.scope.models import registry",
        "from devkit_spec.features.scope.models.registry import register",
        "from devkit_spec.features.scope import *",
        "import importlib; importlib.import_module('devkit_spec.features.scope.models.registry')",
        "import importlib.util; importlib.util.find_spec('devkit_spec.features.scope.models.registry')",
        "from importlib.resources import files; files('devkit_spec.features.scope')",
    ],
)
def test_import_forms_keep_required_consumers(affected: ModuleType, graph_root: Path, statement: str) -> None:
    put(graph_root, f"{SPEC_TESTS}/test_form.py", statement)
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert f"{SPEC_TESTS}/test_form.py" in selection.paths


def test_an_attribute_does_not_create_a_fabricated_module(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/test_attribute.py", "from devkit_spec import VERSION")
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert f"{SPEC_TESTS}/test_attribute.py" not in selection.paths
    assert "devkit_spec.VERSION" not in affected.Workspace(graph_root).imports(
        [graph_root / SPEC_TESTS / "test_attribute.py"]
    )


def test_relative_source_imports_and_cycles(affected: ModuleType, graph_root: Path) -> None:
    put(
        graph_root,
        "packages/devkit-spec/src/devkit_spec/bridge.py",
        "from .features.scope.models import registry\nfrom . import cycle",
    )
    put(graph_root, "packages/devkit-spec/src/devkit_spec/cycle.py", "from . import bridge")
    put(graph_root, f"{SPEC_TESTS}/test_bridge.py", "from devkit_spec.cycle import bridge")
    assert f"{SPEC_TESTS}/test_bridge.py" in affected.select(graph_root, [SCOPE_SOURCE]).paths


def test_transitive_function_local_helpers_and_cycles(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/helpers/__init__.py", "")
    put(graph_root, f"{SPEC_TESTS}/helpers/one.py", "def helper():\n    from helpers import two\n")
    put(
        graph_root,
        f"{SPEC_TESTS}/helpers/two.py",
        "from helpers import one\nimport devkit_spec.features.scope.models.registry",
    )
    put(graph_root, f"{SPEC_TESTS}/test_helper.py", "def test_helper():\n    from helpers.one import helper\n")
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert f"{SPEC_TESTS}/test_helper.py" in selection.paths
    assert f"{SPEC_TESTS}/test_documents.py" not in selection.paths


def test_conftest_only_applies_to_descendants(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/nested/conftest.py", "import devkit_spec.features.scope.models.registry")
    put(graph_root, f"{SPEC_TESTS}/nested/test_nested.py", "import devkit_spec.features.documents")
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert f"{SPEC_TESTS}/nested/test_nested.py" in selection.paths
    assert f"{SPEC_TESTS}/test_documents.py" not in selection.paths


def test_relative_helpers_and_ambiguous_pythonpath_are_conservative(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/nested/helper.py", "import devkit_spec.features.scope.models.registry")
    put(graph_root, f"{SPEC_TESTS}/nested/test_relative.py", "from .helper import value")
    put(graph_root, f"{SPEC_TESTS}/helper.py", "import devkit_spec.features.documents")
    put(graph_root, f"{TESTS}/helper.py", "import devkit_spec.features.scope.models.registry")
    put(graph_root, f"{SPEC_TESTS}/test_ambiguous.py", "from helper import value")
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert {f"{SPEC_TESTS}/nested/test_relative.py", f"{SPEC_TESTS}/test_ambiguous.py"} <= set(selection.paths)


@pytest.mark.parametrize("content", ["def broken(:", "from devkit_spec.features.scope import register\n\x00"])
def test_unparseable_source_selects_full(affected: ModuleType, graph_root: Path, content: str) -> None:
    put(graph_root, SCOPE_SOURCE, content)
    assert affected.select(graph_root, [SCOPE_SOURCE]).mode == "full"


def test_unparseable_imported_helper_selects_full(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/helper.py", "def broken(:")
    put(graph_root, f"{SPEC_TESTS}/test_helper.py", "import helper")
    assert affected.select(graph_root, [SCOPE_SOURCE]).mode == "full"


def test_deleted_renamed_or_unknown_source_selects_full(affected: ModuleType, graph_root: Path) -> None:
    (graph_root / SCOPE_SOURCE).unlink()
    put(graph_root, SCOPE_SOURCE.replace("registry", "renamed"), "VALUE = 1")
    assert affected.select(graph_root, [SCOPE_SOURCE, SCOPE_SOURCE.replace("registry", "renamed")]).mode == "full"
    assert affected.select(graph_root, ["packages/unknown/src/unknown.py"]).mode == "full"


def test_ambiguous_module_inventory_selects_full(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, "packages/devkit-spec/src/devkit_spec/features/scope.py", "")
    assert affected.select(graph_root, [SCOPE_SOURCE]).mode == "full"


def test_opaque_and_wildcard_consumers_remain_broad(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/test_dynamic.py", "import importlib\nimportlib.import_module(module)")
    put(graph_root, f"{SPEC_TESTS}/test_star.py", "from devkit_spec.features.documents import *")
    selection = affected.select(graph_root, [SCOPE_SOURCE])
    assert {f"{SPEC_TESTS}/test_dynamic.py", f"{SPEC_TESTS}/test_star.py"} <= set(selection.paths)


def test_fine_package_data_changes_cover_all_fine_tests(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, "packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/file.md", "data")
    selection = affected.select(graph_root, ["packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/file.md"])
    assert {f"{SPEC_TESTS}/test_scope.py", f"{SPEC_TESTS}/test_documents.py"} <= set(selection.paths)


def test_new_packages_and_embedded_rule_tests_keep_owner_coverage(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, "packages/new/src/new_package/mod.py", "")
    put(graph_root, "packages/devkit/src/devkit_agt/features/rules/services/builtins/rule.py", "")
    put(graph_root, "packages/new/tests/test_new.py", "def test_new(): pass")
    put(
        graph_root,
        "packages/devkit/src/devkit_agt/features/rules/services/builtins/rule/tests/test_rule.py",
        "def test_rule(): pass",
    )
    assert (
        "packages/new/tests/test_new.py" in affected.select(graph_root, ["packages/new/src/new_package/mod.py"]).paths
    )
    assert (
        "packages/devkit/src/devkit_agt/features/rules/services/builtins/rule/tests/test_rule.py"
        in affected.select(
            graph_root, ["packages/devkit/src/devkit_agt/features/rules/services/builtins/rule.py"]
        ).paths
    )


def test_mcp_runtime_consumer_mapping_is_retained(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit-mcp/src/devkit_mcp/features/runtime/mcp/server.py"])
    assert {
        "packages/devkit-mcp/tests",
        f"{TESTS}/integration/features/integration",
        f"{SPEC_TESTS}/integration/features/delivery/test_integration.py",
    } <= set(selection.paths)


def test_relative_helper_package_initializer_keeps_its_dependency(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, f"{SPEC_TESTS}/__init__.py", "")
    put(graph_root, f"{SPEC_TESTS}/helpers/__init__.py", "import devkit_spec.features.scope.models.registry")
    put(
        graph_root,
        f"{SPEC_TESTS}/test_package_helper.py",
        "import devkit_spec.features.documents\nfrom . import helpers",
    )
    assert f"{SPEC_TESTS}/test_package_helper.py" in affected.select(graph_root, [SCOPE_SOURCE]).paths


@pytest.mark.parametrize("consumer", [f"{SPEC_TESTS}/test_cli.py", f"{TESTS}/external/test_cli.py"])
def test_root_cli_coverage_survives_an_unrelated_fine_import(
    affected: ModuleType, graph_root: Path, consumer: str
) -> None:
    put(graph_root, consumer, "from devkit_dist.cli import cli\nimport devkit_spec.features.documents")
    assert consumer in affected.select(graph_root, [SCOPE_SOURCE]).paths


def test_independent_namespaces_do_not_merge_same_named_features(affected: ModuleType, graph_root: Path) -> None:
    put(graph_root, "packages/devkit/src/devkit_agt/features/shared/services/read.py", "VALUE = 1")
    put(graph_root, "packages/devkit-dist/src/devkit_dist/features/shared/services/read.py", "VALUE = 2")
    put(graph_root, f"{TESTS}/shared/test_owner.py", "import devkit_agt.features.shared.services.read")
    put(
        graph_root,
        f"{DIST_TESTS}/integration/features/shared/test_owner.py",
        "import devkit_dist.features.shared.services.read",
    )
    selection = affected.select(graph_root, ["packages/devkit/src/devkit_agt/features/shared/services/read.py"])
    assert selection.mode == "partial"
    assert f"{TESTS}/shared/test_owner.py" in selection.paths
    assert f"{DIST_TESTS}/integration/features/shared/test_owner.py" not in selection.paths


def test_tools_packages_and_embedded_bundle_tests_are_inventoried(affected: ModuleType, graph_root: Path) -> None:
    source = "tools/devkit-dev/src/devkit_dev/bundle/rules/layout/check.py"
    own_test = "tools/devkit-dev/tests/test_package.py"
    embedded_test = "tools/devkit-dev/src/devkit_dev/bundle/rules/layout/tests/test_check.py"
    put(graph_root, source, "VALUE = 1")
    put(graph_root, own_test, "def test_package(): pass")
    put(graph_root, embedded_test, "def test_check(): pass")
    selection = affected.select(graph_root, [source])
    assert selection.mode == "partial"
    assert {own_test, embedded_test} <= set(selection.paths)
    assert affected.select(graph_root, [own_test]).paths == (own_test,)
    assert affected.select(graph_root, ["tools/devkit-dev/README.md"]).mode == "none"


@pytest.mark.parametrize("home,namespace", [("devkit", "devkit_agt"), ("devkit-dist", "devkit_dist")])
def test_deleted_feature_source_selects_full(affected: ModuleType, graph_root: Path, home: str, namespace: str) -> None:
    source = f"packages/{home}/src/{namespace}/features/gate/services/deleted.py"
    put(graph_root, source, "VALUE = 1")
    (graph_root / source).unlink()
    assert affected.select(graph_root, [source]).mode == "full"


@pytest.mark.parametrize(
    "path",
    [
        "packages/devkit-spec/tests/support/spec_support/scope.py",
        "packages/devkit-viewer/tests/support/payload.json",
        "tools/devkit-dev/tests/support/config.toml",
    ],
)
def test_shared_support_changes_preserve_the_conservative_fallback(affected: ModuleType, path: str) -> None:
    assert affected.select(ROOT, [path]).mode == "full"


def test_category_feature_ownership_covers_tests_without_explicit_imports(
    affected: ModuleType, graph_root: Path
) -> None:
    own = f"{TESTS}/unit/features/gate/test_ownership.py"
    other = f"{TESTS}/integration/features/workflow/test_ownership.py"
    put(graph_root, own, "def test_gate(): pass")
    put(graph_root, other, "def test_workflow(): pass")
    paths = affected.select(graph_root, ["packages/devkit/src/devkit_agt/features/gate/usecases/runner.py"]).paths
    assert own in paths
    assert other not in paths


def test_pythonpath_support_helpers_keep_cross_category_dependencies(affected: ModuleType, graph_root: Path) -> None:
    put(
        graph_root, "pyproject.toml", '[tool.pytest.ini_options]\npythonpath = ["packages/devkit-spec/tests/support"]\n'
    )
    put(graph_root, f"{SPEC_TESTS}/support/spec_support/__init__.py", "")
    put(graph_root, f"{SPEC_TESTS}/support/spec_support/scope.py", "import devkit_spec.features.scope.models.registry")
    consumer = f"{TESTS}/integration/features/workflow/test_support.py"
    put(graph_root, consumer, "from spec_support.scope import value")
    assert consumer in affected.select(graph_root, [SCOPE_SOURCE]).paths
