from __future__ import annotations

import os
import unicodedata
from pathlib import Path

import pytest


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


def test_only_the_workspace_relative_part_takes_another_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    """On a file system that keeps names as written (Linux), the root's own spelling must survive a target fix-up."""
    from devkit_agt.features.rules.services import targets

    root = Path("/fs") / _nfd("café")
    on_disk = {str(root), str(root / "docs"), str(root / "docs" / _nfc("né.md"))}

    def listdir(path: str | os.PathLike[str]) -> list[str]:
        prefix = f"{os.fspath(path)}/"
        return [name[len(prefix) :] for name in on_disk if name.startswith(prefix) and "/" not in name[len(prefix) :]]

    monkeypatch.setattr(Path, "exists", lambda self, **_: str(self) in on_disk)
    monkeypatch.setattr(targets.os, "listdir", listdir)
    monkeypatch.setattr(targets.os.path, "lexists", lambda path: os.fspath(path) in on_disk)

    typed = root / "docs" / _nfd("né.md")
    assert targets._on_disk(root, typed) == root / "docs" / _nfc("né.md")
    missing = root / "docs" / _nfd("absent-é.md")
    assert targets._on_disk(root, missing) == missing
