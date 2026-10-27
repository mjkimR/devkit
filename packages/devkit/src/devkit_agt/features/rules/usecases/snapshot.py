"""Validate and capture an exact rules snapshot request."""

from pathlib import Path

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.rules.models.contracts import Phase
from devkit_agt.features.rules.models.snapshot import Snapshot
from devkit_agt.features.rules.repositories.workspace.snapshot import git_snapshot


class CaptureRulesSnapshotUseCase(BaseUseCase):
    """Application entrypoint for snapshot request."""

    def execute(
        self, root: Path, *, phase: str, targets: tuple[str, ...], staged: bool, ci: bool, base: str
    ) -> Snapshot:
        if staged and ci:
            raise ArgumentError("--staged and --ci are mutually exclusive", target_files=["--staged", "--ci"])
        mode = "--staged" if staged else "--ci"
        if targets:
            raise ArgumentError(
                f"{mode} checks the files of the Git snapshot; it takes no file arguments",
                target_files=list(targets),
                fix=f"Drop the file arguments: {' '.join(targets)}",
            )
        if phase.lower() != Phase.LINTER.value:
            raise ArgumentError(
                f"{mode} runs the linter phase only, not {phase}",
                target_files=["--phase"],
                fix=f"Drop --phase {phase}",
            )
        return git_snapshot(root, staged=staged, base=base)
