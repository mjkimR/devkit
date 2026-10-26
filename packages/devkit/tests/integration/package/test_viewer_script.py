"""The viewer frontend recipes name the missing install instead of failing inside npm."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]


@pytest.mark.parametrize("action", ["lint", "check", "test", "build", "pack"])
def test_action_without_dependencies_names_the_install(tmp_path: Path, action: str) -> None:
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts/viewer.sh", tmp_path / "scripts/viewer.sh")
    (tmp_path / "packages/devkit-viewer/frontend").mkdir(parents=True)
    result = subprocess.run(
        ["bash", str(tmp_path / "scripts/viewer.sh"), action], capture_output=True, text=True, check=False
    )
    assert result.returncode == 2
    assert "`just viewer install`" in result.stderr
    assert result.stdout == ""
