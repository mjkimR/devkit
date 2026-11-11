"""Return adaptive assignments."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.services.operations import return_assignment
from devkit_adaptive.features.assignment.usecases.context import repository


class ReturnAssignmentUseCase(BaseUseCase):
    def execute(self, root: Path, options: dict[str, Any]) -> Result:
        return return_assignment(repository(root), options)
