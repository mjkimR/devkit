"""Locate a devkit project and read its ``.devkit/config.toml``."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from devkit.core.errors import ConfigError, GitError
from devkit.core.git import run_git
from devkit.core.receipt import CONFIG_PATH

DEVKIT_DIR = ".devkit"
_GIT_TIMEOUT = 10.0


def git_toplevel(start: Path) -> Path | None:
    """The resolved top-level directory of the Git work tree containing ``start``, or ``None``."""
    try:
        output = run_git(start, "rev-parse", "--show-toplevel", timeout=_GIT_TIMEOUT)
    except GitError:
        return None
    text = os.fsdecode(output.rstrip(b"\n"))
    return Path(text).resolve() if text else None


def find_project_root(start: Path) -> Path:
    """The devkit project root for ``start`` (a directory, or a file whose directory is used).

    Resolution, on the resolved ``start``:

    1. The nearest directory, ``start`` itself first and then each parent,
       that contains a ``.devkit`` directory. Inside a Git work tree the walk
       stops at the work tree's top level, so a ``.devkit`` directory outside
       the repository is never picked up.
    2. Otherwise the top level of the Git work tree containing ``start``.
    3. Otherwise ``start`` itself.
    """
    origin = start.resolve()
    if not origin.is_dir():
        origin = origin.parent
    toplevel = git_toplevel(origin)
    for candidate in (origin, *origin.parents):
        if (candidate / DEVKIT_DIR).is_dir():
            return candidate
        if candidate == toplevel:
            break
    return toplevel if toplevel is not None else origin


def read_project_config(root: Path) -> dict[str, Any]:
    """Parse ``root/.devkit/config.toml``; a missing file is ``{}``.

    Raises ``ConfigError`` when the file exists but cannot be read, is not
    UTF-8 or is not valid TOML. The tables are returned unvalidated; each
    package validates the tables it owns.
    """
    path = root / CONFIG_PATH
    if not path.exists() and not path.is_symlink():
        return {}
    try:
        return tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid config {CONFIG_PATH}: {exc}") from exc
