"""Inspect the effective gate setup and its installed hook entries."""

from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.project.repositories.project import git_toplevel

from devkit_agt.features.gate.usecases.hooks.hooks import (
    HooksLocation,
    HookStatus,
    locate,
    missing_entry_notices,
    status,
)
from devkit_agt.features.gate.usecases.runner import GateProject, LoadGateProjectUseCase


@dataclass(frozen=True)
class GateStatus:
    """Effective project and hook inspection, independent of its transport rendering."""

    project: GateProject
    location: HooksLocation
    hooks: tuple[HookStatus, ...]
    notices: tuple[AdvisoryError, ...]


class GateStatusUseCase(BaseUseCase):
    """Read project configuration, installed hooks and actionable setup notices together."""

    def execute(self, root: Path) -> GateStatus:
        project = LoadGateProjectUseCase().execute(root)
        location = locate(project.root)
        hooks = status(project.root, location)
        notices = missing_entry_notices(project, hooks, location)
        return GateStatus(project, location, tuple(hooks), tuple(notices))


def status_check(root: Path) -> tuple[AdvisoryError, ...]:
    """Contribute existing hook diagnostics to general status without executing gates or repairing hooks."""
    top = git_toplevel(root)
    if top is None:
        return ()
    return GateStatusUseCase().execute(top).notices
