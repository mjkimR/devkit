from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest
from devkit.core import atomic_write_bytes, atomic_write_text


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
