"""Projection diagnostics against real Git rules and index state."""

from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_core.base.errors import GitError
from devkit_dist.features.distribution.repositories import projection_git
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases import commands
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import cli, write_bundle

NATIVE = ".agents/skills/demo/SKILL.md"


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout


@pytest.fixture
def root(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    git(root, "init", "-q")
    return root


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    return [
        write_bundle(
            tmp_path / "bundle",
            """schema = 1
name = "team"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "demo"
kind = "skill"
source = "demo"
""",
            {"demo/SKILL.md": "# Demo\n"},
        )
    ]


def notices(root: Path, desired: list[str], previous: list[str] | None = None):
    return projection_git.projection_git_notices(root, desired, previous or [])


def test_coverage_uses_nested_negation_and_excludes_neighbors(root: Path) -> None:
    (root / ".gitignore").write_text(".agents/skills/demo/*\n")
    directory = root / ".agents/skills/demo"
    directory.mkdir(parents=True)
    (directory / ".gitignore").write_text("!SKILL.md\n")
    result = notices(root, [NATIVE, ".agents/skills/demo/ref.md", ".devkit/managed/team/guide.md"])
    assert [(n.code, n.target_files) for n in result] == [("PROJECTION_NOT_IGNORED", (NATIVE,))]
    (directory / ".gitignore").write_text("# no negation\n")
    assert notices(root, [NATIVE]) == []
    assert not (root / NATIVE).exists()  # planned, not yet deployed


def test_tracked_ignored_and_removed_files_preserve_index(root: Path) -> None:
    path = root / NATIVE
    path.parent.mkdir(parents=True)
    path.write_text("generated\n")
    neighbor = path.parent / "custom.md"
    neighbor.write_text("project-owned\n")
    git(root, "add", "--", NATIVE, str(neighbor))
    (root / ".gitignore").write_text(".agents/\n")
    before = (root / ".git/index").read_bytes()
    ignore = (root / ".gitignore").read_bytes()
    result = notices(root, [], [NATIVE, ".agents/skills/gone/SKILL.md"])
    assert [(n.code, n.target_files) for n in result] == [("PROJECTION_TRACKED", (NATIVE,))]
    assert (root / ".git/index").read_bytes() == before
    assert (root / ".gitignore").read_bytes() == ignore


def test_bound_and_literal_untracking_remediation(root: Path) -> None:
    names = [f".agents/skills/demo/{i:02}.md" for i in range(15)]
    (finding,) = notices(root, names)
    assert len(finding.target_files) == 10
    assert list(finding.target_files) == sorted(names)[:10]
    special = ".agents/skills/demo/a [x]*'file.md"
    path = root / special
    path.parent.mkdir(parents=True)
    path.write_text("generated\n")
    neighbor = path.parent / "a xOTHERfile.md"
    neighbor.write_text("project\n")
    git(root, "add", ".")
    (finding,) = notices(root, [special])
    assert finding.fix is not None
    other = root.parent / "other"
    other.mkdir()
    git(other, "init", "-q")
    other_path = other / special
    other_path.parent.mkdir(parents=True)
    other_path.write_text("unrelated repository\n")
    git(other, "add", ".")
    other_index = (other / ".git/index").read_bytes()
    subprocess.run(["sh", "-c", finding.fix], cwd=other, check=True, capture_output=True)
    assert (other / ".git/index").read_bytes() == other_index
    assert path.exists()
    assert git(root, "ls-files", "-z") == str(neighbor.relative_to(root)).encode() + b"\0"


@pytest.mark.parametrize("failed_command", ["rev-parse", "ls-files"])
def test_non_git_and_failed_query(
    tmp_path: Path, root: Path, monkeypatch: pytest.MonkeyPatch, failed_command: str
) -> None:
    assert notices(tmp_path, [NATIVE]) == []

    original = projection_git.run_git

    def fail(cwd, *args, **kwargs):
        if args[0] == failed_command:
            raise GitError(
                "query failed", command=("git", failed_command), returncode=128, stderr="fatal: access denied"
            )
        return original(cwd, *args, **kwargs)

    monkeypatch.setattr(projection_git, "run_git", fail)
    (finding,) = notices(root, [NATIVE])
    assert finding.code == "PROJECTION_GIT_CHECK_FAILED"


def test_sync_preview_locked_and_removal(root: Path, installed: list[InstalledBundle]) -> None:
    update_config(root, presets={"team": ["all"]}, agents=["codex"])
    before = (root / ".devkit/config.toml").read_bytes()
    preview = sync_project(root, installed, dry_run=True)
    assert "PROJECTION_NOT_IGNORED" in [n.code for n in preview.notices]
    assert not (root / NATIVE).exists()
    assert (root / ".devkit/config.toml").read_bytes() == before
    sync_project(root, installed)
    locked = sync_project(root, installed, locked=True)
    assert "PROJECTION_NOT_IGNORED" in [n.code for n in locked.notices]
    assert locked.actions == []
    removed = sync_project(root, installed, deselect=["team"])
    assert not any(n.code.startswith("PROJECTION_") for n in removed.notices)


def test_cli_json_strict_and_check(
    root: Path, installed: list[InstalledBundle], monkeypatch: pytest.MonkeyPatch
) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr(commands, "discover_bundles", found)
    update_config(root, presets={"team": ["all"]}, agents=["codex"])
    runner = CliRunner()
    args = ["sync", "-w", str(root), "--format", "json"]
    first = runner.invoke(cli, args)
    assert first.exit_code == 0, first.output
    assert "PROJECTION_NOT_IGNORED" in [n["code"] for n in json.loads(first.stdout)["notices"]]
    strict = runner.invoke(cli, [*args, "--strict"])
    assert strict.exit_code == 1, strict.output
    checked = runner.invoke(cli, [*args, "--check"])
    assert checked.exit_code == 0, checked.output
    assert "PROJECTION_NOT_IGNORED" in [n["code"] for n in json.loads(checked.stdout)["notices"]]
