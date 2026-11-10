"""Captured standard-library supervisor. Never import the changing project's packages.

The run directory supplies this file and the worktree module before launch. Both
remain available independently of source checkout or dependency changes.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def atomic(path: Path, value: dict[str, Any]) -> None:
    """Publish a complete record; readers never observe partial JSON."""
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def processes() -> dict[int, dict[str, Any]]:
    """Read process identity and ancestry on macOS and Linux."""
    # The C locale fixes lstart at five tokens ("Tue Nov 10 16:41:11 2026");
    # localized renderings (ko_KR, ja_JP) differ and would misalign the columns.
    result = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,pgid=,lstart=,stat=,args="],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "LC_ALL": "C"},
    )
    found: dict[int, dict[str, Any]] = {}
    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip() if sys.platform.startswith("linux") else ""
    if sys.platform.startswith("linux") and not boot_id:
        raise RuntimeError("Linux boot identity is unavailable")
    for line in result.stdout.splitlines():
        parts = line.split(None, 9)
        if len(parts) != 10:
            continue
        pid, ppid, pgid = map(int, parts[:3])
        if parts[8].startswith("Z"):
            continue
        # Linux ps wall-clock start times can change across snapshots. Pair the
        # kernel start ticks with the boot identity to detect PID reuse, including
        # reuse after a reboot. Older records fail closed against this format.
        birth = " ".join(parts[3:8])
        proc = Path(f"/proc/{pid}/stat")
        if sys.platform.startswith("linux"):
            try:
                birth = f"linux:{boot_id}:" + proc.read_text().rsplit(")", 1)[1].split()[19]
            except (OSError, IndexError):
                continue
        found[pid] = {"pid": pid, "ppid": ppid, "pgid": pgid, "birth": birth, "argv": parts[9]}
    return found


def same(saved: dict[str, Any], current: dict[str, Any] | None) -> bool:
    """A stored PID alone never establishes ownership."""
    return current is not None and all(saved.get(k) == current.get(k) for k in ("pid", "birth"))


def confirmed_quiescence(record: dict[str, Any]) -> bool:
    """Require explicit producer evidence rather than absence of known PIDs.

    A preceding captured runtime may have reported terminal status after missing
    an orphan. Absence of its known PIDs is not positive ownership evidence.
    """
    proof = record.get("ownership")
    if not isinstance(proof, dict):
        return False
    verified = proof.get("verified_at")
    return (
        proof.get("quiescent") is True
        and proof.get("groups") == []
        and isinstance(verified, (int, float))
        and not isinstance(verified, bool)
        and math.isfinite(verified)
    )


def live_owned(record: dict[str, Any]) -> bool:
    """Inspect current managed liveness; this alone never authorizes cleanup."""
    if confirmed_quiescence(record):
        return False
    table = processes()
    groups = record.get("ownership", {}).get("groups", [])
    return any(p["pgid"] in groups for p in table.values()) or any(p["pid"] in table for p in record.get("managed", []))


def validate_group_leaders(
    known: dict[int, dict[str, Any]],
    leader: int,
    table: dict[int, dict[str, Any]],
    groups: set[int],
    *,
    unreaped: bool,
) -> None:
    """Reject unknown/reused established leaders before discovery or signals.

    Only the unreaped direct child has a kernel-held identity without an
    observed birth. Secondary groups need an already observed leader identity.
    """
    for group in groups:
        current = table.get(group)
        if current is None:
            continue
        original = known.get(group)
        if original is None:
            if group == leader and unreaped:
                continue
            raise RuntimeError("established group leader identity is unresolved")
        if not same(original, current):
            raise RuntimeError("established group leader identity changed")


def _discover(
    known: dict[int, dict[str, Any]],
    leader: int,
    table: dict[int, dict[str, Any]],
    *,
    unreaped: bool = True,
    groups: set[int] | None = None,
    retire: bool = True,
) -> None:
    # Established session/group IDs remain owned while members exist, even if
    # the leader was reaped between ps and poll. Retire only after observing emptiness.
    if groups is None:
        groups = {p["pgid"] for p in known.values() if p["pid"] == p["pgid"]}
        if unreaped:
            groups.add(leader)
    for group in list(groups):
        owner, current = known.get(group), table.get(group)
        if (owner and current and not same(owner, current)) or (
            retire and not any(p["pgid"] == group for p in table.values()) and not (unreaped and group == leader)
        ):
            groups.remove(group)
    if leader not in known and leader in table and unreaped:
        known[leader] = table[leader]
    changed = True
    while changed:
        changed = False
        for pid, row in table.items():
            parent = known.get(row["ppid"])
            if pid not in known and ((parent and same(parent, table.get(row["ppid"]))) or row["pgid"] in groups):
                known[pid] = row
                groups.add(row["pgid"])
                changed = True


def supervise(directory: Path) -> None:
    """Run preparation and argv in managed sessions and persist a terminal result."""
    record = json.loads((directory / "manifest.json").read_text())
    supervisor = processes().get(os.getpid())
    record.update(
        supervisor=supervisor,
        started_at=time.time(),
        managed=[],
        ownership={"groups": [], "quiescent": True, "verified_at": time.time(), "basis": "no_process_started"},
    )
    atomic(directory / "state.json", record)
    checkout = Path(record["checkout"])
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("GIT_", "PYTHON", "CONDA"))
        and k
        not in {
            "VIRTUAL_ENV",
            "__PYVENV_LAUNCHER__",
            "UV_PROJECT",
            "UV_WORKING_DIRECTORY",
            "UV_PROJECT_ENVIRONMENT",
            "UV_PYTHON",
            "UV_PYTHON_ENV_FILE",
            "UV_ENV_FILE",
            "UV_ACTIVE",
        }
    }
    env.update(
        TMPDIR=str(directory / "tmp"),
        TMP=str(directory / "tmp"),
        TEMP=str(directory / "tmp"),
        # Temporary consumers must not discover the retained base through .git.
        # Their own repositories remain discoverable below this boundary.
        GIT_CEILING_DIRECTORIES=str(directory.resolve()),
        DEVKIT_EXEC_RUN_ID=record["run_id"],
    )
    paths = [p for p in env.get("PATH", os.defpath).split(os.pathsep) if not (Path(p).parent / "pyvenv.cfg").is_file()]
    env["PATH"] = str(checkout / ".venv" / "bin") + os.pathsep + os.pathsep.join(paths)
    log = (directory / "output.log").open("ab", buffering=0)
    known: dict[int, dict[str, Any]] = {}
    history: list[dict[str, Any]] = []
    cancelled = False
    interrupted = False
    active: subprocess.Popen[bytes] | None = None

    def stop_observed(signum: int, _frame: Any) -> None:
        nonlocal interrupted
        interrupted = True

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, stop_observed)

    def run(argv: list[str], cwd: Path) -> int:
        nonlocal active, cancelled
        if (directory / "cancel").exists() or interrupted:
            cancelled = True
            return -signal.SIGTERM
        active = subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True
        )
        stopping: float | None = None
        groups = {active.pid}
        known.clear()
        record["ownership"] = {"groups": sorted(groups), "quiescent": False}
        atomic(directory / "state.json", record)
        while True:
            table = processes()
            validate_group_leaders(known, active.pid, table, groups, unreaped=active.returncode is None)
            _discover(known, active.pid, table, unreaped=active.returncode is None, groups=groups, retire=False)
            record["managed"] = history + list(known.values())
            record["ownership"] = {"groups": sorted(groups), "quiescent": False}
            atomic(directory / "state.json", record)
            if (directory / "cancel").exists() or interrupted:
                cancelled = True
                stopping = stopping or time.monotonic()
                sig = signal.SIGKILL if time.monotonic() - stopping >= 2 else signal.SIGTERM
                for identity in reversed(list(known.values())):
                    current = table.get(identity["pid"])
                    if same(identity, current):
                        with contextlib.suppress(ProcessLookupError):
                            os.kill(identity["pid"], sig)
            code = active.poll()
            if code is not None:
                # The scan before poll cannot establish post-exit quiescence.
                # Keep every established group through a fresh enumeration.
                table = processes()
                validate_group_leaders(known, active.pid, table, groups, unreaped=False)
                if any(p["pid"] in table and not same(p, table[p["pid"]]) for p in known.values()):
                    raise RuntimeError("managed process identity changed")
                _discover(known, active.pid, table, unreaped=False, groups=groups)
                record["managed"] = history + list(known.values())
                record["ownership"] = {"groups": sorted(groups), "quiescent": False}
                atomic(directory / "state.json", record)
                living = [p for p in known.values() if same(p, table.get(p["pid"]))]
                if not groups and not living:
                    history.extend(known.values())
                    known.clear()
                    active = None
                    record["ownership"] = {"groups": [], "quiescent": True, "verified_at": time.time()}
                    atomic(directory / "state.json", record)
                    return code
            # A changed identity is never signalled or treated as verified shutdown.
            if code is not None and any(p["pid"] in table and not same(p, table[p["pid"]]) for p in known.values()):
                raise RuntimeError("managed process identity changed")
            time.sleep(0.03)

    outcome = "setup_failed"
    native_code: int | None = None
    try:
        code = run(
            [
                sys.executable,
                str(directory / "checkout.py"),
                record["base"],
                str(checkout),
                record["sha"],
                record["run_id"],
            ],
            Path(record["base"]),
        )
        if code != 0:
            raise RuntimeError(f"checkout preparation exit={code}")
        if record["setup"] is not None:
            code = run(["/bin/sh", "-c", record["setup"]], checkout)
            if code != 0:
                raise RuntimeError(f"project setup exit={code}")
        if (checkout / ".devkit/installation.json").is_file():
            interpreter = checkout / ".venv/bin/python"
            if not interpreter.is_file() or not (checkout / ".venv").resolve().is_relative_to(checkout):
                raise RuntimeError(
                    "locked sync requires a checkout-local .venv/bin/python; configure worktree.setup or --setup"
                )
            code = run(
                [str(interpreter), "-m", "devkit_dist", "sync", "--locked", "--format", "json", "-w", str(checkout)],
                checkout,
            )
            if code != 0:
                raise RuntimeError(f"locked sync exit={code}")
        record.update(phase="running", command_started_at=time.time())
        atomic(directory / "state.json", record)
        native_code = run(record["argv"], checkout)
        outcome = "passed" if native_code == 0 else "failed"
    except Exception as exc:
        if record.get("phase") == "running":
            # Preparation completed; an unexecutable native argv is a command failure.
            outcome = "failed"
        record["detail"] = str(exc)
        log.write((str(exc) + "\n").encode())
    if cancelled:
        outcome = "interrupted" if interrupted else "cancelled"
    # Do not manufacture terminal evidence if any managed writer remains unresolved.
    if active is not None or not confirmed_quiescence(record):
        record.update(phase="unknown", outcome="unknown", detail="managed processes remain or identity is unresolved")
        atomic(directory / "state.json", record)
        return
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    record["resources"] = {
        "child_user_seconds": usage.ru_utime,
        "child_system_seconds": usage.ru_stime,
        "child_peak_rss_bytes": usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024),
    }
    record.update(phase=outcome, outcome=outcome, exit_code=native_code, completed_at=time.time())
    atomic(directory / "result.json", record)
    atomic(directory / "state.json", record)
    log.close()


if __name__ == "__main__":
    supervise(Path(sys.argv[1]))
