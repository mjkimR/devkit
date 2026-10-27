"""The gate's ``devkit.post_sync`` extension, run by a real ``devkit sync`` of devkit-dist."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from testsupport.gate import git


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    root = tmp_path / "source"
    root.mkdir()
    (root / "guide.md").write_text("---\nname: guide\ndescription: Team guide.\n---\n# Guide\n")
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "team"\nversion = "0.1.0"\n'
        '[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "guide.md"\n'
    )
    return [InstalledBundle("team-content", "0.1.0", load_bundle(root))]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["codex"])
    return root


def test_sync_installs_hooks_only_after_writing(target: Path, installed: list[InstalledBundle]) -> None:
    git(target, "init", "-q")
    sync_project(target, installed, dry_run=True)
    assert not (target / ".git/hooks/pre-commit").exists()
    result = sync_project(target, installed)
    hooks_line = [item for item in result.notices if item.code == "POST_SYNC_NOTICE"]
    assert [item.message for item in hooks_line] == [
        "gate hooks: pre-commit: installed; commit-msg: installed; post-commit: installed"
    ]
    assert all(item.code == "MCP_RUNTIME_UNAVAILABLE" for item in result.notices if item not in hooks_line)
    entry = target / ".git/hooks/pre-commit.d/20-devkit"
    assert entry.is_file()
    assert (target / ".git/hooks/post-commit.d").is_dir()
    assert not (target / ".git/hooks/post-commit.d/20-devkit").exists()
    before = entry.stat().st_mtime_ns
    sync_project(target, installed, locked=True)
    assert entry.stat().st_mtime_ns == before
