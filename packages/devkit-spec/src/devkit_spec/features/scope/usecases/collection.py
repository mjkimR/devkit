"""Explicit Host collection application operation; workflow evaluation never calls it."""

from pathlib import Path

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.features.scope.models.observation import CollectionOptions, CollectionReport
from devkit_spec.features.scope.services.collection import Collector


class CollectScopesUseCase(BaseUseCase):
    def execute(self, root: Path, options: CollectionOptions) -> CollectionReport:
        if options.mode not in {"snapshot", "refs", "worktrees"}:
            raise ArgumentError(
                "Unknown scope collection mode", target_files=["--mode"], fix="Choose snapshot, refs or worktrees"
            )
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
        if options.mode == "snapshot" and options.fetch:
            raise ArgumentError(
                "Snapshot mode cannot fetch",
                target_files=["--mode", "--fetch"],
                fix="Choose refs/worktrees or omit --fetch",
            )
        return Collector(root, options).execute()
