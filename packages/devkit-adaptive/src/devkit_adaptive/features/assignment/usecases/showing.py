"""Show adaptive assignments."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.services.operations import show_assignment
from devkit_adaptive.features.assignment.usecases.context import repository


class ShowAssignmentUseCase(BaseUseCase):
    def execute(self, root: Path, options: dict[str, Any]) -> Result:
        return show_assignment(repository(root), options)
