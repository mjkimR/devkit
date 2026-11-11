"""List adaptive assignments."""

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.services.operations import list_assignments
from devkit_adaptive.features.assignment.usecases.context import repository


class ListAssignmentsUseCase(BaseUseCase):
    def execute(self, root: Path, options: dict[str, Any]) -> Result:
        return list_assignments(repository(root), options)
