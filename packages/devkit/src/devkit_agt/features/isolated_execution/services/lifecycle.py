"""Execution observation, cancellation and guarded cleanup policies."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from devkit_agt.features.isolated_execution.models.record import TERMINAL, RunRecord
from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.isolated_execution.repositories.runs import Runs
from devkit_agt.features.worktree.repositories.execution import remove


def clean(runs: Runs, run_id: str) -> RunRecord:
    """Preserve durable result and logs while removing an eligible inactive checkout."""
    with runs.cleanup_lock(run_id) as lock_fd:
        record = runs.read(run_id)
        directory = runs.path(run_id)
        try:
            if record.get("outcome") not in TERMINAL or not (directory / "result.json").is_file():
                raise ValueError("only trustworthy terminal execution evidence permits cleanup")
            table = runtime.processes()
            supervisor = record.get("supervisor")
            if supervisor and runtime.same(supervisor, table.get(supervisor["pid"])):
                raise ValueError("supervisor is still active or its PID identity is unresolved")
            if not runtime.confirmed_quiescence(record):
                raise ValueError("positive managed-group quiescence proof is missing or incomplete")
            if runtime.live_owned(record):
                raise ValueError("managed process ownership remains active or unresolved")
            runtime.atomic(
                directory / "cleanup.json",
                {"outcome": "in_progress", "code": "EXECUTION_CLEAN_IN_PROGRESS", "started_at": time.time()},
            )
            outcome = remove(runs.base, Path(record["checkout"]), record["sha"], run_id, lock_fd)
            cleanup = {"outcome": outcome, "code": "EXECUTION_CLEANED", "completed_at": time.time()}
        except BaseException as exc:
            if not isinstance(exc, (OSError, ValueError, subprocess.CalledProcessError)):
                runtime.atomic(
                    directory / "cleanup.json",
                    {
                        "outcome": "unfinished",
                        "code": "EXECUTION_CLEAN_UNFINISHED",
                        "detail": type(exc).__name__,
                        "completed_at": time.time(),
                    },
                )
                raise
            cleanup = {"outcome": "refused", "code": "EXECUTION_CLEAN_REFUSED", "detail": str(exc)}
        runtime.atomic(directory / "cleanup.json", cleanup)
        record["cleanup"] = cleanup
        record["cleanup_requested"] = True
        return record


def wait(runs: Runs, run_id: str, timeout: float | None, cleanup: bool) -> RunRecord:
    """Observe internally; timeout and interruption never signal the execution."""
    started = time.monotonic()
    while True:
        record = runs.read(run_id)
        if record.get("outcome") == "unknown":
            record["observer"] = "unknown"
            return record
        if record.get("outcome") in TERMINAL:
            if cleanup:
                # Result is written before supervisor exit; collect its shutdown before cleanup.
                for _ in range(100):
                    identity = record.get("supervisor")
                    if not identity or not runtime.same(identity, runtime.processes().get(identity["pid"])):
                        break
                    time.sleep(0.02)
                record = clean(runs, run_id)
            record["observer"] = "completed"
            return record
        if timeout is not None and time.monotonic() - started >= timeout:
            record.update(observer="timeout", observer_code="EXECUTION_WAIT_TIMEOUT")
            return record
        time.sleep(0.05)


def cancel(runs: Runs, run_id: str) -> RunRecord:
    """Request supervisor-owned shutdown and wait for actual confirmed outcome."""
    record = runs.read(run_id)
    if record.get("outcome") in TERMINAL or record.get("outcome") == "unknown":
        return record
    (runs.path(run_id) / "cancel").touch()
    return wait(runs, run_id, 10, False)
