"""Locate a devkit project and read its configuration files.

Two roots, kept apart by name:

- the repository root: the top level of the Git work tree (``require_git_toplevel``), which Git operations use;
- the devkit root: the directory holding ``.devkit/`` (``find_project_root``), which configuration, the receipt and
  managed files are read from.

Inside a Git work tree the two are the same directory: a ``.devkit/`` below the top level is not a project of its
own, and one below a top level that has none is refused (``DevkitRootNestedError``) rather than ignored. Outside Git
the devkit root is the nearest directory with ``.devkit/``.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from devkit_core.base.errors import ArgumentError, GitError, UnsafePathError
from devkit_core.core.git import run_git

from devkit_dist.base.errors import ConfigError, DevkitRootNestedError
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH

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


def _nested_devkit(origin: Path, toplevel: Path) -> Path | None:
    """The nearest directory from ``origin`` up to, not including, ``toplevel`` that holds a ``.devkit``
    directory, when ``toplevel`` holds none; else ``None``."""
    if (toplevel / DEVKIT_DIR).is_dir():
        return None
    for candidate in (origin, *origin.parents):
        if candidate == toplevel or not candidate.is_relative_to(toplevel):
            break
        if (candidate / DEVKIT_DIR).is_dir():
            return candidate
    return None


def _nested_error(nested: Path, toplevel: Path) -> DevkitRootNestedError:
    return DevkitRootNestedError(
        f"{nested} holds {DEVKIT_DIR}/ but is inside the Git work tree {toplevel}, whose top level has none; "
        "inside a Git work tree the devkit root is the repository's top level",
        target_files=[str(nested / DEVKIT_DIR)],
        fix=f"Make {nested} a Git repository of its own (git init), or move {nested / DEVKIT_DIR} to {toplevel}",
    )


def find_project_root(start: Path) -> Path:
    """The devkit root for ``start`` (a directory, or a file whose directory is used).

    Resolution, on the resolved ``start``:

    1. Inside a Git work tree, its top level: the repository root is the devkit root, and a ``.devkit`` directory
       below it is not a project of its own. When the top level has no ``.devkit`` directory but ``start`` or a
       directory between it and the top level has one, ``DevkitRootNestedError`` (``DEVKIT_ROOT_NESTED``) names
       both: resolving to the top level would silently read no configuration, receipt or managed rules.
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
        nested = _nested_devkit(origin, toplevel)
        if nested is not None:
            raise _nested_error(nested, toplevel)
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

    For a directory below the top level of a Git work tree, raises ``DevkitRootNestedError``
    (``DEVKIT_ROOT_NESTED``) when it or a directory between it and the top level holds ``.devkit/`` and the top
    level does not, else ``ArgumentError`` naming ``param``, since the repository root is the devkit root there.
    That error's fix suggests the top level only when the top level holds ``.devkit/``.
    """
    root = root.resolve()
    toplevel = git_toplevel(root)
    if toplevel is None or toplevel == root:
        return root
    nested = _nested_devkit(root, toplevel)
    if nested is not None:
        raise _nested_error(nested, toplevel)
    if (toplevel / DEVKIT_DIR).is_dir():
        fix = f"Pass {param} {toplevel}, or omit it to use the repository of the current directory"
    else:
        fix = (
            f"Make {root} a Git repository of its own (git init) to use it as a devkit root, "
            f"or omit {param} to use the repository of the current directory"
        )
    raise ArgumentError(
        f"{param} {root} is inside the Git work tree {toplevel}; the devkit root is the repository's top level",
        target_files=[param],
        fix=fix,
    )


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


def commit_config(root: Path, sha: str) -> dict[str, Any] | None:
    """Parse the ``.devkit/config.toml`` committed at ``sha`` in the repository at ``root``; ``None`` when that commit
    does not track it.

    Raises ``ConfigError`` (``CONFIG_INVALID``) when the committed file is not UTF-8 or not valid TOML, and
    ``GitError`` when Git cannot read the commit. Like ``read_project_config``, the tables are returned unvalidated.
    """
    if not run_git(root, "ls-tree", "--name-only", sha, "--", CONFIG_PATH).strip():
        return None
    try:
        return tomllib.loads(run_git(root, "show", f"{sha}:{CONFIG_PATH}").decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        name = f"{CONFIG_PATH} at commit {sha[:12]}"
        raise ConfigError(f"invalid config {name}: {exc}", target_files=[CONFIG_PATH]) from exc


def config_table[E: ConfigError](value: object, context: str, error: type[E]) -> dict[str, Any]:
    """``value`` when it is a TOML table; otherwise raise ``error`` naming ``context`` (``config <context>: ...``)."""
    if not isinstance(value, dict):
        raise error(f"config {context}: expected a table")
    return value
