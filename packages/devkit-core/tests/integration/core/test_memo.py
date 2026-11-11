"""``devkit_core.core.memo.safe_memo_path``: one path rule for every fingerprinted memo."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import pytest
from devkit_core.core.memo import PathRefusal, safe_memo_path

PARTS = ("rules", "facts", "RULE-x.json")


@pytest.fixture
def root(tmp_path: Path) -> Path:
    root = (tmp_path / "root").resolve()
    (root / ".devkit" / "transient" / "rules" / "facts").mkdir(parents=True)
    return root


def _relink(path: Path) -> None:
    """Move ``path`` aside within the same parent tree and leave a symbolic link to it."""
    moved = path.with_name(path.name + ".real")
    path.rename(moved)
    path.symlink_to(moved, target_is_directory=moved.is_dir())


def _remove(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        child.rmdir() if child.is_dir() else child.unlink()
    path.rmdir()


def _obstruct(path: Path) -> None:
    _remove(path)
    path.write_text("x")


def test_a_safe_layout_gives_the_path_with_or_without_the_file(root: Path) -> None:
    path = root / ".devkit/transient/rules/facts/RULE-x.json"
    assert safe_memo_path(root, PARTS, create=False) == path
    path.write_text("{}")
    assert safe_memo_path(root, PARTS, create=False) == path


LAYOUTS: dict[str, tuple[Callable[[Path], None], PathRefusal]] = {
    "no .devkit": (lambda r: _remove(r / ".devkit"), PathRefusal.NO_TRANSIENT),
    "no transient": (lambda r: _remove(r / ".devkit/transient"), PathRefusal.NO_TRANSIENT),
    ".devkit is a file": (lambda r: _obstruct(r / ".devkit"), PathRefusal.NO_TRANSIENT),
    "transient is a file": (lambda r: _obstruct(r / ".devkit/transient"), PathRefusal.NO_TRANSIENT),
    ".devkit is a symlink": (lambda r: _relink(r / ".devkit"), PathRefusal.NO_TRANSIENT),
    "transient is a symlink": (lambda r: _relink(r / ".devkit/transient"), PathRefusal.NO_TRANSIENT),
    "first directory is a symlink": (lambda r: _relink(r / ".devkit/transient/rules"), PathRefusal.SYMLINK),
    "last directory is a symlink": (lambda r: _relink(r / ".devkit/transient/rules/facts"), PathRefusal.SYMLINK),
    "a directory is a file": (lambda r: _obstruct(r / ".devkit/transient/rules"), PathRefusal.NOT_DIRECTORY),
    "a directory is missing": (lambda r: _remove(r / ".devkit/transient/rules/facts"), PathRefusal.MISSING),
    "the file is a symlink": (lambda r: _link_file(r), PathRefusal.SYMLINK),
    "the file is a dangling symlink": (lambda r: _dangling_file(r), PathRefusal.SYMLINK),
    "the file is a directory": (
        lambda r: (r / ".devkit/transient/rules/facts/RULE-x.json").mkdir(),
        PathRefusal.NOT_REGULAR,
    ),
}


def _link_file(root: Path) -> None:
    target = root / "real.json"
    target.write_text("{}")
    (root / ".devkit/transient/rules/facts/RULE-x.json").symlink_to(target)


def _dangling_file(root: Path) -> None:
    (root / ".devkit/transient/rules/facts/RULE-x.json").symlink_to(root / "absent.json")


@pytest.mark.parametrize("layout", list(LAYOUTS))
def test_every_unsafe_layout_is_refused_silently(root: Path, layout: str, caplog: pytest.LogCaptureFixture) -> None:
    change, refusal = LAYOUTS[layout]
    change(root)
    with caplog.at_level(logging.DEBUG):
        assert safe_memo_path(root, PARTS, create=False) is refusal
    assert caplog.records == []


def test_a_directory_that_resolves_elsewhere_is_moved(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    facts = root / ".devkit/transient/rules/facts"
    real_resolve = Path.resolve

    def resolve(self: Path, strict: bool = False) -> Path:
        return root / "elsewhere" if self == facts else real_resolve(self, strict)

    monkeypatch.setattr(Path, "resolve", resolve)
    assert safe_memo_path(root, PARTS, create=False) is PathRefusal.MOVED


def test_create_makes_missing_directories_below_transient_only(root: Path) -> None:
    _remove(root / ".devkit/transient/rules")
    path = root / ".devkit/transient/rules/facts/RULE-x.json"
    assert safe_memo_path(root, PARTS, create=True) == path
    assert path.parent.is_dir() and not path.exists()
    _remove(root / ".devkit/transient")
    assert safe_memo_path(root, PARTS, create=True) is PathRefusal.NO_TRANSIENT
    assert not (root / ".devkit/transient").exists()


def test_create_never_replaces_a_symlink_or_a_file(root: Path) -> None:
    _relink(root / ".devkit/transient/rules/facts")
    assert safe_memo_path(root, PARTS, create=True) is PathRefusal.SYMLINK
    (root / ".devkit/transient/rules/facts").unlink()
    (root / ".devkit/transient/rules/facts").symlink_to(root / "absent", target_is_directory=True)
    assert safe_memo_path(root, PARTS, create=True) is PathRefusal.SYMLINK
    assert not (root / "absent").exists()


def test_a_path_needs_a_file_name(root: Path) -> None:
    with pytest.raises(ValueError, match="file name"):
        safe_memo_path(root, (), create=False)
