"""``[workflow]``, ``[workflow.approvals]`` and ``[workflow.stages]`` from ``.devkit/config.toml``."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from devkit.core import errors as core_errors
from devkit.core.project import read_project_config
from devkit.core.receipt import CONFIG_PATH
from devkit.workflow.errors import LayoutError, WorkflowError
from devkit.workflow.ids import IDENT, IDENT_HINT
from devkit.workflow.layout import TemplateLayout, validate_file_name, validate_relative_dir, validate_template

__all__ = ["CONFIG_PATH", "ConfigError", "WorkflowConfig", "load_workflow_config", "parse_workflow_config"]
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


class ConfigError(core_errors.ConfigError, WorkflowError):
    """``.devkit/config.toml`` cannot be read or its ``[workflow]`` tables are malformed (``CONFIG_INVALID``)."""

    fix = "Correct .devkit/config.toml: its TOML syntax and the [workflow], [workflow.approvals] and [workflow.stages] tables"


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

    @property
    def layout(self) -> TemplateLayout:
        """The project default layout."""
        return TemplateLayout(self.work_dir, self.unit_path, self.anchor)


def _relative_dir(value: object, key: str) -> str:
    try:
        return validate_relative_dir(value)
    except LayoutError as exc:
        raise ConfigError(f"config {WORKFLOW_TABLE}.{key}: {exc}") from exc


def _file_name(value: object, key: str) -> str:
    try:
        return validate_file_name(value)
    except LayoutError as exc:
        raise ConfigError(f"config {WORKFLOW_TABLE}.{key}: {exc}") from exc


def parse_workflow_config(data: object, source: Path | None = None) -> WorkflowConfig:
    if not isinstance(data, dict):
        raise ConfigError("config: expected a table")
    section = data.get(WORKFLOW_TABLE)
    if section is None:
        return WorkflowConfig(source=source)
    if not isinstance(section, dict):
        raise ConfigError(f"config {WORKFLOW_TABLE}: expected a table")
    allowed = {
        "work_dir",
        "unit_path",
        "anchor",
        "definitions_dir",
        "roles_dir",
        "checks_dir",
        "default",
        APPROVALS_KEY,
        STAGES_KEY,
    }
    unknown = set(section) - allowed
    if unknown:
        raise ConfigError(f"config {WORKFLOW_TABLE}: unknown fields: {sorted(unknown)}")

    work_dir = _relative_dir(section.get("work_dir", DEFAULT_WORK_DIR), "work_dir")
    unit_path = section.get("unit_path", DEFAULT_UNIT_PATH)
    if not isinstance(unit_path, str):
        raise ConfigError(f"config {WORKFLOW_TABLE}.unit_path: expected a string")
    try:
        validate_template(unit_path)
    except LayoutError as exc:
        raise ConfigError(f"config {WORKFLOW_TABLE}.unit_path: {exc}") from exc
    anchor = _file_name(section.get("anchor", DEFAULT_ANCHOR), "anchor")
    definitions_dir = _relative_dir(section.get("definitions_dir", DEFAULT_DEFINITIONS_DIR), "definitions_dir")
    roles_dir = _relative_dir(section.get("roles_dir", DEFAULT_ROLES_DIR), "roles_dir")
    checks_dir = _relative_dir(section.get("checks_dir", DEFAULT_CHECKS_DIR), "checks_dir")

    default = section.get("default")
    if default is not None and (not isinstance(default, str) or not default.strip()):
        raise ConfigError(f"config {WORKFLOW_TABLE}.default: expected a workflow id")

    approvals: dict[str, str] = {}
    raw = section.get(APPROVALS_KEY)
    if raw is not None:
        if not isinstance(raw, dict):
            raise ConfigError(f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}: expected a table of gate to policy")
        for gate in sorted(raw):
            if not IDENT.match(gate):
                raise ConfigError(f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}.{gate}: gate names match {IDENT_HINT}")
            value = raw[gate]
            if not isinstance(value, str) or value not in POLICIES:
                raise ConfigError(
                    f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}.{gate}: {value!r} is not one of {'|'.join(POLICIES)}"
                )
            approvals[gate] = value

    stages: dict[str, str] = {}
    raw_stages = section.get(STAGES_KEY)
    if raw_stages is not None:
        if not isinstance(raw_stages, dict):
            raise ConfigError(f"config {WORKFLOW_TABLE}.{STAGES_KEY}: expected a table of stage id to on|off")
        for stage_id in sorted(raw_stages):
            if not IDENT.match(stage_id):
                raise ConfigError(f"config {WORKFLOW_TABLE}.{STAGES_KEY}.{stage_id}: stage ids match {IDENT_HINT}")
            value = raw_stages[stage_id]
            if not isinstance(value, str) or value not in STAGE_POLICIES:
                raise ConfigError(
                    f"config {WORKFLOW_TABLE}.{STAGES_KEY}.{stage_id}: {value!r} is not one of {'|'.join(STAGE_POLICIES)}"
                )
            stages[stage_id] = value

    return WorkflowConfig(
        work_dir=work_dir,
        unit_path=unit_path,
        anchor=anchor,
        definitions_dir=definitions_dir,
        roles_dir=roles_dir,
        checks_dir=checks_dir,
        default=default,
        approvals=approvals,
        stages=stages,
        source=source,
    )


def load_workflow_config(workspace_root: Path) -> WorkflowConfig:
    """The ``[workflow]`` table of ``.devkit/config.toml``; a missing file or table yields the defaults."""
    try:
        data = read_project_config(workspace_root)
    except core_errors.ConfigError as exc:
        raise ConfigError(str(exc)) from exc
    path = workspace_root / CONFIG_PATH
    return parse_workflow_config(data, source=path if data else None)
