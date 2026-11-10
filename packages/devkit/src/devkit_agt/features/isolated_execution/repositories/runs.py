"""Persistent run records outside disposable execution checkouts."""

from __future__ import annotations

import fcntl
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit.advisory import AdvisoryError

from devkit_agt.features.isolated_execution.models.record import TERMINAL, RunRecord
from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.worktree.repositories import execution


def error(code: str, message: str) -> AdvisoryError:
    """A stable actionable execution error."""
    return AdvisoryError.invalid_input(
        message,
        code=code,
        fix="Inspect uv run devkit exec list and retained execution logs; repair the reported condition before retrying",
    )


class Runs:
    """Repository-bound storage and per-run cleanup serialization."""

    def __init__(self, root: Path) -> None:
        try:
            self.root = Path(execution.git(root, "rev-parse", "--show-toplevel"))
            self.common = Path(execution.git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
            first = execution.git(root, "worktree", "list", "--porcelain").splitlines()[0]
        except (OSError, subprocess.CalledProcessError, IndexError) as exc:
            raise error("EXECUTION_REPOSITORY_UNREADABLE", "exec requires an accessible local Git repository") from exc
        if not first.startswith("worktree ") or not (Path(first[9:]) / ".git").exists():
            raise error("EXECUTION_REPOSITORY_UNSUPPORTED", "a retained non-bare checkout is required")
        self.base = Path(first[9:])
        self.directory = self.common / "devkit" / "executions"

    def path(self, run_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{32}", run_id):
            raise error("EXECUTION_ID_INVALID", "run ID must be the 32 hexadecimal characters returned by start")
        return self.directory / run_id

    def read(self, run_id: str) -> RunRecord:
        directory = self.path(run_id)
        try:
            manifest = json.loads((directory / "manifest.json").read_text())
            if manifest["run_id"] != run_id or manifest["repository"] != str(self.common):
                raise ValueError("repository or run identity differs")
            expected = self.base.parent / f"{self.base.name}-exec-{run_id}"
            if manifest["checkout"] != str(expected):
                raise ValueError("checkout identity differs")
            target = directory / "result.json"
            if not target.exists():
                target = directory / "state.json"
            if not target.exists():
                # Before the supervisor publishes state, the launcher's captured identity applies.
                target = directory / "launch.json"

            def validated(value: RunRecord) -> RunRecord:
                for key in ("run_id", "repository", "checkout", "sha", "argv"):
                    if value[key] != manifest[key]:
                        raise ValueError(f"{key} differs from captured manifest")
                return value

            record = validated(json.loads(target.read_text()) if target.exists() else manifest.copy())
            if record.get("outcome") not in TERMINAL:
                identity = record.get("supervisor")
                table = runtime.processes()
                if not identity or not runtime.same(identity, table.get(identity["pid"])):
                    # Publication precedes supervisor exit. The state snapshot may
                    # predate both; recheck durable evidence before declaring loss.
                    result = directory / "result.json"
                    if result.exists():
                        record = validated(json.loads(result.read_text()))
                    if record.get("outcome") not in TERMINAL:
                        record.update(phase="unknown", outcome="unknown")
            cleanup = directory / "cleanup.json"
            if cleanup.exists():
                record["cleanup"] = json.loads(cleanup.read_text())
            return record
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise error("EXECUTION_RECORD_UNREADABLE", f"execution evidence cannot be trusted: {exc}") from exc

    def launch(self, sha: str, argv: tuple[str, ...], setup: str | None) -> RunRecord:
        if sys.platform != "darwin" and not sys.platform.startswith("linux"):
            raise error("EXECUTION_PLATFORM_UNSUPPORTED", "exec requires POSIX macOS or Linux")
        if (
            not re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", sha)
            or not argv
            or (setup is not None and not setup.strip())
        ):
            raise error(
                "EXECUTION_ARGUMENT_INVALID",
                "start requires a full commit SHA, native argv after -- and a nonempty setup when supplied",
            )
        try:
            sha = execution.git(self.root, "rev-parse", "--verify", f"{sha}^{{commit}}")
        except subprocess.CalledProcessError as exc:
            raise error("EXECUTION_REF_UNKNOWN", "requested commit is not available locally") from exc
        run_id = uuid.uuid4().hex
        directory = self.path(run_id)
        directory.mkdir(parents=True)
        (directory / "tmp").mkdir()
        shutil.copyfile(runtime.__file__, directory / "runtime.py")
        shutil.copyfile(execution.__file__, directory / "checkout.py")
        interpreter = str(Path(getattr(sys, "_base_executable", sys.executable)).resolve())
        record: RunRecord = {
            "schema": 1,
            "run_id": run_id,
            "repository": str(self.common),
            "base": str(self.base),
            "sha": sha,
            "argv": list(argv),
            "setup": setup,
            "runtime": interpreter,
            "checkout": str(self.base.parent / f"{self.base.name}-exec-{run_id}"),
            "environment": str(self.base.parent / f"{self.base.name}-exec-{run_id}" / ".venv"),
            "created_at": time.time(),
            "phase": "preparing",
            "outcome": None,
            "exit_code": None,
            "log": str(directory / "output.log"),
            "result": str(directory / "result.json"),
            "managed": [],
        }
        runtime.atomic(directory / "manifest.json", record)
        with (directory / "supervisor.log").open("ab", buffering=0) as log:
            process = subprocess.Popen(
                [interpreter, "-I", str(directory / "runtime.py"), str(directory)],
                cwd=directory,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
        # Capture launch ownership before returning; preparation and execution remain asynchronous.
        table = runtime.processes()
        record["supervisor"] = table.get(process.pid)
        runtime.atomic(directory / "launch.json", record)
        # Supervisor owns state.json; never overwrite it from the launching process.
        for _ in range(100):
            if (directory / "state.json").exists():
                return record
            if process.poll() is not None:
                break
            time.sleep(0.01)
        else:
            # A slow but positively identified supervisor is still pending, not lost.
            if record["supervisor"] and runtime.same(record["supervisor"], runtime.processes().get(process.pid)):
                return record
        record.update(phase="unknown", outcome="unknown")
        return record

    @contextmanager
    def cleanup_lock(self, run_id: str) -> Iterator[int]:
        with (self.path(run_id) / "cleanup.lock").open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            yield stream.fileno()
