"""Invocation queries and guards exposed to transport adapters."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit_dist.features.project.models.invocation import InvocationBinding
from devkit_dist.features.project.repositories import invocation as context


def configuration_workspace(fallback: Path) -> Path:
    return context.configuration_workspace(fallback)


def guard_execution(*, terminal: bool = False) -> None:
    context.guard_execution(terminal=terminal)


@contextmanager
def invocation(binding: InvocationBinding) -> Iterator[InvocationBinding]:
    """Revalidate the retained executor and bind a fresh context for one invocation."""
    fresh = context.ExecutionBinding(binding.workspace, binding.executor)
    if fresh.common != binding.common or fresh.identity != binding.identity:
        raise context.McpWorkspaceError("the original workspace was replaced; reconnect before approving")
    with context.bind(fresh):
        yield fresh


def execution_binding(workspace: Path, executor: Path) -> InvocationBinding:
    """Capture and validate the live owning-workspace identity for a runtime."""
    return context.ExecutionBinding(workspace, executor)
