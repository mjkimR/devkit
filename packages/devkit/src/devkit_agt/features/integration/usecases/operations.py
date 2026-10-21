"""Execution boundaries sharing the integration engine's retained authority and locks."""

from __future__ import annotations

from devkit_core.base.mcp import Confirmation
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
    """Execute through the integration engine's existing approval contract."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    async def execute(self, branch: str, task: Task, confirm: Confirmation, route: str = "local") -> IntegrationResult:
        return await self.service.integrate(branch, task, confirm, route)


class ResumeIntegrationUseCase(BaseUseCase):
    """Resume only authority retained by the same integration engine."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def execute(self, request_id: str) -> IntegrationResult:
        return self.service.resume(request_id)


class InspectIntegrationUseCase(BaseUseCase):
    """Inspect progress without supplying approval authority."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def execute(self, request_id: str) -> IntegrationResult:
        return self.service.inspect(request_id)
