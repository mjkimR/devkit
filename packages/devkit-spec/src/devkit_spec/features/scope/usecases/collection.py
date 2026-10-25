"""Explicit Host collection application operation; workflow evaluation never calls it."""

from pathlib import Path

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.features.scope.models.observation import CollectionOptions, CollectionReport
from devkit_spec.features.scope.services.collection import Collector


class CollectScopesUseCase(BaseUseCase):
    def execute(self, root: Path, options: CollectionOptions) -> CollectionReport:
        if options.mode not in {"snapshot", "refs", "worktrees"}:
            raise ArgumentError("Unknown scope collection mode", fix="Choose snapshot, refs or worktrees")
        if not 1 <= options.timeout <= 300 or not 1 <= options.source_timeout <= 300:
            raise ArgumentError("Collection budgets must be integers from 1 to 300", fix="Pass budgets in range 1..300")
        if options.mode == "snapshot" and options.fetch:
            raise ArgumentError("Snapshot mode cannot fetch", fix="Choose refs/worktrees or omit --fetch")
        return Collector(root, options).execute()
