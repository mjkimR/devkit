"""Process-local MCP execution binding; no transport dependency or serialized approval authority."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path

from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_core.core.git import run_git

from devkit_dist.features.project.repositories.local_config import resolve_execution_environment


class McpWorkspaceError(AdvisoryError):
    code = "MCP_WORKSPACE_UNAVAILABLE"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    guardrail = True
    fix = "Reconnect from an existing retained checkout; inspect partial effects before a new approval"


class McpInteractiveError(McpWorkspaceError):
    code = "MCP_INTERACTIVE_UNAVAILABLE"
    guardrail = True  # a refusal in its own right, not by inheritance from McpWorkspaceError
    fix = "Use a local interactive Host or an independently authorized explicit CLI/PR route"


def common_directory(root: Path) -> Path:
    try:
        return Path(run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
    except AdvisoryError as exc:
        raise McpWorkspaceError("the owning workspace Git identity is unavailable") from exc


@dataclass
class ExecutionBinding:
    workspace: Path
    executor: Path
    common: Path = field(init=False)
    identity: tuple[int, int] = field(init=False)
    terminal_removal: Path | None = None

    def __post_init__(self) -> None:
        self.workspace = self.workspace.resolve()
        self.executor = self.executor.resolve()
        self.common = common_directory(self.workspace)
        if common_directory(self.executor) != self.common:
            raise McpWorkspaceError("executor and configuration workspace belong to different clones")
        stat = self.workspace.stat()
        self.identity = (stat.st_dev, stat.st_ino)
        self.environment()

    def environment(self, *, terminal: bool = False) -> str:
        if terminal and self.terminal_removal == self.workspace and not self.workspace.exists():
            return "local"
        try:
            stat = self.workspace.stat()
            if (stat.st_dev, stat.st_ino) != self.identity or common_directory(self.workspace) != self.common:
                raise McpWorkspaceError("the owning configuration workspace identity changed")
            return resolve_execution_environment(self.workspace).environment
        except (OSError, AdvisoryError) as exc:
            if isinstance(exc, McpWorkspaceError):
                raise
            raise McpWorkspaceError("the owning configuration workspace or its configuration is unavailable") from exc

    def guard(self, *, terminal: bool = False) -> None:
        if self.environment(terminal=terminal) != "local":
            raise McpInteractiveError("cloud execution cannot request or use native interactive approval")


_BINDING: ContextVar[ExecutionBinding | None] = ContextVar("devkit_mcp_binding", default=None)


@contextmanager
def bind(binding: ExecutionBinding):
    """Store the validated invocation for the current process-local operation."""
    token = _BINDING.set(binding)
    try:
        yield binding
    finally:
        _BINDING.reset(token)


def guard_execution(*, terminal: bool = False) -> None:
    """Domain boundary guard. Explicit CLI execution outside MCP retains its existing authorization contract."""
    binding = _BINDING.get()
    if binding is not None:
        binding.guard(terminal=terminal)
    raw = os.environ.get(CONSTRAINT_ENV)
    if raw is not None:
        _guard_constraint(raw)


def capture_terminal_removal(path: Path) -> None:
    """Called immediately before the exact approved removal, never before merge/push or on resume."""
    binding = _BINDING.get()
    if binding is not None and path.resolve() == binding.workspace:
        binding.guard()
        binding.terminal_removal = binding.workspace


CONSTRAINT_ENV = "DEVKIT_MCP_EXECUTION_CONSTRAINT"


def _guard_constraint(raw: str) -> None:
    """A child restriction can only refuse execution; it grants no invocation or approval authority."""
    try:
        value = json.loads(raw)
        if set(value) != {"workspace", "common", "identity"}:
            raise ValueError("invalid restriction fields")
        workspace = Path(value["workspace"])
        if not workspace.is_absolute():
            raise ValueError("relative workspace")
        current = workspace.stat()
        if [current.st_dev, current.st_ino] != value["identity"] or str(common_directory(workspace)) != value["common"]:
            raise McpWorkspaceError("the owning workspace identity changed in a child operation")
        if resolve_execution_environment(workspace).environment != "local":
            raise McpInteractiveError("cloud execution stops the remaining child operation")
    except (ValueError, TypeError, KeyError, OSError, AdvisoryError) as exc:
        if isinstance(exc, McpWorkspaceError):
            raise
        raise McpWorkspaceError("the child owning-workspace restriction is unavailable or malformed") from exc


def constraint_environment() -> dict[str, str]:
    """Export only a refusal constraint for trusted child operations, never native approval or cleanup state."""
    binding = _BINDING.get()
    if binding is None:
        return {}
    guard_execution()
    return {
        CONSTRAINT_ENV: json.dumps(
            {
                "workspace": str(binding.workspace),
                "common": str(binding.common),
                "identity": list(binding.identity),
            }
        )
    }


def configuration_workspace(fallback: Path) -> Path:
    """Service configuration belongs to the bound workspace, independently of executor preferences."""
    binding = _BINDING.get()
    if binding is not None:
        binding.environment()
        return binding.workspace
    return fallback
