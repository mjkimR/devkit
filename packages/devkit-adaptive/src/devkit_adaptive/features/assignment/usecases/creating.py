"""New adaptive assignments."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.services.operations import new_assignment
from devkit_adaptive.features.assignment.usecases.context import repository


class NewAssignmentUseCase(BaseUseCase):
    def execute(self, root: Path, options: dict[str, Any]) -> Result:
        return new_assignment(repository(root), options)
