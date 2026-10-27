"""Execution boundaries sharing the integration engine's retained authority and locks."""

from __future__ import annotations

from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.integration.models.contracts import IntegrationResult, Task
from devkit_agt.features.integration.usecases.service import IntegrationService


class PrepareIntegrationUseCase(BaseUseCase):
    """Prepare an integration request without execution authority."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def execute(self, branch: str, task: Task, route: str = "local") -> IntegrationResult:
        return self.service.prepare(branch, task, route)


class IntegrateUseCase(BaseUseCase):
    """Execute one Host-authorized invocation after rebuilding and checking its full scope."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def execute(
        self, branch: str, task: Task, route: str = "local", *, expected_digest: str | None = None
    ) -> IntegrationResult:
        return self.service.execute_cli(branch, task, route, expected_digest=expected_digest)
