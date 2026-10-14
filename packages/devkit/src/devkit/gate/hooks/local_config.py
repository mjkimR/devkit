"""The commented settings template in the clone-local ``<common-git-dir>/devkit.config``.

``devkit gate install`` and every
``devkit sync`` (through the ``devkit.post_sync`` extension ``post_sync``) make sure
the file names every installed gate: one commented ``[gates.settings.<id>]``
table per gate, with ``enabled`` and each settings field at its default, its
type and the field's ``metadata["help"]`` when the gate declares one.

An uncommented key replaces the value ``.devkit/config.toml`` gives it, arrays
as a whole, so the header tells the developer to uncomment a table's header and
only the keys they change. A key the project config sets when the table is
written is not offered at its default (uncommenting it would drop the team's
value, such as the ``verify-commands`` commands, and silently weaken the gate):
it is a prose line naming it as set by ``.devkit/config.toml``. Its value is
not copied, since the table is never rewritten and a copy would go stale. A
key the project config only starts setting later still shows its default; the
instruction to uncomment only what changes is what keeps it in effect.

Prose is commented twice (``##``) and settings once (``#``), so uncommenting a
whole table in an editor leaves the prose a comment and yields valid TOML; the
keys are indented under their header, which must be uncommented with them.

The file belongs to the developer. A missing file is created; an existing one
only gets tables appended for gates it does not mention yet (commented or
not), so uncommenting a line in place is the way to change a setting and no
line is ever rewritten. The read and the write happen under the clone-wide
``devkit-hooks.lock`` (``hooks.clone_lock``), so syncs in linked worktrees of
one clone never append the same table twice or lose each other's tables.

A file devkit cannot safely append to (a symbolic link, not a regular file,
not UTF-8, cannot be written), or tables it cannot render because the
project's ``[gates]`` cannot be read, are left alone and reported as
``GateTemplateNotice`` (``GATE_CONFIG_TEMPLATE_SKIPPED``, a warning). The
template is never worth failing an install for: any other error refreshing it
is reported the same way, so the hook notices returned beside it (such as
``GATE_HOOK_PRESERVED``) always reach the user. A settings default that TOML
cannot represent is left out of its gate's table.
"""

from __future__ import annotations

import dataclasses
import os
import re
import sys
import typing
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomlkit

from devkit.advisory import AdvisoryError, as_advisory_error
from devkit.core import CONFIG_PATH, ConfigError, require_git_toplevel
from devkit.core.errors import GitError
from devkit.core.logs import get_logger
from devkit.gate.engine.config import ENABLED_KEY, LOCAL_CONFIG, GateEntry, GatesConfig, load_project_gates_config
from devkit.gate.engine.models import Gate
from devkit.gate.engine.registry import project_registry
from devkit.gate.errors import GateTemplateNotice, HookInstallSkippedNotice
from devkit.gate.hooks import git, hooks
from devkit.rules.engine.settings import describe_setting_type

HEADER = f"""\
## Clone-local settings of devkit commit gates: not tracked by Git, shared by every worktree of this clone.
## A key uncommented here replaces its value from {CONFIG_PATH} as a whole (an array too); a key left commented
## keeps that value. To change a setting, uncomment its table header and only the keys you change (lines starting
## with a single #); a key uncommented without its header belongs to the table above it.
## A key {CONFIG_PATH} set when its table was written is a ## line saying so. Lines starting with ## stay comments.
## `devkit gate install` and `devkit sync` append a commented table for each new gate; existing lines are never changed.
"""
_MENTION = re.compile(r"^\s*#?\s*\[\s*gates\s*\.\s*settings\s*\.\s*\"?([^\]\"\s]+)\"?\s*\]", re.MULTILINE)
# A value to show for a field whose default is ``None`` (TOML has no null), by the field's inner type.
_PLACEHOLDERS: dict[str, Any] = {"integer": 0, "number": 0.0, "string": "", "boolean": False}
_INSTALL_FIX = "then run `devkit gate install`"

_log = get_logger(__name__)


class TemplateState(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class TemplateResult:
    path: Path
    state: TemplateState
    notice: AdvisoryError | None = None  # set when ``state`` is ``SKIPPED``


def _toml(value: Any) -> str:
    return tomlkit.item(value).as_string()


def _project_line(name: str, note: str = "") -> str:
    """A key the project config sets, as prose: uncommenting the table around it keeps the project's value."""
    return f"##   {name}: set in {CONFIG_PATH}; adding {name} = <value> here replaces it" + (
        f"  # {note}" if note else ""
    )


def _project_keys(entry: GateEntry | None) -> set[str]:
    if entry is None:
        return set()
    return set(entry.values) | ({ENABLED_KEY} if entry.enabled is not None else set())


def _setting_line(item: dataclasses.Field[Any], kind: str, value: Any, project: set[str]) -> str:
    if value is None:
        inner = kind.removesuffix(" or null")
        shown, note = _toml(_PLACEHOLDERS.get(inner, [])), f"{kind}; unset by default"
    else:
        shown, note = _toml(value), kind
    help_text = item.metadata.get("help")
    if isinstance(help_text, str) and help_text.strip():
        note = f"{note}; {' '.join(help_text.split())}"
    return _project_line(item.name, note) if item.name in project else f"#   {item.name} = {shown}  # {note}"


def _setting_lines(gate: Gate, project: set[str]) -> list[str]:
    defaults = gate.settings
    if defaults is None or not dataclasses.is_dataclass(defaults) or isinstance(defaults, type):
        return []
    try:
        hints = typing.get_type_hints(type(defaults))
        fields = dataclasses.fields(defaults)
        kinds = {item.name: describe_setting_type(hints[item.name]) for item in fields}
    except Exception:  # an invalid declaration is reported by `devkit gate status`; show no settings for it
        return []
    lines = []
    for item in fields:
        try:
            lines.append(_setting_line(item, kinds[item.name], getattr(defaults, item.name), project))
        except Exception as exc:  # a default TOML cannot represent: leave the key out rather than the whole template
            _log.info("gate %s: setting %s not shown in the template: %s", gate.id, item.name, exc)
    return lines


def render_table(gate: Gate, project: GatesConfig | None = None) -> str:
    """The commented ``[gates.settings.<id>]`` table of one gate.

    Keys that ``project`` (the ``.devkit/config.toml`` layer) sets for the gate
    are prose lines rather than commented defaults.
    """
    keys = _project_keys(project.gates.get(gate.id) if project is not None else None)
    state = "on" if gate.enabled_by_default else "off"
    description = " ".join(str(gate.description).split())
    enabled = f"#   {ENABLED_KEY} = {_toml(gate.enabled_by_default)}"
    lines = [
        f"## {gate.stage.value} gate, {state} by default" + (f": {description}" if description else ""),
        f"# [gates.settings.{gate.id}]",
        _project_line(ENABLED_KEY) if ENABLED_KEY in keys else enabled,
        *_setting_lines(gate, keys),
    ]
    return "\n".join(lines) + "\n"


def mentioned_gates(text: str) -> set[str]:
    """Gate ids whose ``[gates.settings.<id>]`` header appears in ``text``, commented or not."""
    return set(_MENTION.findall(text))


def _skipped(path: Path, problem: str, fix: str | None = None, target: str | None = None) -> TemplateResult:
    notice = GateTemplateNotice(
        f"gate settings template not written to {path}: {problem}",
        target_files=[target or str(path)],
        fix=fix or f"Make {path} a regular UTF-8 file, or delete it, {_INSTALL_FIX}",
    )
    return TemplateResult(path, TemplateState.SKIPPED, notice)


def _write(path: Path, text: str, mode: int) -> None:
    """Replace ``path`` atomically with ``text``, never writing through a link at ``path``."""
    temporary = path.with_name(f".{path.name}.devkit-{os.getpid()}")
    try:
        temporary.write_bytes(text.encode("utf-8"))
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary.is_symlink() or temporary.exists():
            temporary.unlink()


def refresh_template(common_git_dir: Path, gates: list[Gate], project: GatesConfig | None = None) -> TemplateResult:
    """Create ``<common_git_dir>/devkit.config`` with every gate's table, or append the tables it lacks.

    ``project`` is the ``.devkit/config.toml`` layer (``load_project_gates_config``);
    the keys it sets are rendered as prose (``render_table``). Holds the clone-wide
    ``hooks.clone_lock`` from the read to the write. A file that cannot be read or
    written is ``SKIPPED`` with a ``GATE_CONFIG_TEMPLATE_SKIPPED`` notice.
    """
    path = common_git_dir / LOCAL_CONFIG
    try:
        with hooks.clone_lock(common_git_dir):
            return _refresh(path, gates, project)
    except OSError as exc:
        writable = f"Make {path.parent} writable and {path} a regular UTF-8 file, {_INSTALL_FIX}"
        return _skipped(path, f"cannot be written: {exc}", fix=writable)


def _refresh(path: Path, gates: list[Gate], project: GatesConfig | None) -> TemplateResult:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        return _skipped(path, "not a regular file")
    if not path.exists():
        _write(path, HEADER + "".join(f"\n{render_table(gate, project)}" for gate in gates), 0o644)
        return TemplateResult(path, TemplateState.CREATED)
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return _skipped(path, str(exc))
    mentioned = mentioned_gates(text)
    missing = [gate for gate in gates if gate.id not in mentioned]
    if not missing:
        return TemplateResult(path, TemplateState.UNCHANGED)
    if text and not text.endswith("\n"):
        text += "\n"
    _write(path, text + "".join(f"\n{render_table(gate, project)}" for gate in missing), path.stat().st_mode & 0o777)
    return TemplateResult(path, TemplateState.UPDATED)


def refresh_project_template(repo_root: Path) -> TemplateResult:
    """``refresh_template`` for the work tree at ``repo_root``, with the gates its registry loads.

    Gates that fail to load are left out; `devkit gate status` reports them. A
    ``.devkit/config.toml`` whose ``[gates]`` cannot be read skips the refresh:
    without it, a table would offer the project's keys at their defaults. Never
    raises once the common Git directory is found: any other failure is a
    ``SKIPPED`` result, so the caller still reports what it did before.
    """
    common = git.common_git_dir(repo_root)
    try:
        project = load_project_gates_config(repo_root)
    except ConfigError as exc:
        return _skipped(
            common / LOCAL_CONFIG,
            f"{CONFIG_PATH} cannot be read: {exc.message}",
            fix=f"Correct {CONFIG_PATH} (`devkit gate status` reports the problem), {_INSTALL_FIX}",
            target=CONFIG_PATH,
        )
    try:
        return refresh_template(common, project_registry(repo_root).get_all(), project)
    except Exception as exc:  # the template is secondary: never lose the install's own result over it
        error = as_advisory_error(exc)
        path = common / LOCAL_CONFIG
        return _skipped(
            path,
            f"refresh failed: {error.code}: {error.message}",
            fix=error.fix or f"Correct the cause, {_INSTALL_FIX}",
            target=next(iter(error.target_files), None),
        )


def post_sync(root: Path, result: dict[str, Any]) -> list[AdvisoryError] | None:
    """Install hook dispatchers and active devkit entries, then refresh the clone-local template."""
    del result
    try:
        top = require_git_toplevel(root)
    except GitError:
        return None
    notices: list[AdvisoryError] = []
    try:
        installed = hooks.install(top, sys.executable)
    except (AdvisoryError, OSError) as exc:
        if isinstance(exc, AdvisoryError):
            notice = HookInstallSkippedNotice(
                "automatic Git hook installation skipped",
                f"reason={exc.code}: {exc.message}",
                *exc.details,
                fix=exc.fix,
                target_files=exc.target_files,
            )
        else:
            notice = HookInstallSkippedNotice(
                "automatic Git hook installation skipped",
                str(exc),
                fix="Correct the hook directory permissions, then run `devkit sync`",
            )
        notices.append(notice)
    else:
        notices.extend(installed.notices)
    refreshed = refresh_project_template(top)
    if refreshed.notice is not None:
        notices.append(refreshed.notice)
    return notices or None
