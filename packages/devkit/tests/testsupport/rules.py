"""Rule engine test helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


def write_receipt(root: Path, assets: list[dict[str, object]], files: dict[str, str] | None = None) -> Path:
    """Write a schema-valid ``.devkit/installation.json``; ``files`` maps workspace paths to SHA-256 digests."""
    path = root / ".devkit/installation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema": 1,
        "packages": [],
        "selection": {"agents": [], "presets": {}},
        "assets": assets,
        "files": {name: {"sha256": digest, "mode": 420} for name, digest in (files or {}).items()},
    }
    path.write_text(json.dumps(data))
    return path


def digests(root: Path, *rels: str) -> dict[str, str]:
    """The SHA-256 of each ``root/rel``, keyed by ``rel``: the ``files`` argument of ``write_receipt``."""
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in rels}


def git(root: Path, *args: str) -> str:
    """Run Git in ``root`` with a clean ``GIT_*`` environment and return its stripped standard output."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    completed = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True, env=env)
    return completed.stdout.strip()


def init_repo(root: Path) -> Path:
    """An initialized repository on ``main`` with one commit (``README.md``)."""
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    (root / "README.md").write_text("# Repo\n")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "init")
    return root


def write(root: Path, rel: str, text: str | bytes) -> Path:
    """Write ``text`` (or bytes) to ``root/rel``, creating parent directories."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path
