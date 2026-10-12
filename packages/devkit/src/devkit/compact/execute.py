"""Run one command with its complete output in a log file, and return a bounded view of it.

``run_command`` never prints: it returns a ``CommandRun`` (exit code, log path,
``Scan``, notices) and the CLI renders it. The command runs in a session of its
own with stdin closed; when the caller is interrupted or terminated (Ctrl-C,
``SIGTERM``, ``SIGHUP``), the whole process group is stopped before the signal
propagates, so no test or build process outlives the run.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import logging
import os
import re
import shlex
import signal
import stat
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit.compact.errors import CommandNotStartedError, LogDirectoryError, SlowCommandNotice
from devkit.compact.scan import Scan, scan
from devkit.core.project import find_project_root

KEEP_LOGS = 20
STOP_GRACE = 5.0
LOG_ROOT = "devkit-run"

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class CommandRun:
    """One finished command: its exit code (``128 + N`` when signal ``N`` ended it), log and bounded output."""

    argv: tuple[str, ...]
    exit_code: int
    log: Path
    duration: float
    scan: Scan
    notices: tuple[AdvisoryError, ...] = ()

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @property
    def command(self) -> str:
        return shlex.join(self.argv)


def log_root() -> Path:
    """``<tmp>/devkit-run-<uid>``: private to the user, since ``/tmp`` may be shared."""
    return Path(tempfile.gettempdir()) / f"{LOG_ROOT}-{os.getuid()}"


def default_log_dir(cwd: Path) -> Path:
    """``<tmp>/devkit-run-<uid>/<hash>``: one directory per project, outside the work tree."""
    key = hashlib.sha256(str(find_project_root(cwd)).encode()).hexdigest()[:12]
    return log_root() / key


def _ensure_private(root: Path) -> None:
    """Create ``root`` as ``0700``; refuse it when it is a symlink or another user owns it."""
    try:
        root.mkdir(mode=0o700, exist_ok=True)
        info = os.lstat(root)
    except OSError as error:
        raise LogDirectoryError(
            f"cannot create the log directory {root}: {error.strerror or error}", target_files=[str(root)]
        ) from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise LogDirectoryError(
            f"the log directory {root} is not a directory owned by the current user",
            target_files=[str(root)],
            fix=f"rm -rf {shlex.quote(str(root))}  (after the user agrees)",
        )


def run_command(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    slow_after: float = 60.0,
    notices: bool = True,
    log_dir: Path | None = None,
) -> CommandRun:
    """Run ``argv`` to completion and scan its combined stdout and stderr.

    ``slow_after`` (seconds, ``0`` off) adds a ``RUN_SLOW_COMMAND`` notice;
    ``notices=False`` drops relayed ``[NOTICE]`` blocks. The newest
    ``KEEP_LOGS`` logs of ``log_dir`` (default ``default_log_dir``) are kept.
    Raises ``CommandNotStartedError`` when there is no command, the command
    cannot be started, or the working directory cannot be entered.
    """
    argv = tuple(argv)
    if not argv:
        raise CommandNotStartedError("no command to start", fix="Pass the command and its arguments")
    try:
        directory = (cwd or Path.cwd()).resolve()
    except FileNotFoundError as error:  # the shell's current directory was removed
        raise _directory_error(argv, os.environ.get("PWD", "."), "the current directory no longer exists") from error
    if not directory.is_dir():
        raise _directory_error(argv, str(directory), "not an existing directory")
    if log_dir is None:
        _ensure_private(log_root())
    logs = log_dir or default_log_dir(directory)
    logs.mkdir(parents=True, exist_ok=True)
    _prune(logs, KEEP_LOGS - 1)
    prefix = f"{time.strftime('%Y%m%d-%H%M%S')}-{_slug(argv)}-"
    with tempfile.NamedTemporaryFile(mode="w+b", prefix=prefix, suffix=".log", dir=logs, delete=False) as log:
        path = Path(log.name)
        started = time.monotonic()
        # Handlers first: a signal right after the start must still stop the command's process group.
        with _signals_exit():
            try:
                process = subprocess.Popen(
                    argv,
                    cwd=directory,
                    env=None if env is None else dict(env),
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            except OSError as error:
                log.close()
                path.unlink(missing_ok=True)
                reason = error.strerror or str(error)
                # The child reports a failed chdir with the directory as filename, a failed exec with the command.
                if error.filename is not None and Path(error.filename) == directory:
                    raise _directory_error(argv, str(directory), reason) from error
                raise CommandNotStartedError(f"cannot start {argv[0]!r}: {reason}", target_files=[argv[0]]) from error
            try:
                code = process.wait()
            except BaseException:
                _stop(process)
                raise
        duration = time.monotonic() - started
        if code < 0:
            code = 128 - code
        # Read back through the open file: a concurrent run may already have pruned the path.
        log.seek(0)
        # Only "\n" ends a line: a carriage return redraws it, and the scan keeps what is left visible.
        reader = io.TextIOWrapper(log.file, encoding="utf-8", errors="replace", newline="\n")  # pyright: ignore[reportArgumentType]
        try:
            result = scan(reader, notices=notices, base=(directory, cwd or Path.cwd()))
        finally:
            reader.detach()
    _log.info("%s exited %d after %.1fs in %s; log %s", shlex.join(argv), code, duration, directory, path)
    found: list[AdvisoryError] = []
    if slow_after and duration >= slow_after:
        found.append(
            SlowCommandNotice(
                f"{shlex.join(argv)} ran {duration:.0f}s, longer than --slow-after {slow_after:g}s",
                "Narrow the run (a test path, a keyword filter) or look for slow fixtures and external waits; "
                "--slow-after 0 turns this notice off",
            )
        )
    return CommandRun(argv, code, path, duration, result, tuple(found))


def _directory_error(argv: Sequence[str], directory: str, reason: str) -> CommandNotStartedError:
    return CommandNotStartedError(
        f"cannot start {argv[0]!r}: working directory {directory}: {reason}",
        target_files=[directory],
        fix="Run the command from an existing directory you can enter",
    )


def _slug(argv: Sequence[str]) -> str:
    words = [Path(argv[0]).name, *argv[1:2]]
    return re.sub(r"[^A-Za-z0-9._]+", "-", " ".join(words)).strip("-.")[:40] or "command"


def _prune(directory: Path, keep: int) -> None:
    """Delete all but the ``keep`` newest logs; a log another run removes first is skipped."""
    dated: list[tuple[float, Path]] = []
    for path in directory.glob("*.log"):
        with contextlib.suppress(OSError):
            dated.append((path.stat().st_mtime, path))
    for _, path in sorted(dated, reverse=True)[keep:]:
        with contextlib.suppress(OSError):
            path.unlink()


@contextlib.contextmanager
def _signals(handler: Callable[[int, object], None] | int, *signums: int) -> Iterator[None]:
    """Install ``handler`` for ``signums`` while the block runs; only the main thread can, elsewhere nothing changes."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    previous = {signum: signal.signal(signum, handler) for signum in signums}
    try:
        yield
    finally:
        for signum, old in previous.items():
            signal.signal(signum, old if old is not None else signal.SIG_DFL)


def _exit_on(signum: int, _frame: object) -> None:
    raise SystemExit(128 + signum)


def _signals_exit() -> contextlib.AbstractContextManager[None]:
    """Turn ``SIGTERM`` and ``SIGHUP`` into ``SystemExit(128 + N)``, so cleanup runs."""
    return _signals(_exit_on, signal.SIGTERM, signal.SIGHUP)


def _stop(process: subprocess.Popen[bytes]) -> None:
    """Terminate the command's process group, then kill it after ``STOP_GRACE`` seconds.

    Further interrupts are ignored meanwhile, so a second Ctrl-C cannot skip the kill.
    """
    with _signals(signal.SIG_IGN, signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=STOP_GRACE)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
