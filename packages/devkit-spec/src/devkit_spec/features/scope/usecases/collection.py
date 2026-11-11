"""Explicit Host collection application operation; workflow evaluation never calls it."""

from pathlib import Path

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.features.scope.models.observation import CollectionOptions, CollectionReport
from devkit_spec.features.scope.services.collection import Collector


class CollectScopesUseCase(BaseUseCase):
    def execute(self, root: Path, options: CollectionOptions) -> CollectionReport:
        budgets = [
            flag
            for flag, value in (("--timeout", options.timeout), ("--source-timeout", options.source_timeout))
            if not 1 <= value <= 300
        ]
        if budgets:
            raise ArgumentError(
                "Collection budgets must be integers from 1 to 300",
                target_files=budgets,
                fix="Pass budgets in range 1..300",
            )
        return Collector(root, options).execute()
