from __future__ import annotations

import os
from pathlib import Path

import pytest
from devkit.core import ConfigError, find_project_root, git_toplevel, read_project_config
from devkit.core import project as project_module
from devkit.core.errors import GitError


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


def test_outside_git_walks_to_the_filesystem_root(tmp_path: Path) -> None:
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
