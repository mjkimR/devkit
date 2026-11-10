"""Verify adaptive assignments."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.services.operations import mutate
from devkit_adaptive.features.assignment.usecases.context import repository


class VerifyAssignmentUseCase(BaseUseCase):
    def execute(self, root: Path, options: dict[str, Any]) -> Result:
        return mutate(repository(root), "verify", options)
