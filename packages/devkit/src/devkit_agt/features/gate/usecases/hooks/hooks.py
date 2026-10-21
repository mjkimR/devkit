"""Shared POSIX hook dispatchers and independently managed devkit entries."""

from __future__ import annotations

import os
import shlex
import subprocess
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from devkit.advisory import AdvisoryError, Level
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import atomic_write_bytes, file_lock
from devkit_dist.features.project.repositories.project import require_git_toplevel

import devkit_agt.features.gate.repositories.git as git
from devkit_agt.features.gate.models.contracts import Stage
from devkit_agt.features.gate.models.errors import (
    ForeignHookError,
    GateInterpreterError,
    GatePythonError,
    HookBackupExistsError,
    HookEntryMissingNotice,
    HookLayoutError,
    HookPreservedNotice,
    HookScriptFailedNotice,
    HooksPathSetError,
)
from devkit_agt.features.gate.usecases.runner import GateProject, load_gate_project

MARKER = "# Managed by devkit hook dispatcher"
GATE_MARKER = "# Managed by devkit gate"
LEGACY_MARKER = "# Managed by devkit legacy adapter"
BACKUP_SUFFIX = ".legacy"
DEVKIT_ENTRY = "20-devkit"
LEGACY_ENTRY = "00-legacy"
PYTHON_LINE = "python="
HOOKS_PATH_KEY = "core.hooksPath"
LOCK_FILE = "devkit-hooks.lock"
_PYTHON_CHECK_TIMEOUT = 60.0
# Ends the quoted here-document a generated script prints an advisory block with.
_ADVISORY_DELIMITER = "DEVKIT_ADVISORY"


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
    python: str | None = None  # fallback recorded by the managed 20-devkit entry, absent on empty stages
    backup: bool = False
    scripts: tuple[str, ...] = ()

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
    hooks_path_scope: str | None = None  # the configuration scope that sets ``hooks_path``


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
            candidate = require_git_toplevel(cwd) / candidate
        if candidate.resolve() == directory.resolve():
            custom = None
    return HooksLocation(directory, custom, git.config_scope(cwd, HOOKS_PATH_KEY) if custom else None)


def _advisory_block(error: AdvisoryError) -> str:
    """``error``'s sentinel block, as a generated script prints it, one ``\\n``-terminated line each."""
    return "".join(f"{line}\n" for line in error.lines())


def dispatcher_script(stage: Stage) -> str:
    """Run executable direct children in bytewise filename order, without changing the Git environment.

    ``post-commit`` reports a failed script as ``GATE_HOOK_SCRIPT_FAILED``, rendered here by the advisory
    library; the script path and exit status follow as ``[DETAIL]`` lines at run time.
    """
    failure = 'exit "$code"' if stage.blocking else 'report_failure "$script" "$code"'
    failed = _advisory_block(HookScriptFailedNotice("hook script failed"))
    # A function keeps the original hook arguments separate from the script path.
    return f"""#!/bin/sh
{MARKER}
run_script() {{
    script=$1
    shift
    [ -f "$script" ] && [ -x "$script" ] || return 0
    "$script" "$@"
    code=$?
    if [ "$code" -ne 0 ]; then
        {failure}
    fi
}}
report_failure() {{
    cat >&2 <<'{_ADVISORY_DELIMITER}'
{failed}{_ADVISORY_DELIMITER}
    printf '[DETAIL] stage={stage} script=%s exit=%s\\n' "$1" "$2" >&2
}}
if [ "${{LC_ALL+x}}" = x ]; then
    saved_lc_all=$LC_ALL
    had_lc_all=yes
else
    had_lc_all=no
fi
LC_ALL=C
export LC_ALL
for entry in "$0.d"/*; do
    if [ "$had_lc_all" = yes ]; then
        LC_ALL=$saved_lc_all
        export LC_ALL
    else
        unset LC_ALL
    fi
    run_script "$entry" "$@"
done
exit 0
"""


def legacy_script(stage: Stage) -> str:
    return f"""#!/bin/sh
{LEGACY_MARKER}
legacy="$(dirname "$0")/../{stage}{BACKUP_SUFFIX}"
if [ -f "$legacy" ] && [ -x "$legacy" ]; then
    exec "$legacy" "$@"
fi
exit 0
"""


def _unavailable(stage: Stage) -> GateInterpreterError:
    """The advisory a ``20-devkit`` entry prints when no interpreter can import ``devkit_agt.features.gate``."""
    error = GateInterpreterError(f"{stage}: no interpreter can import devkit_agt.features.gate; the gates did not run")
    return error if stage.blocking else error.with_level(Level.WARNING)


def _bootstrap(block: str, code: int) -> str:
    """``python -m devkit_agt.features.gate`` in the same process, reporting a failed import as the advisory ``block``.

    One interpreter start-up per hook: the import is checked where the stage runs, rather than in a
    second process first. Without it, an interpreter that cannot import devkit exits ``1`` with a
    traceback, which reads as gates refusing the commit.
    """
    return f"""import runpy, sys
try:
    import devkit_agt.features.gate.cli
except Exception as exc:
    reason = (str(exc).splitlines() or [""])[0]
    sys.stderr.write({block!r} + "[DETAIL] python=" + sys.executable + "\\n[DETAIL] " + type(exc).__name__ + ": " + reason + "\\n")
    sys.exit({code})
sys.argv[1:1] = ["run"]
runpy.run_module("devkit_agt.features.gate", run_name="__main__", alter_sys=True)
"""


def wrapper_script(stage: Stage, python: str) -> str:
    """The ``20-devkit`` entry, with an absolute fallback interpreter.

    When the selected interpreter is missing or cannot import ``devkit_agt.features.gate``, the entry prints
    ``GATE_INTERPRETER_UNAVAILABLE`` and exits ``2`` in a blocking stage, ``0`` in ``post-commit``.
    """
    unavailable = _unavailable(stage)
    code = int(unavailable.exit_code)
    block = _advisory_block(unavailable)
    return f"""#!/bin/sh
{GATE_MARKER}
{PYTHON_LINE}{shlex.quote(python)}
top=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$top" ]; then
    candidate="$top/.venv/bin/python"
    if [ -x "$candidate" ]; then
        for info in "$top"/.venv/lib/python*/site-packages/devkit_agt-*.dist-info; do
            if [ -d "$info" ]; then
                python=$candidate
                break
            fi
        done
    fi
fi
if [ ! -x "$python" ]; then
    cat >&2 <<'{_ADVISORY_DELIMITER}'
{block}{_ADVISORY_DELIMITER}
    printf '[DETAIL] python=%s\\n[DETAIL] not an executable file\\n' "$python" >&2
    exit {code}
fi
bootstrap={shlex.quote(_bootstrap(block, code))}
exec "$python" -P -c "$bootstrap" {stage} "$@"
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
    if MARKER in text.splitlines():
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
        entries = path.with_name(path.name + ".d")
        scripts = tuple(sorted(child.name for child in entries.iterdir())) if entries.is_dir() else ()
        entry = entries / DEVKIT_ENTRY
        if state is HookState.MANAGED:
            python = _read_python(entry.read_text("utf-8", errors="replace")) if entry.is_file() else None
        result.append(HookStatus(stage, path, state, python, _present(_backup(path)), scripts))
    return result


def _enabled_gates(project: GateProject, stage: Stage) -> list[str]:
    return [gate.id for gate in project.registry.for_stage(stage) if project.config.enabled(gate)]


def missing_entry_notices(
    project: GateProject, statuses: Sequence[HookStatus], location: HooksLocation | None = None
) -> list[AdvisoryError]:
    """Warnings for enabled gates that do not run at commit time.

    A stage's gates run only through its managed dispatcher and that dispatcher's ``20-devkit`` entry,
    which ``install`` writes for the stages with enabled gates when it runs: one ``GATE_HOOK_ENTRY_MISSING``
    per stage without them (a gate of another stage enabled later in the configuration does not run until
    the next install or sync). When ``location`` has a ``core.hooksPath`` that sends Git elsewhere, no
    managed hook runs at all, and ``install`` refuses: one ``GATE_HOOKS_PATH_SET`` warning names every
    enabled gate instead, with the fix that clears the setting.
    """
    if location is not None and location.hooks_path:
        gates = [gate for stage in Stage for gate in _enabled_gates(project, stage)]
        if not gates:
            return []
        notice = _hooks_path_error(location, f"gates={','.join(gates)}", prefix="enabled gates do not run: ")
        return [notice.with_level(Level.WARNING)]
    by_stage = {item.stage: item for item in statuses}
    notices: list[AdvisoryError] = []
    for stage in Stage:
        gates = _enabled_gates(project, stage)
        item = by_stage.get(stage)
        if not gates or item is None:
            continue
        entry = _entries(item.path) / DEVKIT_ENTRY
        if item.state is not HookState.MANAGED:
            problem = f"the {stage} hook is not a devkit dispatcher ({item.state})"
        elif not (_owned(entry, GATE_MARKER) and os.access(entry, os.X_OK)):
            problem = f"{entry.parent.name}/{DEVKIT_ENTRY} is not installed"
        else:
            continue
        notices.append(
            HookEntryMissingNotice(
                f"{stage}: enabled gates do not run: {problem}",
                f"gates={','.join(gates)}",
                target_files=[str(entry)],
            )
        )
    return notices


def check_python(python: str) -> str:
    """The absolute form of ``python`` (POSIX separators) after checking it can import ``devkit_agt.features.gate``."""
    candidate = Path(os.path.abspath(Path(python).expanduser()))
    if not (candidate.is_file() and os.access(candidate, os.X_OK)):
        raise GatePythonError(f"--python {python}: not an executable file")
    try:
        completed = subprocess.run(
            [str(candidate), "-P", "-c", "import devkit_agt.features.gate"],
            capture_output=True,
            text=True,
            check=False,
            timeout=_PYTHON_CHECK_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GatePythonError(f"--python {python}: cannot be run: {exc}") from exc
    if completed.returncode != 0:
        last = (completed.stderr.strip().splitlines() or [f"exit status {completed.returncode}"])[-1]
        raise GatePythonError(f"--python {python}: cannot import devkit_agt.features.gate", last)
    return candidate.as_posix()


def _write(path: Path, text: str) -> None:
    """Replace ``path`` with an executable (``0o755``) LF-only file without following a link at ``path``."""
    data = text.encode("utf-8")
    if path.is_file() and not path.is_symlink() and path.read_bytes() == data and os.access(path, os.X_OK):
        return
    atomic_write_bytes(path, data, mode=0o755)


def _hooks_path_fix(location: HooksLocation) -> str:
    """The step that stops ``core.hooksPath`` bypassing the managed directory, by the scope that sets it."""
    scope = location.hooks_path_scope
    if scope == "local":
        step = f"run `git config --unset {HOOKS_PATH_KEY}`"
    elif scope == "worktree":
        step = f"run `git config --worktree --unset {HOOKS_PATH_KEY}`"
    elif scope == "command":
        step = f"remove {HOOKS_PATH_KEY} from the `git -c` options or GIT_CONFIG_* environment variables"
    else:  # global or system: override it for this repository only, leaving other repositories untouched
        step = f"run `git config {HOOKS_PATH_KEY} {shlex.quote(location.directory.as_posix())}`"
    return f"Once the user agrees, {step}, then `devkit gate install`"


def _hooks_path_error(location: HooksLocation, *details: str, prefix: str = "") -> HooksPathSetError:
    """``GATE_HOOKS_PATH_SET`` for the ``core.hooksPath`` of ``location``, its message after ``prefix``."""
    scope = f" ({location.hooks_path_scope} config)" if location.hooks_path_scope else ""
    return HooksPathSetError(
        f"{prefix}{HOOKS_PATH_KEY} is set to {location.hooks_path!r}{scope}; managed hooks are only installed into "
        f"{location.directory}, which Git would not run",
        *details,
        fix=_hooks_path_fix(location),
    )


def _refuse_hooks_path(location: HooksLocation) -> None:
    if location.hooks_path:
        raise _hooks_path_error(location)


@dataclass
class InstallResult:
    actions: list[str] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)


@contextmanager
def clone_lock(common_git_dir: Path) -> Iterator[None]:
    """Serialize hook and ``devkit.config`` template mutations across linked worktrees of the same clone.

    An exclusive ``devkit_core.core.file_lock`` on ``<common_git_dir>/devkit-hooks.lock``, waited for without
    a bound and held until the block ends. A lock file that is a symlink or not a regular file is
    ``UnsafePathError`` (``PATH_UNSAFE``).
    """
    with file_lock(common_git_dir / LOCK_FILE):
        yield


def _owned(path: Path, marker: str) -> bool:
    return path.is_file() and not path.is_symlink() and marker in path.read_text("utf-8", errors="replace").splitlines()


def _entries(path: Path) -> Path:
    return path.with_name(path.name + ".d")


class InstallHooksUseCase(BaseUseCase):
    """Application entrypoint for install."""

    def execute(self, cwd: Path, python: str, *, force: bool = False, preserve_python: bool = False) -> InstallResult:
        """Install dispatchers and ``20-devkit`` entries, preserving regular foreign hooks automatically.

        ``force`` also permits moving symlinks or non-regular hooks. Preflight all stages before writing;
        reserved entry collisions, existing backups and custom ``core.hooksPath`` are always refused.
        Automatic sync uses ``preserve_python`` to retain each valid existing fallback under the clone lock.
        """
        location = locate(cwd)
        _refuse_hooks_path(location)
        recorded = check_python(python)
        project = load_gate_project(cwd)
        # Invalid configuration must still be reported by the hooks, rather than silently bypassed.
        stages = (
            set(Stage)
            if not project.validation.ok
            else {gate.stage for gate in project.registry.get_all() if project.config.enabled(gate)}
        )
        with clone_lock(location.directory.parent):
            current = status(cwd, location)
            moving = [item for item in current if item.state in (HookState.FOREIGN, HookState.INERT)]
            special = [item for item in moving if item.path.is_symlink() or not item.path.is_file()]
            if special and not force:
                raise ForeignHookError(
                    "hooks are symbolic links or non-regular files",
                    *(str(item.path) for item in special),
                    fix="Inspect the existing hooks, then run `devkit gate install --force` to preserve and chain them",
                )
            blocked = [item for item in moving if item.backup]
            if blocked:
                raise HookBackupExistsError(
                    "legacy hook backup already exists",
                    *(str(_backup(item.path)) for item in blocked),
                    fix="Move the conflicting legacy backups to another path, then run `devkit sync`",
                )
            if location.directory.is_symlink():
                raise HookLayoutError("hooks directory is a symbolic link", str(location.directory))
            for item in current:
                entries = _entries(item.path)
                if entries.is_symlink() or (_present(entries) and not entries.is_dir()):
                    raise HookLayoutError("hook script directory is not a regular directory", str(entries))
                for name, marker in ((DEVKIT_ENTRY, GATE_MARKER), (LEGACY_ENTRY, LEGACY_MARKER)):
                    entry = entries / name
                    if _present(entry) and not _owned(entry, marker):
                        raise HookLayoutError("reserved hook entry is not managed by devkit", str(entry))
            fallbacks: dict[str, str] = {}
            if preserve_python:
                for item in current:
                    if item.python and item.python not in fallbacks:
                        try:
                            fallbacks[item.python] = check_python(item.python)
                        except GatePythonError:
                            fallbacks[item.python] = recorded
            location.directory.mkdir(parents=True, exist_ok=True)
            result = InstallResult()
            for item in current:
                entries = _entries(item.path)
                entries.mkdir(exist_ok=True)
                if item in moving or _present(_backup(item.path)):
                    _write(entries / LEGACY_ENTRY, legacy_script(item.stage))
                if item.stage in stages:
                    _write(
                        entries / DEVKIT_ENTRY, wrapper_script(item.stage, fallbacks.get(item.python or "", recorded))
                    )
                if item in moving:
                    os.rename(item.path, _backup(item.path))
                try:
                    _write(item.path, dispatcher_script(item.stage))
                except OSError:
                    if item in moving:
                        os.rename(_backup(item.path), item.path)
                    raise
                if item in moving:
                    kind = "inert (non-executable) hook" if item.state is HookState.INERT else "existing hook"
                    result.actions.append(f"{item.stage}: moved {kind} to {item.path.name}{BACKUP_SUFFIX}")
                    result.notices.append(
                        HookPreservedNotice(
                            f"existing {item.stage} hook preserved at {_backup(item.path)}",
                            f"The preserved hook runs first through {entries / LEGACY_ENTRY}; its executable mode is unchanged",
                            target_files=[str(_backup(item.path))],
                        )
                    )
                result.actions.append(f"{item.stage}: installed")
            return result


install = InstallHooksUseCase().execute


class UninstallHooksUseCase(BaseUseCase):
    """Application entrypoint for uninstall."""

    def execute(self, cwd: Path) -> list[str]:
        """Remove owned devkit entries; retain the dispatcher and legacy adapter while user entries remain."""
        location = locate(cwd)
        actions: list[str] = []
        with clone_lock(location.directory.parent):
            for item in status(cwd, location):
                if item.state is not HookState.MANAGED:
                    continue
                entries = _entries(item.path)
                if entries.is_symlink() or (_present(entries) and not entries.is_dir()):
                    raise HookLayoutError("hook script directory is not a regular directory", str(entries))
                entry = entries / DEVKIT_ENTRY
                if _owned(entry, GATE_MARKER):
                    entry.unlink()
                    actions.append(f"{item.stage}: removed {DEVKIT_ENTRY}")
                legacy = entries / LEGACY_ENTRY
                remaining = list(entries.iterdir()) if entries.exists() else []
                if any(child != legacy or not _owned(legacy, LEGACY_MARKER) for child in remaining):
                    actions.append(f"{item.stage}: retained dispatcher for user scripts")
                    continue
                if _owned(legacy, LEGACY_MARKER):
                    legacy.unlink()
                if entries.exists():
                    entries.rmdir()
                item.path.unlink()
                actions.append(f"{item.stage}: removed")
                backup = _backup(item.path)
                if _present(backup):
                    os.rename(backup, item.path)
                    actions.append(f"{item.stage}: restored {backup.name}")
        return actions
