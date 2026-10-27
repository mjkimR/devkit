"""Reconcile and inspect the owning workspace's retained runtime registration."""

from pathlib import Path
from typing import Any

from devkit.advisory import Level
from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.distribution.services.installation.config import read_config
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.host.usecases import registrations


class SetupMcpUseCase(BaseUseCase):
    """Register the retained runtime for ``hosts`` (default: the configured agents) and remove the owned entries of
    every other host: ``hosts`` limits registration. Refuses outside a Git checkout before any lock, and with
    ``MCP_RUNTIME_UNAVAILABLE`` before any write when no verified runtime can be registered."""

    def execute(
        self, root: Path, hosts: tuple[str, ...], *, executable: str | None = None
    ) -> registrations.RegistrationPlan:
        registrations.require_checkout(root)
        with registrations.clone_lock(root), project_lock(root):
            registrations.recover(root)
            planned = registrations.plan(root, hosts or read_config(root).agents, executable=executable)
            for notice in planned.notices:
                if isinstance(notice, registrations.RuntimeUnavailable):
                    raise notice.with_level(Level.ERROR)
            registrations.apply(planned)
        return planned


class RemoveMcpUseCase(BaseUseCase):
    """Remove every owned project entry; refuses outside a Git checkout before any lock."""

    def execute(self, root: Path) -> registrations.RegistrationPlan:
        registrations.require_checkout(root)
        with registrations.clone_lock(root), project_lock(root):
            registrations.recover(root)
            planned = registrations.plan(root, (), remove=True)
            registrations.apply(planned)
        return planned


class InspectMcpUseCase(BaseUseCase):
    def execute(self, root: Path) -> dict[str, Any]:
        return registrations.inspect(root, read_config(root).agents)
