"""``[workflow]`` and ``[workflow.approvals]`` from ``.devkit/config.toml``."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

CONFIG_PATH = ".devkit/config.toml"
WORKFLOW_TABLE = "workflow"
APPROVALS_KEY = "approvals"

DEFAULT_WORK_DIR = ".devkit/transient/work"
DEFAULT_UNIT_PATH = "{slug}"
DEFAULT_ANCHOR = "task.md"
DEFAULT_DEFINITIONS_DIR = ".devkit/workflows"

POLICIES = ("ask", "auto", "off")
GATE_NAME = re.compile(r"^[a-z][a-z0-9-]*$")


class ConfigError(ValueError):
    """Raised when the ``[workflow]`` configuration is malformed."""


@dataclass(frozen=True)
class WorkflowConfig:
    work_dir: str = DEFAULT_WORK_DIR
    unit_path: str = DEFAULT_UNIT_PATH
    anchor: str = DEFAULT_ANCHOR
    definitions_dir: str = DEFAULT_DEFINITIONS_DIR
    default: str | None = None
    approvals: dict[str, str] = field(default_factory=dict)
    source: Path | None = None

    def policy(self, gate: str) -> str:
        return self.approvals.get(gate, "ask")


def _relative_dir(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"config {WORKFLOW_TABLE}.{key}: expected a nonempty string")
    rel = PurePosixPath(value)
    if rel.is_absolute() or "\\" in value or ".." in rel.parts:
        raise ConfigError(f"config {WORKFLOW_TABLE}.{key}: must be a workspace-relative path without '..'")
    return rel.as_posix()


def _file_name(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip() or "/" in value or "\\" in value or value in {".", ".."}:
        raise ConfigError(f"config {WORKFLOW_TABLE}.{key}: expected a bare file name")
    return value


def parse_workflow_config(data: object, source: Path | None = None) -> WorkflowConfig:
    if not isinstance(data, dict):
        raise ConfigError("config: expected a table")
    section = data.get(WORKFLOW_TABLE)
    if section is None:
        return WorkflowConfig(source=source)
    if not isinstance(section, dict):
        raise ConfigError(f"config {WORKFLOW_TABLE}: expected a table")
    allowed = {"work_dir", "unit_path", "anchor", "definitions_dir", "default", APPROVALS_KEY}
    unknown = set(section) - allowed
    if unknown:
        raise ConfigError(f"config {WORKFLOW_TABLE}: unknown fields: {sorted(unknown)}")

    from agent_workflow_engine.layout import validate_template  # local import: layout imports nothing from here

    work_dir = _relative_dir(section.get("work_dir", DEFAULT_WORK_DIR), "work_dir")
    unit_path = section.get("unit_path", DEFAULT_UNIT_PATH)
    if not isinstance(unit_path, str):
        raise ConfigError(f"config {WORKFLOW_TABLE}.unit_path: expected a string")
    try:
        validate_template(unit_path)
    except ValueError as exc:
        raise ConfigError(f"config {WORKFLOW_TABLE}.unit_path: {exc}") from exc
    anchor = _file_name(section.get("anchor", DEFAULT_ANCHOR), "anchor")
    definitions_dir = _relative_dir(section.get("definitions_dir", DEFAULT_DEFINITIONS_DIR), "definitions_dir")

    default = section.get("default")
    if default is not None and (not isinstance(default, str) or not default.strip()):
        raise ConfigError(f"config {WORKFLOW_TABLE}.default: expected a workflow id")

    approvals: dict[str, str] = {}
    raw = section.get(APPROVALS_KEY)
    if raw is not None:
        if not isinstance(raw, dict):
            raise ConfigError(f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}: expected a table of gate to policy")
        for gate in sorted(raw):
            if not GATE_NAME.match(gate):
                raise ConfigError(f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}.{gate}: gate names match [a-z][a-z0-9-]*")
            value = raw[gate]
            if not isinstance(value, str) or value not in POLICIES:
                raise ConfigError(
                    f"config {WORKFLOW_TABLE}.{APPROVALS_KEY}.{gate}: {value!r} is not one of {'|'.join(POLICIES)}"
                )
            approvals[gate] = value

    return WorkflowConfig(
        work_dir=work_dir,
        unit_path=unit_path,
        anchor=anchor,
        definitions_dir=definitions_dir,
        default=default,
        approvals=approvals,
        source=source,
    )


def load_workflow_config(workspace_root: Path) -> WorkflowConfig:
    path = workspace_root / CONFIG_PATH
    if not path.is_file():
        return WorkflowConfig()
    try:
        data = tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid config {CONFIG_PATH}: {exc}") from exc
    return parse_workflow_config(data, source=path)
