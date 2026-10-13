"""The commented settings template in the clone-local ``<common-git-dir>/devkit.config``.

``devkit gate install`` and, once the managed wrappers are installed, every
``devkit sync`` (through the ``devkit.post_sync`` hook ``post_sync``) make sure
the file names every installed gate: one commented ``[gates.settings.<id>]``
table per gate, with ``enabled`` and each settings field at its default, its
type and the field's ``metadata["help"]`` when the gate declares one.

Prose is commented twice (``##``) and settings once (``#``), so uncommenting a
whole table in an editor leaves the prose a comment and yields valid TOML; the
keys are indented under their header, which must be uncommented with them.

The file belongs to the developer. A missing file is created; an existing one
only gets tables appended for gates it does not mention yet (commented or
not), so uncommenting a line in place is the way to change a setting and no
line is ever rewritten. A file devkit cannot safely append to (a symbolic link,
not a regular file, not UTF-8) is left alone and reported as
``GateTemplateNotice`` (``GATE_CONFIG_TEMPLATE_SKIPPED``, a warning).
"""

from __future__ import annotations

import dataclasses
import os
import re
import typing
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomlkit

from devkit.advisory import AdvisoryError
from devkit.core import require_git_toplevel
from devkit.core.errors import GitError
from devkit.gate.engine.config import LOCAL_CONFIG
from devkit.gate.engine.models import Gate
from devkit.gate.engine.registry import project_registry
from devkit.gate.errors import GateTemplateNotice
from devkit.gate.hooks import git, hooks
from devkit.rules.engine.settings import describe_setting_type

HEADER = """\
## Clone-local settings of devkit commit gates: not tracked by Git, shared by every worktree of this clone.
## [gates] here overrides the same keys in .devkit/config.toml.
## To change a setting, uncomment its table header together with the keys below it (lines starting with a single #);
## a key uncommented without its header belongs to the table above it. Lines starting with ## stay comments.
## `devkit gate install` and `devkit sync` append a commented table for each new gate; existing lines are never changed.
"""
_MENTION = re.compile(r"^\s*#?\s*\[\s*gates\s*\.\s*settings\s*\.\s*\"?([^\]\"\s]+)\"?\s*\]", re.MULTILINE)
# A value to show for a field whose default is ``None`` (TOML has no null), by the field's inner type.
_PLACEHOLDERS: dict[str, Any] = {"integer": 0, "number": 0.0, "string": "", "boolean": False}


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


def _setting_lines(gate: Gate) -> list[str]:
    defaults = gate.settings
    if defaults is None or not dataclasses.is_dataclass(defaults) or isinstance(defaults, type):
        return []
    try:
        hints = typing.get_type_hints(type(defaults))
        kinds = {item.name: describe_setting_type(hints[item.name]) for item in dataclasses.fields(defaults)}
    except Exception:  # an invalid declaration is reported by `devkit gate status`; show no settings for it
        return []
    lines = []
    for item in dataclasses.fields(defaults):
        kind = kinds[item.name]
        value = getattr(defaults, item.name)
        if value is None:
            inner = kind.removesuffix(" or null")
            shown, note = _toml(_PLACEHOLDERS.get(inner, [])), f"{kind}; unset by default"
        else:
            shown, note = _toml(value), kind
        help_text = item.metadata.get("help")
        if isinstance(help_text, str) and help_text.strip():
            note = f"{note}; {' '.join(help_text.split())}"
        lines.append(f"#   {item.name} = {shown}  # {note}")
    return lines


def render_table(gate: Gate) -> str:
    """The commented ``[gates.settings.<id>]`` table of one gate."""
    state = "on" if gate.enabled_by_default else "off"
    description = " ".join(str(gate.description).split())
    lines = [
        f"## {gate.stage.value} gate, {state} by default" + (f": {description}" if description else ""),
        f"# [gates.settings.{gate.id}]",
        f"#   enabled = {_toml(gate.enabled_by_default)}",
        *_setting_lines(gate),
    ]
    return "\n".join(lines) + "\n"


def mentioned_gates(text: str) -> set[str]:
    """Gate ids whose ``[gates.settings.<id>]`` header appears in ``text``, commented or not."""
    return set(_MENTION.findall(text))


def _skipped(path: Path, problem: str) -> TemplateResult:
    notice = GateTemplateNotice(
        f"gate settings template not written to {path}: {problem}",
        target_files=[str(path)],
        fix=f"Make {path} a regular UTF-8 file, or delete it, then run `devkit gate install`",
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


def refresh_template(common_git_dir: Path, gates: list[Gate]) -> TemplateResult:
    """Create ``<common_git_dir>/devkit.config`` with every gate's table, or append the tables it lacks."""
    path = common_git_dir / LOCAL_CONFIG
    if path.is_symlink() or (path.exists() and not path.is_file()):
        return _skipped(path, "not a regular file")
    if not path.exists():
        _write(path, HEADER + "".join(f"\n{render_table(gate)}" for gate in gates), 0o644)
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
    _write(path, text + "".join(f"\n{render_table(gate)}" for gate in missing), path.stat().st_mode & 0o777)
    return TemplateResult(path, TemplateState.UPDATED)


def refresh_project_template(repo_root: Path) -> TemplateResult:
    """``refresh_template`` for the work tree at ``repo_root``, with the gates its registry loads.

    Gates that fail to load are left out; `devkit gate status` reports them.
    """
    return refresh_template(git.common_git_dir(repo_root), project_registry(repo_root).get_all())


def post_sync(root: Path, result: dict[str, Any]) -> list[AdvisoryError] | None:
    """``devkit.post_sync`` hook: refresh the template when this repository runs the managed wrappers.

    A sync never installs hooks, so a repository without them is left alone, as
    is a directory outside a Git work tree.
    """
    del result
    try:
        top = require_git_toplevel(root)
        if not any(item.state is hooks.HookState.MANAGED for item in hooks.status(top)):
            return None
        refreshed = refresh_project_template(top)
    except GitError:
        return None
    return [refreshed.notice] if refreshed.notice is not None else None
