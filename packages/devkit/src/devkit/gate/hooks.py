"""Managed hook wrappers in the repository's hooks directory.

The hooks directory is always ``<common-git-dir>/hooks``, shared by every
worktree; ``install``, ``status`` and ``uninstall`` all use it. When
``core.hooksPath`` points Git elsewhere, ``install`` refuses and ``status``
reports the setting, because wrappers in the common hooks directory would not
run.

Each wrapper is static. On every commit it:

1. runs ``<hook>.pre-gate`` first when that file exists and is executable (the
   hook ``install --force`` moved aside), and stops when a blocking stage's
   hook fails;
2. picks the interpreter: the work tree's ``.venv/bin/python`` when ``devkit``
   is installed in it, otherwise the absolute interpreter recorded at install
   time, and exits ``2`` on a blocking stage when neither exists;
3. execs ``<python> -P -m devkit.gate run <stage>`` (``-P`` keeps repository
   files from shadowing standard library modules).

The runner discovers gates at commit time, so selecting a gate bundle and
running ``devkit sync`` changes what runs without touching the hooks directory.
Symbolic links are never written through: a hook that is a link (even a
dangling one) is foreign, and wrappers replace files atomically.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from devkit.advisory import AdvisoryError, ExitCode
from devkit.gate import git
from devkit.gate.models import Stage

MARKER = "# Managed by devkit gate"
BACKUP_SUFFIX = ".pre-gate"
PYTHON_LINE = "python="
HOOKS_PATH_KEY = "core.hooksPath"
_PYTHON_CHECK_TIMEOUT = 60.0


class HookState(StrEnum):
    MISSING = "missing"
    MANAGED = "managed"
    FOREIGN = "foreign"  # an executable hook, a symbolic link, or anything that is not a regular file
    INERT = "inert"  # a regular file Git ignores because it is not executable


@dataclass(frozen=True)
class HookStatus:
    stage: Stage
    path: Path
    state: HookState
    python: str | None = None  # interpreter a managed wrapper records
    backup: bool = False

    @property
    def python_ok(self) -> bool:
        if self.python is None:
            return False
        path = Path(self.python)
        return path.is_absolute() and path.is_file() and os.access(path, os.X_OK)


@dataclass(frozen=True)
class HooksLocation:
    directory: Path  # ``<common-git-dir>/hooks``
    hooks_path: str | None = None  # ``core.hooksPath`` when it sends Git to another directory


def _present(path: Path) -> bool:
    return path.is_symlink() or path.exists()


def _backup(path: Path) -> Path:
    return path.with_name(path.name + BACKUP_SUFFIX)


def locate(cwd: Path) -> HooksLocation:
    """The managed hooks directory and the ``core.hooksPath`` override that bypasses it, if any."""
    directory = git.common_git_dir(cwd) / "hooks"
    custom = git.config_value(cwd, HOOKS_PATH_KEY)
    if custom:
        # Git runs hooks from the work tree's top level, so a relative value is relative to it.
        candidate = Path(custom).expanduser()
        if not candidate.is_absolute():
            candidate = git.repo_root(cwd) / candidate
        if candidate.resolve() == directory.resolve():
            custom = None
    return HooksLocation(directory, custom)


def wrapper_script(stage: Stage, python: str) -> str:
    """The wrapper for one stage. ``python`` is the absolute fallback interpreter (POSIX separators)."""
    # Blocking stages fail closed with ERROR (the gates could not run) when no interpreter is found;
    # post-commit cannot undo the commit anyway.
    missing_exit = int(ExitCode.ERROR) if stage.blocking else int(ExitCode.OK)
    chained = f'"$0{BACKUP_SUFFIX}" "$@"' + (" || exit $?" if stage.blocking else "")
    return f"""#!/bin/sh
{MARKER}
{PYTHON_LINE}{shlex.quote(python)}
if [ -x "$0{BACKUP_SUFFIX}" ]; then
    {chained}
fi
top=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$top" ]; then
    candidate="$top/.venv/bin/python"
    if [ -x "$candidate" ]; then
        for info in "$top"/.venv/lib/python*/site-packages/devkit-*.dist-info; do
            if [ -d "$info" ]; then
                python=$candidate
                break
            fi
        done
    fi
fi
if [ ! -x "$python" ]; then
    echo "[devkit gate] {stage}: no interpreter with devkit found ($python); run 'uv sync' in this repository" >&2
    exit {missing_exit}
fi
exec "$python" -P -m devkit.gate run {stage} "$@"
"""


def _read_python(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(PYTHON_LINE):
            parts = shlex.split(line[len(PYTHON_LINE) :])
            return parts[0] if parts else None
    return None


def _state(path: Path) -> tuple[HookState, str | None]:
    if not _present(path):
        return HookState.MISSING, None
    if path.is_symlink() or not path.is_file():
        return HookState.FOREIGN, None
    try:
        text = path.read_text("utf-8", errors="replace")
    except OSError:
        return HookState.FOREIGN, None
    if MARKER in text:
        return HookState.MANAGED, _read_python(text)
    if not os.access(path, os.X_OK):
        return HookState.INERT, None
    return HookState.FOREIGN, None


def status(cwd: Path, location: HooksLocation | None = None) -> list[HookStatus]:
    directory = (location or locate(cwd)).directory
    result: list[HookStatus] = []
    for stage in Stage:
        path = directory / stage.value
        state, python = _state(path)
        result.append(HookStatus(stage, path, state, python, _present(_backup(path))))
    return result


def check_python(python: str) -> str:
    """The absolute form of ``python`` (POSIX separators) after checking it can import ``devkit.gate``."""
    candidate = Path(os.path.abspath(Path(python).expanduser()))
    fix = "devkit gate install --python <interpreter of an environment where devkit is installed>"
    if not (candidate.is_file() and os.access(candidate, os.X_OK)):
        raise AdvisoryError.invalid_input(
            f"--python {python}: not an executable file", code="GATE_PYTHON_INVALID", fix=fix, target_files=["--python"]
        )
    try:
        completed = subprocess.run(
            [str(candidate), "-P", "-c", "import devkit.gate"],
            capture_output=True,
            text=True,
            check=False,
            timeout=_PYTHON_CHECK_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdvisoryError.invalid_input(
            f"--python {python}: cannot be run: {exc}", code="GATE_PYTHON_INVALID", fix=fix, target_files=["--python"]
        ) from exc
    if completed.returncode != 0:
        last = (completed.stderr.strip().splitlines() or [f"exit status {completed.returncode}"])[-1]
        raise AdvisoryError.invalid_input(
            f"--python {python}: cannot import devkit.gate",
            last,
            code="GATE_PYTHON_INVALID",
            fix=fix,
            target_files=["--python"],
        )
    return candidate.as_posix()


def _write(path: Path, text: str) -> None:
    """Replace ``path`` with an executable LF-only file without following a link at ``path``."""
    temporary = path.with_name(f".{path.name}.devkit-{os.getpid()}")
    try:
        temporary.write_bytes(text.encode("utf-8"))
        temporary.chmod(0o755)
        os.replace(temporary, path)
    finally:
        if _present(temporary):
            temporary.unlink()


def _refuse_hooks_path(location: HooksLocation) -> None:
    if location.hooks_path:
        raise AdvisoryError.interaction(
            f"{HOOKS_PATH_KEY} is set to {location.hooks_path!r}; managed hooks are only installed into "
            f"{location.directory}, which Git would not run",
            code="GATE_HOOKS_PATH_SET",
            what_to_report="Another tool owns the hooks directory. Ask whether to unset core.hooksPath.",
            fix=f"git config --unset {HOOKS_PATH_KEY}",
        )


def install(cwd: Path, python: str, *, force: bool = False) -> list[str]:
    """Write a wrapper for every stage.

    Foreign hooks are refused unless ``force`` moves them to ``<hook>.pre-gate``,
    where the wrapper keeps running them first. Inert (non-executable) hooks,
    which Git ignores, are moved aside without ``force``. ``python`` is checked
    and recorded as an absolute path.
    """
    location = locate(cwd)
    _refuse_hooks_path(location)
    recorded = check_python(python)
    current = status(cwd, location)
    foreign = [item for item in current if item.state is HookState.FOREIGN]
    if foreign and not force:
        raise AdvisoryError.interaction(
            f"hooks not managed by devkit gate exist: {', '.join(item.stage.value for item in foreign)}",
            *(str(item.path) for item in foreign),
            code="GATE_FOREIGN_HOOK",
            what_to_report=(
                "Existing hooks would be moved aside; the managed wrapper keeps running them before the gates. "
                "Ask whether to proceed."
            ),
            fix=f"devkit gate install --force  (moves them to <hook>{BACKUP_SUFFIX})",
        )
    moving = [item for item in current if item.state in (HookState.FOREIGN, HookState.INERT)]
    blocked = [item for item in moving if item.backup]
    if blocked:
        raise AdvisoryError.interaction(
            f"backup already exists for: {', '.join(item.stage.value for item in blocked)}",
            *(str(_backup(item.path)) for item in blocked),
            code="GATE_BACKUP_EXISTS",
            what_to_report="An earlier backup would be overwritten. Ask the user how to resolve it.",
        )
    location.directory.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []
    for item in current:
        if item in moving:
            os.rename(item.path, _backup(item.path))
            kind = "inert (non-executable) hook" if item.state is HookState.INERT else "existing hook"
            actions.append(f"{item.stage}: moved {kind} to {item.path.name}{BACKUP_SUFFIX}")
        _write(item.path, wrapper_script(item.stage, recorded))
        actions.append(f"{item.stage}: installed")
    return actions


def uninstall(cwd: Path) -> list[str]:
    """Remove managed wrappers and restore any hook ``install`` moved aside.

    Works on the common hooks directory even when ``core.hooksPath`` is set.
    """
    location = locate(cwd)
    actions: list[str] = []
    for item in status(cwd, location):
        if item.state is not HookState.MANAGED:
            continue
        item.path.unlink()
        actions.append(f"{item.stage}: removed")
        backup = _backup(item.path)
        if _present(backup):
            os.rename(backup, item.path)
            actions.append(f"{item.stage}: restored {backup.name}")
    return actions
