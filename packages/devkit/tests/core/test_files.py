from __future__ import annotations

import os
import stat
from collections.abc import Callable
from pathlib import Path

import pytest
from devkit.core import atomic_write_bytes, atomic_write_text, remove_empty_tree


def test_atomic_write_creates_parents_and_writes_exactly(tmp_path: Path) -> None:
    path = tmp_path / "a" / "b.txt"
    atomic_write_text(path, "x\r\ny\n")
    assert path.read_bytes() == b"x\r\ny\n"
    assert stat.S_IMODE(path.stat().st_mode) == 0o644
    assert [p.name for p in path.parent.iterdir()] == ["b.txt"]  # no temporary file left behind


def test_atomic_write_keeps_the_existing_mode_unless_given(tmp_path: Path) -> None:
    path = tmp_path / "script.sh"
    path.write_bytes(b"old")
    path.chmod(0o755)
    atomic_write_bytes(path, b"new")
    assert path.read_bytes() == b"new" and stat.S_IMODE(path.stat().st_mode) == 0o755
    atomic_write_bytes(path, b"newer", mode=0o600)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_atomic_write_replaces_a_symlink_instead_of_writing_through_it(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_bytes(b"target")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    atomic_write_bytes(link, b"new")
    assert not link.is_symlink() and link.read_bytes() == b"new" and target.read_bytes() == b"target"


def test_a_failed_atomic_write_leaves_the_target_and_no_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "f.txt"
    path.write_bytes(b"old")

    def fail(src: object, dst: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError, match="replace failed"):
        atomic_write_bytes(path, b"new")
    assert path.read_bytes() == b"old" and [p.name for p in tmp_path.iterdir()] == ["f.txt"]


def test_remove_empty_tree_removes_only_directories_deepest_first(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    (tree / "a" / "b").mkdir(parents=True)
    (tree / "c").mkdir()
    removed = remove_empty_tree(tree)
    assert removed[-1] == tree and set(removed) == {tree, tree / "a", tree / "a" / "b", tree / "c"}
    assert removed.index(tree / "a" / "b") < removed.index(tree / "a")
    assert not tree.exists() and tmp_path.is_dir()


def test_remove_empty_tree_keeps_a_tree_holding_any_file_or_symlink(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    (tree / "a" / "b").mkdir(parents=True)
    (tree / "empty").mkdir()
    (tree / "a" / "b" / ".keep").write_text("")
    assert remove_empty_tree(tree) == []
    assert (tree / "empty").is_dir() and (tree / "a" / "b" / ".keep").is_file()
    (tree / "a" / "b" / ".keep").unlink()
    (tree / "a" / "link").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    assert remove_empty_tree(tree) == [] and (tree / "empty").is_dir()


def test_remove_empty_tree_never_follows_or_removes_a_symlinked_directory(tmp_path: Path) -> None:
    real = tmp_path / "real"
    (real / "sub").mkdir(parents=True)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    holder = tmp_path / "holder"
    holder.mkdir()
    (holder / "inner").symlink_to(real, target_is_directory=True)
    assert remove_empty_tree(link) == [] and link.is_symlink()
    assert remove_empty_tree(holder) == [] and (holder / "inner").is_symlink()
    assert (real / "sub").is_dir()


def test_remove_empty_tree_of_a_missing_path_or_a_file_removes_nothing(tmp_path: Path) -> None:
    file = tmp_path / "file"
    file.write_text("x")
    assert remove_empty_tree(tmp_path / "missing") == []
    assert remove_empty_tree(file) == [] and file.is_file()


def test_remove_empty_tree_stops_before_removing_when_a_directory_cannot_be_listed(
    tmp_path: Path, lock: Callable[[Path], None]
) -> None:
    tree = tmp_path / "tree"
    (tree / "closed").mkdir(parents=True)
    (tree / "open").mkdir()
    lock(tree / "closed")
    with pytest.raises(PermissionError):
        remove_empty_tree(tree)
    assert (tree / "open").is_dir() and (tree / "closed").is_dir()
