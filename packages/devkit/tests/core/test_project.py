from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import pytest
from devkit.core import (
    ConfigError,
    config_table,
    find_project_root,
    git_toplevel,
    read_project_config,
    read_toml,
    require_git_toplevel,
)
from devkit.core import project as project_module
from devkit.core.errors import GitError, UnsafePathError


def test_nearest_devkit_directory_wins(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    nested = repo / "packages/app"
    (nested / ".devkit").mkdir(parents=True)
    (nested / "src/deep").mkdir(parents=True)
    assert find_project_root(nested / "src/deep") == nested
    assert find_project_root(nested) == nested
    assert find_project_root(repo / "packages") == repo


def test_a_file_start_uses_its_directory(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / "docs").mkdir()
    (repo / "docs/a.md").write_text("x")
    assert find_project_root(repo / "docs/a.md") == repo


def test_devkit_file_is_not_a_project_marker(repo: Path) -> None:
    (repo / "sub").mkdir()
    (repo / "sub/.devkit").write_text("not a directory")
    assert find_project_root(repo / "sub") == repo


def test_falls_back_to_git_toplevel(repo: Path) -> None:
    (repo / "a/b").mkdir(parents=True)
    assert find_project_root(repo / "a/b") == repo
    assert git_toplevel(repo / "a/b") == repo


def test_walk_stops_at_the_repository_boundary(tmp_path: Path, repo: Path) -> None:
    # ``repo`` lives at tmp_path/repo; a .devkit directory above it belongs to no project of this repo.
    (tmp_path / ".devkit").mkdir()
    (repo / "x").mkdir()
    assert find_project_root(repo / "x") == repo


def test_outside_git_walks_up_the_parents(tmp_path: Path) -> None:
    project = tmp_path / "plain"
    (project / ".devkit").mkdir(parents=True)
    (project / "a/b").mkdir(parents=True)
    assert git_toplevel(project) is None
    assert find_project_root(project / "a/b") == project.resolve()


def test_outside_git_without_marker_returns_start(tmp_path: Path) -> None:
    start = tmp_path / "lonely"
    start.mkdir()
    assert find_project_root(start) == start.resolve()


def test_symlinked_start_is_resolved(tmp_path: Path) -> None:
    real = tmp_path / "real"
    (real / ".devkit").mkdir(parents=True)
    os.symlink(real, tmp_path / "link")
    assert find_project_root(tmp_path / "link") == real.resolve()


def test_git_toplevel_tolerates_git_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> bytes:
        raise GitError("boom")

    monkeypatch.setattr(project_module, "run_git", fail)
    assert git_toplevel(tmp_path) is None

    monkeypatch.setattr(project_module, "run_git", lambda *a, **k: b"\n")
    assert git_toplevel(tmp_path) is None


def test_read_project_config(tmp_path: Path) -> None:
    assert read_project_config(tmp_path) == {}
    config = tmp_path / ".devkit/config.toml"
    config.parent.mkdir()
    config.write_text('schema = 1\n[rules]\nexclude = ["vendor/**"]\n')
    assert read_project_config(tmp_path) == {"schema": 1, "rules": {"exclude": ["vendor/**"]}}


@pytest.mark.parametrize(
    "content",
    [b"[rules\n", b"a = 1\na = 2\n", b"x = '\xff'\n"],
)
def test_invalid_config(tmp_path: Path, content: bytes) -> None:
    config = tmp_path / ".devkit/config.toml"
    config.parent.mkdir()
    config.write_bytes(content)
    with pytest.raises(ConfigError, match=r"invalid config \.devkit/config\.toml"):
        read_project_config(tmp_path)


def test_unreadable_config(tmp_path: Path) -> None:
    (tmp_path / ".devkit/config.toml").mkdir(parents=True)
    with pytest.raises(ConfigError):
        read_project_config(tmp_path)


def test_require_git_toplevel_names_the_workspace_root_option(repo: Path, tmp_path: Path) -> None:
    (repo / "a/b").mkdir(parents=True)
    assert require_git_toplevel(repo / "a/b") == repo
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(GitError, match="not inside a Git work tree") as caught:
        require_git_toplevel(outside)
    error = caught.value
    assert (error.code, error.mode.value, error.target_files) == ("GIT_FAILED", "INPUT_ERROR", ("--workspace-root",))
    assert error.fix and "--workspace-root" in error.fix
    assert "not a git repository" in error.message  # Git's own diagnostic is kept


def test_require_git_toplevel_passes_through_a_git_that_did_not_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = GitError("git is not available: [Errno 2] No such file", command=("git",))

    def missing(*args: object, **kwargs: object) -> bytes:
        raise original

    monkeypatch.setattr(project_module, "run_git", missing)
    with pytest.raises(GitError) as caught:
        require_git_toplevel(tmp_path)
    assert caught.value is original and caught.value.mode.value == "MAINTENANCE"
    assert git_toplevel(tmp_path) is None


def test_read_toml_reports_its_display_name(tmp_path: Path) -> None:
    path = tmp_path / "local.config"
    assert read_toml(path) is None
    path.write_text("[gates]\nx = 1\n")
    assert read_toml(path) == {"gates": {"x": 1}}
    path.write_text("[gates\n")
    with pytest.raises(ConfigError, match="invalid config local") as caught:
        read_toml(path, "local")
    assert caught.value.target_files == ("local",)


class AreaConfigError(ConfigError):
    code = "AREA_CONFIG_INVALID"


def test_config_table_raises_the_area_error() -> None:
    assert config_table({"a": 1}, "area", AreaConfigError) == {"a": 1}
    with pytest.raises(AreaConfigError, match=r"config area\.x: expected a table"):
        config_table(3, "area.x", AreaConfigError)


def test_outside_git_the_walk_stops_below_the_home_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home = (tmp_path / "home").resolve()
    (home / ".devkit").mkdir(parents=True)  # a stray ~/.devkit
    (home / "scratch/a").mkdir(parents=True)
    (home / "proj/.devkit").mkdir(parents=True)
    (home / "proj/sub").mkdir()
    (tmp_path / ".devkit").mkdir()  # above the home directory
    monkeypatch.setenv("HOME", str(home))
    assert find_project_root(home / "scratch/a") == home / "scratch/a"
    assert find_project_root(home / "proj/sub") == home / "proj"
    assert find_project_root(home) == home


def test_a_looping_start_is_unsafe(tmp_path: Path) -> None:
    (tmp_path / "a").symlink_to(tmp_path / "b")
    (tmp_path / "b").symlink_to(tmp_path / "a")
    with pytest.raises(UnsafePathError, match="cannot be resolved"):
        find_project_root(tmp_path / "a")


def test_an_unsearchable_devkit_directory_is_a_config_error(tmp_path: Path, lock: Callable[[Path], None]) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text("a = 1\n")
    lock(tmp_path / ".devkit")
    with pytest.raises(ConfigError, match=r"invalid config \.devkit/config\.toml"):
        read_project_config(tmp_path)
