"""Locate a devkit project and read its configuration files.

Two roots, kept apart by name:

- the repository root: the top level of the Git work tree (``require_git_toplevel``), which Git operations use;
- the devkit root: the directory holding ``.devkit/`` (``find_project_root``), which configuration, the receipt and
  managed files are read from.

Inside a Git work tree the two are the same directory: a ``.devkit/`` below the top level is not a project of its
own. Outside Git the devkit root is the nearest directory with ``.devkit/``.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from devkit.core.errors import ArgumentError, ConfigError, GitError, UnsafePathError
from devkit.core.git import run_git
from devkit.core.receipt import CONFIG_PATH

DEVKIT_DIR = ".devkit"
TOPLEVEL_FIX = "Run from inside the repository, or pass --workspace-root/-w a directory inside it"


def require_git_toplevel(start: Path) -> Path:
    """The resolved top-level directory of the Git work tree containing ``start``.

    Raises ``GitError`` (``GIT_FAILED``, an input error naming
    ``--workspace-root``, with Git's standard error in the message) when Git
    ran and refused ``start``: not inside a work tree, or a repository Git
    will not use (``safe.directory``). When Git produced no exit status (not
    installed, timed out) ``run_git``'s ``GitError`` passes through unchanged.
    """
    try:
        output = run_git(start, "rev-parse", "--show-toplevel")
    except GitError as exc:
        if exc.returncode is None:
            raise
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


def _home() -> Path | None:
    try:
        return Path.home().resolve()
    except (RuntimeError, KeyError, OSError):  # no HOME and no password entry
        return None


def find_project_root(start: Path) -> Path:
    """The devkit root for ``start`` (a directory, or a file whose directory is used).

    Resolution, on the resolved ``start``:

    1. Inside a Git work tree, its top level: the repository root is the devkit root, and a ``.devkit`` directory
       below it is not a project of its own.
    2. Outside a Git work tree (or without Git), the nearest directory, ``start`` itself first and then each
       parent, that contains a ``.devkit`` directory. The walk stops below the user's home directory: the home
       directory and the directories above it are never searched, so a stray ``~/.devkit`` does not claim every
       directory under it (``start`` itself is always considered).
    3. Otherwise ``start`` itself.

    Raises ``UnsafePathError`` when ``start`` cannot be resolved (a symlink loop).
    """
    try:
        origin = start.resolve()
    except (RuntimeError, OSError) as exc:  # Python 3.12 raises RuntimeError for a symlink loop
        raise UnsafePathError(f"path cannot be resolved: {start}: {exc}") from exc
    if not origin.is_dir():
        origin = origin.parent
    toplevel = git_toplevel(origin)
    if toplevel is not None:
        return toplevel
    home = _home()
    for candidate in (origin, *origin.parents):
        if home is not None and candidate != origin and home.is_relative_to(candidate):
            break
        if (candidate / DEVKIT_DIR).is_dir():
            return candidate
    return origin


def require_devkit_root(root: Path, param: str = "--workspace-root") -> Path:
    """``root`` resolved, when it can be a devkit root: outside Git, or the top level of its Git work tree.

    Raises ``ArgumentError`` naming ``param`` for a directory below the top level of a Git work tree, since the
    repository root is the devkit root there.
    """
    root = root.resolve()
    toplevel = git_toplevel(root)
    if toplevel is not None and toplevel != root:
        raise ArgumentError(
            f"{param} {root} is inside the Git work tree {toplevel}; the devkit root is the repository's top level",
            target_files=[param],
            fix=f"Pass {param} {toplevel}, or omit it to use the repository of the current directory",
        )
    return root


def read_toml(path: Path, display: str | None = None) -> dict[str, Any] | None:
    """Parse the TOML file at ``path``; ``None`` when it does not exist.

    Raises ``ConfigError`` (``CONFIG_INVALID``, targeting ``display``, default
    ``str(path)``) when the file exists but cannot be read, is not UTF-8 or is
    not valid TOML, including a dangling symlink or a directory in its place.
    """
    name = display if display is not None else str(path)
    try:
        if not path.exists() and not path.is_symlink():
            return None
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
