"""Keep scope fixtures independent of the checkout containing pytest basetemp."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_git_discovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Stop above the per-test root; real repositories and linked worktrees below it remain discoverable.
    ceilings = [part for part in os.environ.get("GIT_CEILING_DIRECTORIES", "").split(os.pathsep) if part]
    ceilings.extend((str(tmp_path.parent), str(tmp_path.resolve().parent)))
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", os.pathsep.join(dict.fromkeys(ceilings)))
