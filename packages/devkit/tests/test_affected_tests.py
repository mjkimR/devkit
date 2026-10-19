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

ROOT = Path(__file__).resolve().parents[3]
TESTS = "packages/devkit/tests"


@pytest.fixture(scope="module")
def affected() -> ModuleType:
    spec = importlib.util.spec_from_file_location("affected_tests", ROOT / "scripts/affected_tests.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["affected_tests"] = module  # dataclasses resolve their module while the class is created
    spec.loader.exec_module(module)
    return module


def test_a_change_selects_its_area_and_the_areas_that_import_it(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit/src/devkit/worktree/lifecycle.py"])
    assert selection.mode == "partial"
    assert selection.reason == "devkit.worktree"
    assert {f"{TESTS}/worktree", f"{TESTS}/integration", "packages/devkit-spec/tests"} <= set(selection.paths)
    assert f"{TESTS}/gate" not in selection.paths


def test_a_leaf_area_selects_no_unrelated_area(affected: ModuleType) -> None:
    selection = affected.select(ROOT, ["packages/devkit/src/devkit/gate/runner.py"])
    assert selection.mode == "partial"
    assert f"{TESTS}/gate" in selection.paths
    assert {f"{TESTS}/worktree", f"{TESTS}/integration", f"{TESTS}/distribution"}.isdisjoint(selection.paths)
    assert set(affected.SOURCE_TREE_TESTS) <= set(selection.paths)


@pytest.mark.parametrize(
    "path",
    [
        "packages/devkit/src/devkit/core/git.py",
        "packages/devkit-advisory/src/devkit/advisory/error.py",
        "packages/devkit/src/devkit/cli.py",
        "packages/devkit/src/devkit/__main__.py",
        "packages/devkit-spec/pyproject.toml",
        "pyproject.toml",
        "uv.lock",
        "packages/devkit-spec/tests/conftest.py",
        "packages/devkit/tests/testsupport/gate.py",
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
    assert selection.paths == (
        "packages/devkit-spec/tests/test_documented_codes.py",
        f"{TESTS}/rules/test_docs.py",
        f"{TESTS}/test_documented_codes.py",
        f"{TESTS}/workflow/test_library.py",
    )


def test_changed_tests_select_themselves_and_helpers_their_directory(affected: ModuleType) -> None:
    selection = affected.select(
        ROOT,
        [
            "packages/devkit-spec/tests/scope/support.py",
            f"{TESTS}/gate/test_hooks.py",
            f"{TESTS}/gate/test_deleted_meanwhile.py",
        ],
    )
    assert selection.paths == ("packages/devkit-spec/tests/scope", f"{TESTS}/gate/test_hooks.py")


def test_paths_inside_a_selected_directory_are_covered(affected: ModuleType) -> None:
    scope = "packages/devkit-spec/tests/scope"
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
    assert command == [["bash", script, "test", "all", f"{TESTS}/test_module_script.py", "-k", "foo", "-n0"]]


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
