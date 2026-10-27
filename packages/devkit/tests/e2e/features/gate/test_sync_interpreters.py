"""Shared hook fallback lifetime across automatic sync and worktree removal."""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

import devkit_agt.features.gate.usecases.hooks.hooks as hooks
import devkit_agt.features.gate.usecases.hooks.local_config as local_config
import pytest
from devkit_agt.features.gate import Stage
from testsupport.gate import git


def _python(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n')
    path.chmod(0o755)
    return str(path)


def test_linked_sync_retains_fallback_after_worktree_removal(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stable = _python(repo / "stable-python")
    hooks.install(repo, stable)
    git(repo, "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "seed")
    linked = repo.parent / "linked"
    git(repo, "worktree", "add", "-b", "dev-test", str(linked))
    disposable = _python(linked / "python")
    monkeypatch.setattr(local_config.sys, "executable", disposable)
    assert local_config.post_sync(linked, {}) is None
    git(repo, "worktree", "remove", "--force", str(linked))
    entries = [s for s in hooks.status(repo) if s.stage in (Stage.PRE_COMMIT, Stage.COMMIT_MSG)]
    assert all(s.python == stable and s.python_ok for s in entries)
    ran = subprocess.run([str(repo / ".git/hooks/pre-commit")], cwd=repo, capture_output=True, text=True)
    assert ran.returncode == 0, ran.stderr


@pytest.mark.parametrize("invalid", ["missing", "import-failure"])
def test_sync_repairs_invalid_fallback_per_stage(repo: Path, invalid: str) -> None:
    stable = _python(repo / "stable-python")
    hooks.install(repo, stable)
    broken = _python(repo / "broken-python")
    if invalid == "missing":
        Path(broken).unlink()
    else:
        Path(broken).write_text("#!/bin/sh\nexit 1\n")
    entry = repo / ".git/hooks/commit-msg.d/20-devkit"
    entry.write_text(hooks.wrapper_script(Stage.COMMIT_MSG, broken))
    assert local_config.post_sync(repo, {}) == ["gate hooks: commit-msg: installed"]
    states = {s.stage: s for s in hooks.status(repo)}
    assert states[Stage.PRE_COMMIT].python == stable
    assert states[Stage.COMMIT_MSG].python == sys.executable
    assert states[Stage.COMMIT_MSG].python_ok


def test_sync_installs_missing_entries_and_explicit_install_replaces(repo: Path) -> None:
    assert local_config.post_sync(repo, {}) is not None
    assert local_config.post_sync(repo, {}) is None
    replacement = _python(repo / "replacement-python")
    hooks.install(repo, replacement)
    assert all(s.python == replacement for s in hooks.status(repo) if s.python)
