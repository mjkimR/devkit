"""``[workflow]``, ``[workflow.approvals]`` and ``[workflow.stages]`` from ``.devkit/config.toml``."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

from devkit.core.project import config_table, read_project_config
from devkit.core.receipt import CONFIG_PATH
from devkit.workflow.definition.ids import IDENT_HINT, is_ident
from devkit.workflow.errors import LayoutError, WorkflowConfigError
from devkit.workflow.project.layout import LAYOUT_KEYS, TemplateLayout, validate_layout_key, validate_relative_dir

__all__ = ["WorkflowConfig", "load_workflow_config", "parse_workflow_config"]

WORKFLOW_TABLE = "workflow"
APPROVALS_KEY = "approvals"
STAGES_KEY = "stages"

DEFAULT_WORK_DIR = ".devkit/transient/work"
DEFAULT_UNIT_PATH = "{slug}"
DEFAULT_ANCHOR = "task.md"
DEFAULT_DEFINITIONS_DIR = ".devkit/workflows"
DEFAULT_ROLES_DIR = ".devkit/roles"
DEFAULT_CHECKS_DIR = ".devkit/workflow-checks"

POLICIES = ("ask", "auto", "off")
STAGE_POLICIES = ("on", "off")
DIRECTORY_KEYS = ("definitions_dir", "roles_dir", "checks_dir")
ALLOWED_KEYS = frozenset({*LAYOUT_KEYS, *DIRECTORY_KEYS, "default", APPROVALS_KEY, STAGES_KEY})
DEFAULTS = {
    "work_dir": DEFAULT_WORK_DIR,
    "unit_path": DEFAULT_UNIT_PATH,
    "anchor": DEFAULT_ANCHOR,
    "definitions_dir": DEFAULT_DEFINITIONS_DIR,
    "roles_dir": DEFAULT_ROLES_DIR,
    "checks_dir": DEFAULT_CHECKS_DIR,
}


@dataclass(frozen=True)
class WorkflowConfig:
    work_dir: str = DEFAULT_WORK_DIR
    unit_path: str = DEFAULT_UNIT_PATH
    anchor: str = DEFAULT_ANCHOR
    definitions_dir: str = DEFAULT_DEFINITIONS_DIR
    roles_dir: str = DEFAULT_ROLES_DIR  # project-authored subagent contracts, <role>.md
    checks_dir: str = DEFAULT_CHECKS_DIR  # project-authored plugin checks, *.py
    default: str | None = None
    approvals: dict[str, str] = field(default_factory=dict)
    stages: dict[str, str] = field(default_factory=dict)
    source: Path | None = None

    def policy(self, gate: str) -> str:
        return self.approvals.get(gate, "ask")

    def stage_policy(self, stage_id: str) -> str:
        return self.stages.get(stage_id, "on")

    @cached_property
    def layout(self) -> TemplateLayout:
        """The project default layout (built and validated once)."""
        return TemplateLayout(self.work_dir, self.unit_path, self.anchor)


def _path_value(section: dict[str, Any], key: str) -> str:
    """A layout key or directory key of ``[workflow]``, validated, else its default."""
    value = section.get(key, DEFAULTS[key])
    try:
        return validate_layout_key(key, value) if key in LAYOUT_KEYS else validate_relative_dir(value)
    except LayoutError as exc:
        raise WorkflowConfigError(f"config {WORKFLOW_TABLE}.{key}: {exc}") from exc


def _policy_table(section: dict[str, Any], key: str, allowed: Iterable[str], names: str) -> dict[str, str]:
    """``[workflow.<key>]``: identifiers mapped to one of ``allowed``; ``names`` says what the keys are."""
    raw = section.get(key)
    if raw is None:
        return {}
    choices = "|".join(allowed)
    if not isinstance(raw, dict):
        raise WorkflowConfigError(f"config {WORKFLOW_TABLE}.{key}: expected a table of {names} to {choices}")
    table: dict[str, str] = {}
    for name in sorted(raw):
        where = f"config {WORKFLOW_TABLE}.{key}.{name}"
        if not is_ident(name):
            raise WorkflowConfigError(f"{where}: {names} match {IDENT_HINT}")
        value = raw[name]
        if not isinstance(value, str) or value not in allowed:
            raise WorkflowConfigError(f"{where}: {value!r} is not one of {choices}")
        table[name] = value
    return table


def parse_workflow_config(data: object, source: Path | None = None) -> WorkflowConfig:
    """The ``[workflow]`` table of parsed configuration ``data``; raises ``WorkflowConfigError``."""
    if not isinstance(data, dict):
        raise WorkflowConfigError("config: expected a table")
    section = data.get(WORKFLOW_TABLE)
    if section is None:
        return WorkflowConfig(source=source)
    section = config_table(section, WORKFLOW_TABLE, WorkflowConfigError)
    unknown = set(section) - ALLOWED_KEYS
    if unknown:
        raise WorkflowConfigError(f"config {WORKFLOW_TABLE}: unknown fields: {sorted(unknown)}")
    default = section.get("default")
    if default is not None and (not isinstance(default, str) or not default.strip()):
        raise WorkflowConfigError(f"config {WORKFLOW_TABLE}.default: expected a workflow id")
    return WorkflowConfig(
        work_dir=_path_value(section, "work_dir"),
        unit_path=_path_value(section, "unit_path"),
        anchor=_path_value(section, "anchor"),
        definitions_dir=_path_value(section, "definitions_dir"),
        roles_dir=_path_value(section, "roles_dir"),
        checks_dir=_path_value(section, "checks_dir"),
        default=default,
        approvals=_policy_table(section, APPROVALS_KEY, POLICIES, "gate names"),
        stages=_policy_table(section, STAGES_KEY, STAGE_POLICIES, "stage ids"),
        source=source,
    )


def load_workflow_config(workspace_root: Path) -> WorkflowConfig:
    """The ``[workflow]`` table of ``.devkit/config.toml``; a missing file or table yields the defaults.

    An unreadable file raises the core ``ConfigError`` (``CONFIG_INVALID``)
    unchanged; a malformed table raises ``WorkflowConfigError`` (``WORKFLOW_CONFIG_INVALID``).
    """
    data = read_project_config(workspace_root)
    return parse_workflow_config(data, source=workspace_root / CONFIG_PATH if data else None)
