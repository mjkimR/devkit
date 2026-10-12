"""Managed hook wrappers in the repository's hooks directory.

Each wrapper is static: it execs the interpreter that installed it with
``-m agent_commit_gate run <stage>``, and the runner discovers gates at commit
time. Selecting a gate bundle and running ``devkit sync`` therefore changes what
runs without touching the hooks directory again.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from agent_advisory import AdvisoryError

from agent_commit_gate import git
from agent_commit_gate.models import Stage

MARKER = "# Managed by agent-commit-gate"
BACKUP_SUFFIX = ".pre-gate"
PYTHON_LINE = "python="


class HookState(StrEnum):
    MISSING = "missing"
    MANAGED = "managed"
    FOREIGN = "foreign"


@dataclass(frozen=True)
class HookStatus:
    stage: Stage
    path: Path
    state: HookState
    python: str | None = None  # interpreter a managed wrapper execs
    backup: bool = False

    @property
    def python_ok(self) -> bool:
        return self.python is not None and Path(self.python).is_file()


def wrapper_script(stage: Stage, python: str) -> str:
    # Blocking stages fail closed when the environment is gone; post-commit cannot undo the commit anyway.
    missing_exit = 1 if stage.blocking else 0
    return f"""#!/bin/sh
{MARKER}
{PYTHON_LINE}{shlex.quote(python)}
if [ ! -x "$python" ]; then
    echo "[commit-gate] {stage}: $python not found; run 'uv sync' in this repository" >&2
    exit {missing_exit}
fi
exec "$python" -m agent_commit_gate run {stage} "$@"
"""


def _hooks_dir(cwd: Path) -> Path:
    custom = git.config_value(cwd, "core.hooksPath")
    if custom:
        raise AdvisoryError.interaction(
            f"core.hooksPath is set to {custom!r}; managed hooks are only installed into the repository's own hooks directory",
            code="GATE_HOOKS_PATH_SET",
            what_to_report="Another tool owns the hooks directory. Ask whether to unset core.hooksPath.",
            fix="git config --unset core.hooksPath",
        )
    return git.hooks_dir(cwd)


def _read_python(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(PYTHON_LINE):
            parts = shlex.split(line[len(PYTHON_LINE) :])
            return parts[0] if parts else None
    return None


def status(cwd: Path) -> list[HookStatus]:
    directory = git.hooks_dir(cwd)
    result: list[HookStatus] = []
    for stage in Stage:
        path = directory / stage.value
        backup = path.with_name(path.name + BACKUP_SUFFIX).exists()
        if not path.exists():
            result.append(HookStatus(stage, path, HookState.MISSING, backup=backup))
            continue
        text = path.read_text("utf-8", errors="replace")
        if MARKER in text:
            result.append(HookStatus(stage, path, HookState.MANAGED, _read_python(text), backup))
        else:
            result.append(HookStatus(stage, path, HookState.FOREIGN, backup=backup))
    return result


def install(cwd: Path, python: str, *, force: bool = False) -> list[str]:
    """Write a wrapper for every stage. Foreign hooks are refused unless ``force`` moves them aside."""
    directory = _hooks_dir(cwd)
    current = status(cwd)
    foreign = [item for item in current if item.state is HookState.FOREIGN]
    if foreign and not force:
        raise AdvisoryError.interaction(
            f"hooks not managed by agent-commit-gate exist: {', '.join(item.stage.value for item in foreign)}",
            *(str(item.path) for item in foreign),
            code="GATE_FOREIGN_HOOK",
            what_to_report="Existing hooks would be replaced. Ask whether to move them aside.",
            fix=f"commit-gate install --force  (moves them to <hook>{BACKUP_SUFFIX})",
        )
    blocked = [item for item in foreign if item.backup]
    if blocked:
        raise AdvisoryError.interaction(
            f"backup already exists for: {', '.join(item.stage.value for item in blocked)}",
            *(str(item.path.with_name(item.path.name + BACKUP_SUFFIX)) for item in blocked),
            code="GATE_BACKUP_EXISTS",
            what_to_report="An earlier backup would be overwritten. Ask the user how to resolve it.",
        )
    directory.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []
    for item in current:
        if item.state is HookState.FOREIGN:
            item.path.rename(item.path.with_name(item.path.name + BACKUP_SUFFIX))
            actions.append(f"{item.stage}: moved existing hook to {item.path.name}{BACKUP_SUFFIX}")
        item.path.write_text(wrapper_script(item.stage, python), "utf-8")
        item.path.chmod(0o755)
        actions.append(f"{item.stage}: installed")
    return actions


def uninstall(cwd: Path) -> list[str]:
    """Remove managed wrappers and restore any hook ``install --force`` moved aside."""
    actions: list[str] = []
    for item in status(cwd):
        if item.state is not HookState.MANAGED:
            continue
        item.path.unlink()
        actions.append(f"{item.stage}: removed")
        backup = item.path.with_name(item.path.name + BACKUP_SUFFIX)
        if backup.exists():
            backup.rename(item.path)
            actions.append(f"{item.stage}: restored {backup.name}")
    return actions
