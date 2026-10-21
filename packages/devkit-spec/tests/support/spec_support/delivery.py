"""Shared installed-bundle delivery fixtures and Git helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli

from spec_support.scope import git, write


def _devkit(*args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def _cli(root: Path, *args: str) -> str:
    res = CliRunner().invoke(devkit_cli, [*args, "-w", str(root)])
    assert res.exit_code == 0, res.stdout + (res.stderr if hasattr(res, "stderr") else "")
    return res.stdout


@pytest.fixture(scope="module")
def synced_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("synced-integration")
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    res = _devkit("sync", "-w", str(root))
    assert res.returncode == 0, res.stderr
    return root


def _make_synced_repo(tmp_path: Path, template: Path, *, extra_config: str = "") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "commit.gpgsign", "false")
    shutil.copytree(template / ".devkit", repo / ".devkit", ignore=shutil.ignore_patterns("transient"))
    write(repo, ".gitignore", ".devkit/managed/\n")
    config_path = repo / ".devkit/config.toml"
    config_text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    if "[integration]" not in config_text:
        config_text += '\n[integration]\nprovider = "spec"\n'
    if extra_config:
        config_text += "\n" + extra_config.strip() + "\n"
    config_path.write_text(config_text.lstrip(), encoding="utf-8")
    write(
        repo,
        "docs/capabilities/delivery/CAP-DLV-sample.md",
        "---\nid: CAP-DLV-sample\ntitle: Sample\nsummary: Sample capability.\nstatus: active\narea: delivery\ncreated: 2026-10-01\nupdated: 2026-10-01\n---\n\n# [CAP-DLV-sample] Sample\n\n## 1. Overview\nSample capability.\n",
    )
    write(repo, "src/app.py", "VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "initial")
    return repo


def _start_worktree(repo: Path, branch: str, path: Path) -> Path:
    git(repo, "worktree", "add", "-q", "-b", branch, str(path), "main")
    git(repo, "config", f"branch.{branch}.devkitWorktree", "true")
    git(repo, "config", f"branch.{branch}.devkitBase", "main")
    shutil.copytree(repo / ".devkit/managed", path / ".devkit/managed", dirs_exist_ok=True)
    return path
