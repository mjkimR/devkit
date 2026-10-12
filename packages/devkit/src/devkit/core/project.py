"""Locate a devkit project and read its configuration files."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from devkit.core.errors import ConfigError, GitError
from devkit.core.git import run_git
from devkit.core.receipt import CONFIG_PATH

DEVKIT_DIR = ".devkit"
TOPLEVEL_FIX = "Run from inside the repository, or pass --workspace-root/-w a directory inside it"


def require_git_toplevel(start: Path) -> Path:
    """The resolved top-level directory of the Git work tree containing ``start``.

    Raises ``GitError`` (``GIT_FAILED``, an input error naming
    ``--workspace-root``) when ``start`` is not inside a Git work tree or Git
    cannot run.
    """
    try:
        output = run_git(start, "rev-parse", "--show-toplevel")
    except GitError as exc:
        raise GitError(
            f"{start} is not inside a Git work tree: {exc.message}",
            command=exc.command,
            returncode=exc.returncode,
            stderr=exc.stderr,
            input_error=True,
            target_files=["--workspace-root"],
            fix=TOPLEVEL_FIX,
        ) from exc
    text = os.fsdecode(output.rstrip(b"\n"))
    if not text:
        raise GitError(
            f"{start} is not inside a Git work tree (a bare repository has none)",
            input_error=True,
            target_files=["--workspace-root"],
            fix=TOPLEVEL_FIX,
        )
    return Path(text).resolve()


def git_toplevel(start: Path) -> Path | None:
    """``require_git_toplevel(start)``, or ``None`` when ``start`` is not inside a Git work tree."""
    try:
        return require_git_toplevel(start)
    except GitError:
        return None


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


def read_toml(path: Path, display: str | None = None) -> dict[str, Any] | None:
    """Parse the TOML file at ``path``; ``None`` when it does not exist.

    Raises ``ConfigError`` (``CONFIG_INVALID``, targeting ``display``, default
    ``str(path)``) when the file exists but cannot be read, is not UTF-8 or is
    not valid TOML, including a dangling symlink or a directory in its place.
    """
    if not path.exists() and not path.is_symlink():
        return None
    name = display if display is not None else str(path)
    try:
        return tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid config {name}: {exc}", target_files=[name]) from exc


def read_project_config(root: Path) -> dict[str, Any]:
    """Parse ``root/.devkit/config.toml``; a missing file is ``{}``.

    Raises ``ConfigError`` (``CONFIG_INVALID``) as ``read_toml`` does. The
    tables are returned unvalidated; each area validates the tables it owns and
    reports a malformed one with its own ``ConfigError`` subclass.
    """
    return read_toml(root / CONFIG_PATH, CONFIG_PATH) or {}


def config_table[E: ConfigError](value: object, context: str, error: type[E]) -> dict[str, Any]:
    """``value`` when it is a TOML table; otherwise raise ``error`` naming ``context`` (``config <context>: ...``)."""
    if not isinstance(value, dict):
        raise error(f"config {context}: expected a table")
    return value
