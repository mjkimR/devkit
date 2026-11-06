"""Typed application operations for the isolated execution CLI."""

from __future__ import annotations

import math
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.isolated_execution.models.record import RunRecord, public_record
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
    def execute(self, root: Path, *, limit: int = 20, offset: int = 0) -> RunRecord:
        """Discover a bounded page; one corrupt run does not hide other evidence."""
        if not 1 <= limit <= 100 or offset < 0:
            raise error("EXECUTION_LIST_ARGUMENT_INVALID", "list limit must be 1-100 and offset nonnegative")
        runs = Runs(root)
        paths = sorted(runs.directory.glob("*/manifest.json"), key=lambda p: p.parent.name)
        records: list[RunRecord] = []
        for path in paths[offset : offset + limit]:
            try:
                records.append(public_record(runs.read(path.parent.name), compact=True))
            except AdvisoryError as exc:
                records.append(
                    {"run_id": path.parent.name[:32], "phase": "unknown", "outcome": "unknown", "code": exc.code}
                )
        return {
            "runs": records,
            "total": len(paths),
            "offset": offset,
            "limit": limit,
            "next_offset": offset + limit if offset + limit < len(paths) else None,
        }


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
                size = stream.tell()
                offset = max(0, size - 65536)
                stream.seek(offset)
                lines = stream.read(65536).decode(errors="replace").splitlines()
        except FileNotFoundError:
            lines, size, offset = [], 0, 0
        record["lines"] = lines[-tail:] if tail else []
        omitted = max(0, len(lines) - tail)
        record["tail"] = {
            "requested_lines": tail,
            "read_bytes": size - offset,
            "omitted_prefix_bytes": offset,
            "omitted_lines_in_window": omitted,
            "truncated": bool(offset or omitted),
        }
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
