"""Run one command with its complete output in a log file, and return a bounded view of it.

``run_command`` never prints: it returns a ``CommandRun`` (exit code, log path,
``Scan``, notices) and the CLI renders it. The command runs in a session of its
own with stdin closed; when the caller is interrupted or terminated (Ctrl-C,
``SIGTERM``, ``SIGHUP``), the whole process group is stopped before
``CommandInterrupted`` propagates, so no test or build process outlives the run.
Processes the command leaves running in the background when it exits are not
stopped; what they write later is appended to the log, after the part the view
was made from.
"""

from __future__ import annotations

import contextlib
import errno
import hashlib
import io
import os
import re
import shlex
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError, Level
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core.logs import get_logger
from devkit_dist.base.errors import DevkitRootNestedError
from devkit_dist.features.project.repositories.project import find_project_root, git_toplevel

from devkit_agt.features.compact.models.errors import CommandNotStartedError, LogDirectoryError, SlowCommandNotice
from devkit_agt.features.compact.models.scan import Scan
from devkit_agt.features.compact.services.scan import scan

KEEP_LOGS = 20
STOP_GRACE = 5.0
_STOP_POLL = 0.05
LOG_ROOT = "devkit-run"
INTERRUPTS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
FAILURE_TAIL_LINES = 10  # last output lines a failed run's details show, beside its summaries

_log = get_logger(__name__)


@dataclass(frozen=True)
class CommandRun:
    """One finished command: its exit code (``128 + N`` when signal ``N`` ended it), log and bounded output.

    ``interrupted`` is the signal that interrupted the run (``0`` when it ran to the end); an interrupted run
    has an empty ``scan``.
    """

    argv: tuple[str, ...]
    exit_code: int
    log: Path
    duration: float
    scan: Scan
    notices: tuple[AdvisoryError, ...] = ()
    interrupted: int = 0

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.interrupted

    @property
    def command(self) -> str:
        return shlex.join(self.argv)

    def failure_details(self, prefix: str = "", *, failed_tests: bool = False) -> list[str]:
        """The advisory details of a failed run: ``<prefix>exit=<code>  log=<path>``, its summaries, its failed
        tests when ``failed_tests``, its last ``FAILURE_TAIL_LINES`` other output lines and its relayed errors."""
        found = self.scan
        lines = [f"{prefix}exit={self.exit_code}  log={self.log}"]
        lines += [f"  summary: {summary}" for summary in found.summaries]
        if failed_tests:
            lines += [f"  failed: {failure.test}: {failure.message}" for failure in found.failures]
        shown = set(found.summaries)
        tail = [line for line in found.output.splitlines() if line.strip() and line not in shown]
        lines += [f"  | {line}" for line in tail[-FAILURE_TAIL_LINES:]]
        lines += [
            f"  > {line}" for item in found.advisories if item.level is Level.ERROR for line in item.text.splitlines()
        ]
        return lines


class CommandInterrupted(SystemExit):
    """The run was interrupted (Ctrl-C) or terminated (``SIGTERM``, ``SIGHUP``) after the command started.

    Raised once the command's process group has been stopped. ``run`` is the
    interrupted run (its ``log`` holds the output up to the interruption,
    ``interrupted`` the signal); left uncaught it exits ``128 + N``, as the
    signal would have.
    """

    def __init__(self, run: CommandRun) -> None:
        super().__init__(128 + run.interrupted)
        self.run = run


def log_root() -> Path:
    """``<tmp>/devkit-run-<uid>``: private to the user, since ``/tmp`` may be shared."""
    return Path(tempfile.gettempdir()) / f"{LOG_ROOT}-{os.getuid()}"


def default_log_dir(cwd: Path) -> Path:
    """``<tmp>/devkit-run-<uid>/<hash>``: one directory per project, outside the work tree.

    The key only groups logs: a nested ``.devkit/`` (``DEVKIT_ROOT_NESTED``) does not stop a run, whose logs then go
    with the repository's top level.
    """
    try:
        root = find_project_root(cwd)
    except DevkitRootNestedError:
        root = git_toplevel(cwd) or cwd.resolve()
    key = hashlib.sha256(str(root).encode()).hexdigest()[:12]
    return log_root() / key


def _ensure_private(directory: Path) -> None:
    """Create ``directory`` as ``0700``; refuse it when it is a symlink, not a directory or another user's, and
    take away any access a group or others have to it."""
    try:
        directory.mkdir(mode=0o700, exist_ok=True)
        # Checked and changed through a descriptor that never follows a link, so what is checked is what changes.
        descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as error:
        if error.errno in (errno.EEXIST, errno.ENOTDIR, errno.ELOOP):
            raise _not_private(directory) from error
        raise _unusable(directory, error) from error
    try:
        info = os.fstat(descriptor)
        if info.st_uid != os.getuid():
            raise _not_private(directory)
        if info.st_mode & 0o077:
            os.fchmod(descriptor, 0o700)
    except OSError as error:
        raise _unusable(directory, error) from error
    finally:
        os.close(descriptor)


def _not_private(directory: Path) -> LogDirectoryError:
    return LogDirectoryError(
        f"the log directory {directory} is not a directory owned by the current user",
        target_files=[str(directory)],
        fix=f"rm -rf {shlex.quote(str(directory))}  (after the user agrees)",
    )


def _unusable(directory: Path, error: OSError) -> LogDirectoryError:
    return LogDirectoryError(
        f"cannot write logs to {directory}: {error.strerror or error}",
        target_files=[str(directory)],
        what_to_report="devkit run cannot write its log to its log directory",
    )


class RunCommand(BaseUseCase):
    """Run ``argv`` to completion and scan its combined stdout and stderr."""

    def execute(
        self,
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
        cannot be started, or the working directory cannot be entered;
        ``LogDirectoryError`` when the log cannot be written; and
        ``CommandInterrupted`` when the run is interrupted after the command
        started.
        """
        argv = tuple(argv)
        if not argv:
            raise CommandNotStartedError("no command to start", fix="Pass the command and its arguments")
        try:
            given = cwd or Path.cwd()
            directory = given.resolve()
        except FileNotFoundError as error:  # the shell's current directory was removed
            raise _directory_error(
                argv, os.environ.get("PWD", "."), "the current directory no longer exists"
            ) from error
        if not directory.is_dir():
            raise _directory_error(argv, str(directory), "not an existing directory")
        # Warning locations are made relative to the directory as given and as resolved; the command may remove it.
        base = (directory, given)
        logs = log_dir or default_log_dir(directory)
        if log_dir is None:
            _ensure_private(log_root())
            _ensure_private(logs)
        prefix = f"{time.strftime('%Y%m%d-%H%M%S')}-{_slug(argv)}-"
        with contextlib.ExitStack() as opened:
            try:
                logs.mkdir(parents=True, exist_ok=True)
                _prune(logs, KEEP_LOGS - 1)
                log = opened.enter_context(
                    tempfile.NamedTemporaryFile(mode="rb", prefix=prefix, suffix=".log", dir=logs, delete=False)
                )
                path = Path(log.name)
                # The command writes through a descriptor of its own, appending: a process that outlives it then
                # cannot write where the scan reads, which a shared file offset would make it do.
                output = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
            except OSError as error:
                raise _unusable(logs, error) from error
            started = time.monotonic()
            interrupts = _Interrupts()
            # Handlers first: a signal right after the start must still stop the command's process group.
            with _signals(interrupts.handle, *INTERRUPTS):
                try:
                    process = subprocess.Popen(
                        argv,
                        cwd=directory,
                        env=None if env is None else dict(env),
                        stdin=subprocess.DEVNULL,
                        stdout=output,
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
                    raise CommandNotStartedError(
                        f"cannot start {argv[0]!r}: {reason}", target_files=[argv[0]]
                    ) from error
                finally:
                    os.close(output)
                try:
                    interrupts.started()
                    code = _exit_code(process.wait())
                    duration = time.monotonic() - started
                    # What the command wrote until it exited; the open file is read, since a concurrent run may
                    # already have pruned the path.
                    size = os.fstat(log.fileno()).st_size
                    # Only "\n" ends a line: a carriage return redraws it, and the scan keeps what is left visible.
                    with io.TextIOWrapper(
                        io.BufferedReader(_LogReader(log.fileno(), size)),
                        encoding="utf-8",
                        errors="replace",
                        newline="\n",
                    ) as reader:
                        result = scan(reader, notices=notices, base=base)
                except _Signalled as signalled:
                    _stop(process)
                    code = _exit_code(process.returncode)
                    run = CommandRun(argv, code, path, time.monotonic() - started, Scan(), interrupted=signalled.signum)
                    _log.info("%s interrupted by signal %d; log %s", shlex.join(argv), signalled.signum, path)
                    raise CommandInterrupted(run) from None
                except BaseException:
                    _stop(process)
                    raise
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


run_command = RunCommand().execute


def _exit_code(returncode: int) -> int:
    return 128 - returncode if returncode < 0 else returncode


class _LogReader(io.RawIOBase):
    """The log's first ``size`` bytes, read with ``pread``: no other descriptor's offset moves the reads."""

    def __init__(self, descriptor: int, size: int) -> None:
        super().__init__()
        self.descriptor = descriptor
        self.size = size
        self.offset = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: memoryview) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        data = os.pread(self.descriptor, min(len(buffer), self.size - self.offset), self.offset)
        buffer[: len(data)] = data
        self.offset += len(data)
        return len(data)


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


class _Signalled(BaseException):
    """An interrupting signal arrived while the command ran."""

    def __init__(self, signum: int) -> None:
        super().__init__(signum)
        self.signum = signum


class _Interrupts:
    """Turn ``INTERRUPTS`` into ``_Signalled`` once the command has started, so its group is stopped first.

    While ``Popen`` starts it, a signal is held back and raised by ``started``:
    raised inside ``Popen``, it would leave the new session running with nothing
    to stop it.
    """

    def __init__(self) -> None:
        self.starting = True
        self.held = 0

    def handle(self, signum: int, _frame: object) -> None:
        if self.starting:
            self.held = self.held or signum
            return
        raise _Signalled(signum)

    def started(self) -> None:
        self.starting = False
        if self.held:
            raise _Signalled(self.held)


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


def _group_alive(pgid: int) -> bool:
    """Whether the process group ``pgid`` still has a running member."""
    try:
        os.killpg(pgid, 0)
    except (ProcessLookupError, PermissionError):  # PermissionError: on macOS, when only zombies are left
        return False
    return True


def _leader_exited(pid: int) -> bool:
    """Whether the group leader ``pid`` (a child of this process) has exited, without reaping it (``WNOWAIT``).

    ``False`` where ``os.waitid`` is unavailable (macOS before Python 3.13).
    """
    waitid = getattr(os, "waitid", None)
    if waitid is None:
        return False
    try:
        return waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None
    except ChildProcessError:  # already reaped
        return True


def _live_members(pgid: int) -> bool | None:
    """Whether the process group ``pgid`` has a member that is not a zombie, read from ``/proc/<pid>/stat``.

    ``None`` where ``/proc`` is unavailable (macOS).
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    if not os.path.exists("/proc/self/stat"):
        return None
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat", "rb") as stream:
                stat = stream.read()
        except OSError:  # the process exited meanwhile
            continue
        # ``pid (comm) state ppid pgrp ...``: ``comm`` may hold spaces and parentheses, so split after the last ``)``.
        fields = stat[stat.rfind(b")") + 1 :].split()
        if len(fields) > 2 and fields[2] == str(pgid).encode() and fields[0] != b"Z":
            return True
    return False


def _only_zombies_left(pid: int) -> bool:
    """Whether the group led by ``pid`` holds nothing but zombies, its exited (unreaped) leader among them.

    Linux counts a zombie as a group member, so ``_group_alive`` cannot tell; ``False`` where ``/proc`` or
    ``os.waitid`` is unavailable.
    """
    return _leader_exited(pid) and _live_members(pid) is False


def _stop(process: subprocess.Popen[bytes]) -> None:
    """Terminate the command's process group, then kill what is left of it after ``STOP_GRACE`` seconds.

    The leader exiting is not enough: a member that ignores ``SIGTERM`` is killed once the grace ends,
    so nothing in the group outlives the run. Further interrupts are ignored meanwhile, so a second
    Ctrl-C cannot skip the kill.

    The leader is reaped only once the group is done with: while it is an unreaped zombie its PID,
    which is the group ID, cannot be reused, so no signal can reach another process group. A leader
    this run has already reaped (the command had exited) is not signalled at all, since its group ID
    may name another group by now; what it left in the background is not stopped, as when the run
    ends normally. On macOS a group left with zombies only refuses even signal ``0`` (``EPERM``), which
    ends the wait at once. On Linux a zombie still counts as a member, so the unreaped leader keeps the
    group alive; the wait ends early instead once the leader has exited (``os.waitid`` with ``WNOWAIT``,
    which does not reap it) and ``/proc`` shows no member of the group that is not a zombie. Where
    neither applies, an interrupted run waits the full ``STOP_GRACE`` before the ``SIGKILL``. Either
    way the ``SIGKILL`` goes to a group that ``_group_alive`` still reports, so a member the ``/proc``
    scan missed while it started is killed too.
    """
    if process.returncode is not None:
        return
    with _signals(signal.SIG_IGN, *INTERRUPTS):
        deadline = time.monotonic() + STOP_GRACE
        with contextlib.suppress(ProcessLookupError, PermissionError):  # PermissionError: zombies only (macOS)
            os.killpg(process.pid, signal.SIGTERM)
        while _group_alive(process.pid) and not _only_zombies_left(process.pid) and time.monotonic() < deadline:
            time.sleep(_STOP_POLL)
        if _group_alive(process.pid):
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
        process.wait()
