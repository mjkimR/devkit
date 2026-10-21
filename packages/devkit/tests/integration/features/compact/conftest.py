from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Logs go under the test's own temporary directory, and commands run from it."""
    temp = tmp_path / "tmp"
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
