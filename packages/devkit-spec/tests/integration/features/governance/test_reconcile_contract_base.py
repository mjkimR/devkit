"""The reconcile contract's integration base reads the worktree list as records."""

from __future__ import annotations

from pathlib import Path

from spec_support.scope import git

from devkit_spec.features.governance.usecases.reconcile_contract import _integration_base


def test_a_newline_in_the_base_path_is_not_read_as_a_branch(tmp_path: Path) -> None:
    root = tmp_path / "r\nbranch evil"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "-c", "user.name=T", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "a")
    linked = tmp_path / "linked"
    git(root, "worktree", "add", "-q", "-b", "feature", str(linked))
    assert _integration_base(linked) == "main"
