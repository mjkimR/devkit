from __future__ import annotations

from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, repo_factory


@pytest.fixture
def make_repo(tmp_path: Path) -> MakeRepo:
    return repo_factory(tmp_path)
