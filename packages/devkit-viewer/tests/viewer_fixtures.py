"""Git fixtures of the devkit-viewer tests, importable under a name no other package's tests use."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def git(root: Path, *args: str) -> str:
    """Run Git in ``root`` with a fixed identity and no user configuration."""
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **_ENV},
    )
    return completed.stdout


def commit_files(root: Path, files: dict[str, str], message: str = "change") -> None:
    for path, text in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


MakeRepo = Callable[..., Path]


def repo_factory(tmp_path: Path) -> MakeRepo:
    """A Git repository ``<parent>/<name>`` on branch ``main`` with ``files`` committed; ``devkit`` adds
    ``.devkit/config.toml``."""

    def make(
        name: str, files: dict[str, str] | None = None, *, devkit: bool = True, parent: Path | None = None
    ) -> Path:
        root = (parent or tmp_path) / name
        root.mkdir(parents=True)
        git(root, "init", "-q", "-b", "main")
        content = dict(files or {"README.md": f"# {name}\n"})
        if devkit:
            content[".devkit/config.toml"] = ""
        commit_files(root, content, "initial")
        return root.resolve()

    return make
