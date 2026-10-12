from __future__ import annotations

from pathlib import Path

import pytest
from testsupport.workflow import WORKFLOW


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A workspace with one valid definition under the default definitions_dir."""
    defs = tmp_path / ".devkit" / "workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW, encoding="utf-8")
    return tmp_path
