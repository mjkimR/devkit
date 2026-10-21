"""Reconcile and inspect the owning workspace's retained runtime registration."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.distribution.services.installation.config import read_config
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.host.usecases import registrations


class SetupMcpUseCase(BaseUseCase):
    def execute(
        self, root: Path, hosts: tuple[str, ...], *, executable: str | None = None
    ) -> registrations.RegistrationPlan:
        with registrations.clone_lock(root), project_lock(root):
            registrations.recover(root)
            planned = registrations.plan(root, hosts or read_config(root).agents, executable=executable)
            registrations.apply(planned)
        return planned


class RemoveMcpUseCase(BaseUseCase):
    def execute(self, root: Path) -> registrations.RegistrationPlan:
        with registrations.clone_lock(root), project_lock(root):
            registrations.recover(root)
            planned = registrations.plan(root, (), remove=True)
            registrations.apply(planned)
        return planned


class InspectMcpUseCase(BaseUseCase):
    def execute(self, root: Path) -> dict[str, Any]:
        return registrations.inspect(root, read_config(root).agents)
