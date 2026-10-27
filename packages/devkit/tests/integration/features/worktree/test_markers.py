"""``branch_marker``: the ``branch.<branch>.devkit*`` keys read from the local configuration."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from devkit_agt.features.worktree import BASE_KEY, MARKER, UNIT_KEY, branch_marker, marker_key
from testsupport.rules import git, init_repo


def test_markers_are_read_from_the_local_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo(tmp_path / "repo")
    glob = tmp_path / "global.gitconfig"
    glob.write_text(f'[branch "dev-x"]\n\t{UNIT_KEY} = from-global\n')
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.fspath(glob))
    git(repo, "config", "--local", marker_key("dev-x"), "/wt")
    git(repo, "config", "--local", marker_key("dev-x", BASE_KEY), "main")
    assert marker_key("dev-x") == f"branch.dev-x.{MARKER}"
    assert branch_marker(repo, "dev-x") == "/wt"
    assert branch_marker(repo, "dev-x", BASE_KEY) == "main"
    assert branch_marker(repo, "dev-x", UNIT_KEY) == ""  # a global value is never a marker
    assert branch_marker(repo, "dev-y") == ""
