"""Apply project policy and extension guards to worktree lifecycle operations."""

from __future__ import annotations

from pathlib import Path

from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.project.repositories.project import find_project_root

from devkit_agt.features.worktree.models.config import WorktreeConfig
from devkit_agt.features.worktree.models.lifecycle import FinishResult, Position, StartResult
from devkit_agt.features.worktree.repositories.config import read_worktree_config
from devkit_agt.features.worktree.services.extensions import run_attach_checks, run_post_finish
from devkit_agt.features.worktree.usecases.lifecycle import attach, discard, finish, locate, start


class LocateProject(BaseUseCase):
    """Resolve the checkout and its project's worktree policy."""

    def execute(self, start: Path) -> tuple[Position, WorktreeConfig]:
        """Resolve the checkout and its project's worktree policy."""
        return locate(start), read_worktree_config(find_project_root(start))


class StartActivity(BaseUseCase):
    """Create or attach the task checkout with the configured setup and attach guards."""

    def execute(
        self,
        position: Position,
        config: WorktreeConfig,
        branch: str,
        *,
        existing: str | None = None,
        unit: str | None = None,
    ) -> StartResult:
        """Create or attach the task checkout with the configured setup and attach guards."""
        if existing is not None and unit is not None:
            return attach(
                position,
                branch,
                source=existing,
                unit=unit,
                setup=config.setup,
                sync=True,
                check=run_attach_checks,
            )
        return start(position, branch, setup=config.setup, sync=True)


class FinishActivity(BaseUseCase):
    """Clean up a merged branch or discard one under the project's policy, then invoke post-finish extensions."""

    def execute(
        self,
        position: Position,
        config: WorktreeConfig,
        branch: str,
        *,
        discard_branch: bool = False,
    ) -> FinishResult:
        """Clean up a merged branch or discard one under the project's policy, then invoke post-finish extensions."""
        if discard_branch:
            result = discard(position, branch)
        else:
            result = finish(position, branch, delete_branch=config.delete_branch)
        result.notices.extend(run_post_finish(position.base, result.to_dict()))
        return result
