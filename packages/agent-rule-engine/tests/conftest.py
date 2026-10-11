from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from agent_rule_engine import WorkspaceCache


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def workspace_cache(temp_workspace: Path) -> WorkspaceCache:
    return WorkspaceCache(temp_workspace)
