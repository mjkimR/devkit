from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

import pytest
from devkit.core import UnsafePathError, is_safe_relpath, normalize_relpath, resolve_within


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a", "a"),
        ("a/b.md", "a/b.md"),
        (".devkit/managed/x.py", ".devkit/managed/x.py"),
        ("a//b", "a/b"),
        ("./a", "a"),
        ("a/./b/", "a/b"),
        ("dir\\file.md", "dir\\file.md"),
        ("a\\b\\c", "a\\b\\c"),
        ("..a", "..a"),
        ("a..", "a.."),
        ("한글/파일.md", "한글/파일.md"),
        (" leading-space", " leading-space"),
    ],
)
def test_accepted_paths(value: str, expected: str) -> None:
    assert normalize_relpath(value) == PurePosixPath(expected)
    assert is_safe_relpath(value)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("", "empty"),
        ("   ", "empty"),
        (".", "root itself"),
        ("./", "root itself"),
        ("./.", "root itself"),
        ("/etc/passwd", "relative"),
        ("//x", "relative"),
        ("..", r"'\.\.'"),
        ("../x", r"'\.\.'"),
        ("a/../b", r"'\.\.'"),
        ("a/..", r"'\.\.'"),
        ("\\x", "backslashes"),
        ("..\\x", "backslashes"),
        ("a\\..\\b", "backslashes"),
        ("C:", "drive"),
        ("c:\\windows", "drive"),
        ("C:foo", "drive"),
        ("a\0b", "NUL"),
    ],
)
def test_rejected_paths(value: str, message: str) -> None:
    with pytest.raises(UnsafePathError, match=message):
        normalize_relpath(value)
    assert not is_safe_relpath(value)


def test_non_string_values_are_rejected() -> None:
    with pytest.raises(UnsafePathError, match="must be a string"):
        normalize_relpath(3)  # type: ignore[arg-type]
    assert not is_safe_relpath(None)
    assert not is_safe_relpath(["a"])


@pytest.mark.parametrize("value", ["a//b", "./a", "a/", "a/./b"])
def test_canonical_mode_rejects_unnormalized_values(value: str) -> None:
    assert is_safe_relpath(value)
    assert not is_safe_relpath(value, canonical=True)
    with pytest.raises(UnsafePathError, match="canonical"):
        normalize_relpath(value, canonical=True)


def test_canonical_mode_accepts_normalized_values() -> None:
    assert normalize_relpath("a/b", canonical=True) == PurePosixPath("a/b")


def test_resolve_within(tmp_path: Path) -> None:
    root = tmp_path / "root"
    (root / "sub").mkdir(parents=True)
    (root / "sub/file.txt").write_text("x")
    assert resolve_within(root, "sub/file.txt") == (root / "sub/file.txt").resolve()
    assert resolve_within(root, PurePosixPath("sub/new/missing.txt")) == (root / "sub/new/missing.txt").resolve()
    with pytest.raises(UnsafePathError):
        resolve_within(root, "../outside")


def test_resolve_within_follows_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret").write_text("s")
    os.symlink(outside, root / "escape")
    os.symlink(root / "real", root / "inside")
    (root / "real").mkdir()
    with pytest.raises(UnsafePathError, match="resolves outside"):
        resolve_within(root, "escape/secret")
    assert resolve_within(root, "inside/x") == (root / "real/x").resolve()


def test_resolve_within_with_symlinked_root(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    os.symlink(real, link)
    assert resolve_within(link, "a.txt") == real.resolve() / "a.txt"


def test_a_symlink_loop_cannot_be_resolved(tmp_path: Path) -> None:
    (tmp_path / "a").symlink_to(tmp_path / "b")
    (tmp_path / "b").symlink_to(tmp_path / "a")
    with pytest.raises(UnsafePathError, match=r"path cannot be resolved: a/x\.py"):
        resolve_within(tmp_path, "a/x.py")
