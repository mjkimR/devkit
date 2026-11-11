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
import re
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomlkit
from devkit.advisory import AdvisoryError, as_advisory_error
from devkit_core.base.errors import GitError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import UnsafePathError, atomic_write_text
from devkit_core.core.logs import get_logger
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.repositories.project import require_git_toplevel
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH
from devkit_dist.features.project.services.config_template import TemplateKey, TemplateTable, prose, render_key

import devkit_agt.features.gate.repositories.git as git
import devkit_agt.features.gate.usecases.hooks.hooks as hooks
from devkit_agt.features.gate.models.base import BaseGate
from devkit_agt.features.gate.models.errors import GateDefinitionError, GateTemplateNotice, HookInstallSkippedNotice
from devkit_agt.features.gate.repositories.config import (
    ENABLED_KEY,
    LOCAL_CONFIG,
    GateEntry,
    GatesConfig,
    declared_settings,
    load_project_gates_config,
)
from devkit_agt.features.gate.usecases.registry import default_gate_registry, project_registry

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
_INSTALL_FIX = f"then run `{devkit_command('gate install')}`"

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


def _setting_lines(gate: BaseGate, project: set[str]) -> list[str]:
    try:
        settings = declared_settings(gate) or ()
    except GateDefinitionError:  # an invalid declaration is reported by `devkit gate status`; show no settings for it
        return []
    lines = []
    for setting in settings:
        item = setting.item
        try:
            key = _template_key(item, setting.kind, getattr(gate.settings, item.name))
            # A key the project sets is prose naming it; its note is the one the commented default would carry.
            line = render_key(key, indent="  ", example=True)
            if item.name in project:
                shown = key.example if key.default is None else key.default
                line = _project_line(item.name, line.removeprefix(f"#   {item.name} = {_toml(shown)}  # "))
            lines.append(line)
        except Exception as exc:  # a default TOML cannot represent: leave the key out rather than the whole template
            _log.info("gate %s: setting %s not shown in the template: %s", gate.id, item.name, exc)
    return lines


def render_table(gate: BaseGate, project: GatesConfig | None = None) -> str:
    """The commented ``[gates.settings.<id>]`` table of one gate.

    Keys that ``project`` (the ``.devkit/config.toml`` layer) sets for the gate
    are prose lines rather than commented defaults.
    """
    keys = _project_keys(project.gates.get(gate.id) if project is not None else None)
    state = "on" if gate.enabled_by_default else "off"
    description = " ".join(str(gate.description).split())
    enabled = f"#   {ENABLED_KEY} = {_toml(gate.enabled_by_default)}"
    lines = [
        *prose(f"{gate.stage.value} gate, {state} by default" + (f": {description}" if description else "")),
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


def refresh_template(common_git_dir: Path, gates: list[BaseGate], project: GatesConfig | None = None) -> TemplateResult:
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
    except (OSError, UnsafePathError) as exc:  # UnsafePathError: the clone lock file is not a regular file
        writable = f"Make {path.parent} writable and {path} a regular UTF-8 file, {_INSTALL_FIX}"
        return _skipped(path, f"cannot be written: {exc}", fix=writable)


def _refresh(path: Path, gates: list[BaseGate], project: GatesConfig | None) -> TemplateResult:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        return _skipped(path, "not a regular file")
    if not path.exists():
        atomic_write_text(path, HEADER + "".join(f"\n{render_table(gate, project)}" for gate in gates), mode=0o644)
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
    atomic_write_text(
        path, text + "".join(f"\n{render_table(gate, project)}" for gate in missing), mode=path.stat().st_mode & 0o777
    )
    return TemplateResult(path, TemplateState.UPDATED)


class RefreshGateTemplateUseCase(BaseUseCase):
    """Application entrypoint for refresh project template."""

    def execute(self, repo_root: Path) -> TemplateResult:
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
                fix=f"Correct {CONFIG_PATH} (`{devkit_command('gate status')}` reports the problem), {_INSTALL_FIX}",
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


refresh_project_template = RefreshGateTemplateUseCase().execute


def _skipped_install(exc: AdvisoryError | OSError) -> HookInstallSkippedNotice:
    if isinstance(exc, AdvisoryError):
        return HookInstallSkippedNotice(
            "automatic Git hook installation skipped",
            f"reason={exc.code}: {exc.message}",
            *exc.details,
            fix=exc.fix,
            target_files=exc.target_files,
        )
    return HookInstallSkippedNotice(
        "automatic Git hook installation skipped",
        str(exc),
        fix=f"Correct the hook directory permissions, then run `{devkit_command('sync')}`",
    )


def post_sync(root: Path, result: dict[str, Any]) -> list[str | AdvisoryError] | None:
    """Install hook dispatchers and active devkit entries, then refresh the clone-local template.

    Reports one ``gate hooks: <change>; ...`` line when the hooks changed (the first sync, a moved hook, a repaired
    entry), nothing when they are already in place.
    """
    del result
    try:
        top = require_git_toplevel(root)
    except GitError:
        return None
    notices: list[str | AdvisoryError] = []
    try:
        installed = hooks.install(top, sys.executable, preserve_python=True)
    except (AdvisoryError, OSError) as exc:
        notices.append(_skipped_install(exc))
    else:
        if installed.actions:
            notices.append(f"gate hooks: {'; '.join(installed.actions)}")
        notices.extend(installed.notices)
    refreshed = refresh_project_template(top)
    if refreshed.notice is not None:
        notices.append(refreshed.notice)
    return notices or None


def post_sync_preview(root: Path, result: dict[str, Any]) -> list[str | AdvisoryError] | None:
    """What ``post_sync`` would change in the Git hooks, for ``devkit sync --dry-run``; writes nothing.

    One ``gate hooks would change: <change>; ...`` line, or the ``GATE_HOOK_INSTALL_SKIPPED`` warning the sync would
    report; ``None`` when the hooks are already in place or ``root`` is not in a Git work tree.
    """
    del result
    try:
        top = require_git_toplevel(root)
    except GitError:
        return None
    try:
        planned = hooks.install(top, sys.executable, preserve_python=True, dry_run=True)
    except (AdvisoryError, OSError) as exc:
        return [_skipped_install(exc)]
    return [f"gate hooks would change: {'; '.join(planned.actions)}"] if planned.actions else None


def _template_key(item: dataclasses.Field[Any], kind: str, value: Any) -> TemplateKey:
    help_text = item.metadata.get("help")
    note = " ".join(help_text.split()) if isinstance(help_text, str) else ""
    if value is None:
        inner = kind.removesuffix(" or null")
        return TemplateKey(
            item.name, None, "unset by default" + (f"; {note}" if note else ""), kind, _PLACEHOLDERS.get(inner, [])
        )
    return TemplateKey(item.name, value, note, kind)


def config_tables() -> tuple[TemplateTable, ...]:
    """The commented ``[gates.settings.<id>]`` tables of the built-in gates for ``devkit config template``.

    For the ``devkit.config_tables`` entry point ``gates``: every project gets the same template, so it lists the
    built-in gates only, at their defaults; bundle gates appear in the clone-local ``devkit.config``.
    """
    tables = []
    for gate in default_gate_registry().get_all():
        state = "on" if gate.enabled_by_default else "off"
        keys = [TemplateKey(ENABLED_KEY, gate.enabled_by_default, "false turns the gate off")]
        for setting in declared_settings(gate) or ():
            keys.append(_template_key(setting.item, setting.kind, getattr(gate.settings, setting.item.name)))
        description = " ".join(str(gate.description).split())
        tables.append(
            TemplateTable(
                tuple(keys),
                ("settings", gate.id),
                help=f"{gate.stage.value} gate, {state} by default: {description}",
            )
        )
    return tuple(tables)
