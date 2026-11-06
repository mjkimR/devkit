"""Typed application operations for the isolated execution CLI."""

from __future__ import annotations

import math
from pathlib import Path

from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.isolated_execution.models.record import RunRecord
from devkit_agt.features.isolated_execution.repositories.runs import Runs, error
from devkit_agt.features.isolated_execution.services import lifecycle
from devkit_agt.features.worktree.repositories.execution import configured_setup


class StartExecution(BaseUseCase):
    def execute(self, root: Path, sha: str, argv: tuple[str, ...], setup: str | None = None) -> RunRecord:
        """Capture the command and return after detached launch."""
        if setup is None:
            setup = configured_setup(root)
        return Runs(root).launch(sha, argv, setup)


class ListExecutions(BaseUseCase):
    def execute(self, root: Path) -> list[RunRecord]:
        """Discover retained runs from a fresh caller process."""
        runs = Runs(root)
        return [
            runs.read(p.name)
            for p in sorted(runs.directory.glob("*/manifest.json"), key=lambda p: p.parent.name)
            for p in [p.parent]
        ]


class InspectExecution(BaseUseCase):
    def execute(self, root: Path, run_id: str) -> RunRecord:
        """Read persisted evidence and current process ownership."""
        return Runs(root).read(run_id)


class ExecutionLogs(BaseUseCase):
    def execute(self, root: Path, run_id: str, tail: int = 100) -> RunRecord:
        """Retrieve at most 1000 lines and 64 KiB, retaining full output on disk."""
        if not 0 <= tail <= 1000:
            raise error("EXECUTION_TAIL_INVALID", "tail must be between 0 and 1000")
        record = Runs(root).read(run_id)
        path = Path(record["log"])
        try:
            with path.open("rb") as stream:
                stream.seek(0, 2)
                stream.seek(max(0, stream.tell() - 65536))
                lines = stream.read().decode(errors="replace").splitlines()
        except FileNotFoundError:
            lines = []
        record["lines"] = lines[-tail:] if tail else []
        return record


class WaitExecution(BaseUseCase):
    def execute(self, root: Path, run_id: str, *, timeout: float | None = None, clean: bool = False) -> RunRecord:
        """Wait without agent-side polling or implicit cancellation."""
        if timeout is not None and (timeout < 0 or not math.isfinite(timeout)):
            raise error("EXECUTION_TIMEOUT_INVALID", "timeout must be a finite nonnegative number")
        return lifecycle.wait(Runs(root), run_id, timeout, clean)


class CancelExecution(BaseUseCase):
    def execute(self, root: Path, run_id: str) -> RunRecord:
        """Request managed process termination, retaining its environment."""
        return lifecycle.cancel(Runs(root), run_id)


class CleanExecution(BaseUseCase):
    def execute(self, root: Path, run_id: str) -> RunRecord:
        """Explicitly remove only a verified inactive clean run-owned checkout."""
        runs = Runs(root)
        runs.read(run_id)
        return lifecycle.clean(runs, run_id)
