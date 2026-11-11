"""The one subprocess runner for Git.

``run_git`` returns bytes: Git paths are arbitrary bytes, so they are decoded with
``data.decode("utf-8", errors="surrogateescape")``, which keeps every name
round-trippable. ``run_git_text`` applies that rule for callers that want text,
``run_git_result`` serves commands whose nonzero exit is an answer, and
``is_ancestor`` is the shared ``merge-base --is-ancestor`` test. ``worktree_records`` and
``status_records`` read ``git worktree list --porcelain -z`` and ``git status --porcelain=v1 -z`` into records;
their pure parsers serve callers that run Git themselves. ``dirty_paths`` and ``changed_paths`` are the
uncommitted and committed path lists a write-scope check compares, and ``git_config`` reads one configuration value. These generic primitives live here; queries that encode one package's policy live in that package
and are built on them. ``repository_facts`` scopes a memo of where a repository is.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
from collections.abc import Collection, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from devkit_core.base.errors import GitError
from devkit_core.core.deadline import Deadline

DEFAULT_TIMEOUT = 60.0  # seconds; the one Git timeout every devkit area uses

# Queries whose answer only moves when a repository or work tree is created, moved or removed.
_FACTS = frozenset(
    {
        ("rev-parse", "--show-toplevel"),
        ("rev-parse", "--path-format=absolute", "--git-common-dir"),
        ("rev-parse", "--absolute-git-dir"),
    }
)
_ENVIRONMENT = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_CEILING_DIRECTORIES",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
)
_memo: ContextVar[dict[tuple[object, ...], bytes] | None] = ContextVar("devkit_git_facts", default=None)


@contextmanager
def repository_facts() -> Iterator[None]:
    """Memoize ``run_git``'s successful repository-location queries (``rev-parse --show-toplevel``,
    ``--git-common-dir``, ``--absolute-git-dir``) for the scope; nested scopes share the outer memo.

    For one command that creates, moves or removes no repository or work tree, so each answer is fixed for the
    scope: the memo is keyed by directory, query and the Git environment variables that change the answer. A failed
    query is not memoized.
    """
    if _memo.get() is not None:
        yield
        return
    token = _memo.set({})
    try:
        yield
    finally:
        _memo.reset(token)


class GitResult(NamedTuple):
    """The exit status and standard output of a Git command that ``run_git_result`` accepted."""

    returncode: int
    stdout: bytes


def run_git(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
    isolated_env: bool = False,
    new_session: bool = False,
) -> bytes:
    """Run ``git -C <cwd> <args...>`` and return its standard output.

    ``input`` is written to Git's standard input; without it Git's standard
    input is ``/dev/null``, so Git never consumes the caller's input (a hook's
    ref list) or waits on a prompt. ``timeout`` is in seconds; ``None`` waits
    indefinitely. The process inherits the environment, so the ``GIT_DIR`` /
    ``GIT_INDEX_FILE`` set by Git for hooks are honored, with ``LC_ALL=C``
    (Git's messages are never localized) and ``GIT_TERMINAL_PROMPT=0`` (Git
    fails instead of prompting for credentials) on top.

    Raises ``GitError`` when Git cannot be started, does not finish within
    ``timeout``, or exits nonzero; the error carries the command, the exit
    status (``None`` if there is none) and Git's decoded standard error.
    ``index`` sets ``GIT_INDEX_FILE`` for this call.

    ``deadline`` bounds the call by a shared ``Deadline`` instead of ``timeout``; passing a ``timeout`` other
    than ``DEFAULT_TIMEOUT`` with it is a programming error (``ValueError``), as it is for ``file_lock``. An
    expired deadline starts no Git, Git gets the time left on it, and a Git still running when it runs out is killed.
    Both raise ``deadline.exceeded("git <subcommand>")`` (``DeadlineExceededError`` unless the deadline
    has an error factory); every other failure is still ``GitError``.

    ``isolated_env`` drops every inherited ``GIT_*`` variable (``GIT_DIR``, ``GIT_WORK_TREE``, ``GIT_INDEX_FILE``,
    ...) before the ones above are set, so a hook's or a caller's repository overrides never redirect a command run
    in another work tree. ``new_session`` starts Git in a session of its own and, on a timeout or any other
    interruption, kills its whole process group, so the hooks and filters Git started (``post-checkout``, Git LFS)
    stop with it; the timeout is still a ``GitError`` whose ``__cause__`` is ``subprocess.TimeoutExpired``.
    """
    memo = _memo.get() if args in _FACTS and input is None and index is None and deadline is None else None
    key: tuple[object, ...] = ()
    if memo is not None:
        try:
            where = str(cwd) if os.path.isabs(cwd) else (os.getcwd(), str(cwd))
        except OSError:  # the process directory is gone: run Git unmemoized, as outside a scope
            memo = None
        else:
            environment = () if isolated_env else tuple(os.environ.get(name) for name in _ENVIRONMENT)
            key = (where, args, isolated_env, *environment)
            if key in memo:
                return memo[key]
    stdout = run_git_result(
        cwd,
        *args,
        input=input,
        timeout=timeout,
        index=index,
        deadline=deadline,
        isolated_env=isolated_env,
        new_session=new_session,
    ).stdout
    if memo is not None:
        memo[key] = stdout
    return stdout


def run_git_result(
    cwd: Path,
    *args: str,
    ok_returncodes: Collection[int] = (0,),
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
    isolated_env: bool = False,
    new_session: bool = False,
) -> GitResult:
    """Run Git as ``run_git`` does and return its exit status and standard output when the status is accepted.

    For a command whose nonzero exit is an answer, such as ``merge-tree --write-tree``, whose exit ``1`` reports
    conflicts on standard output: ``ok_returncodes`` names the accepted exit statuses (``0`` alone by default). Any
    other status raises ``GitError`` exactly as ``run_git`` does, as do a Git that cannot start or does not finish.
    Takes ``run_git``'s other options and environment; nothing is memoized.
    """
    command = ("git", "-C", str(cwd), *args)
    label = f"git {args[0]}" if args else "git"
    if deadline is not None:
        if timeout != DEFAULT_TIMEOUT:
            raise ValueError("run_git takes a timeout or a deadline, not both")
        deadline.check(label)
        timeout = max(deadline.remaining(), 0.001)
    inherited = {key: value for key, value in os.environ.items() if not (isolated_env and key.startswith("GIT_"))}
    env = {**inherited, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}
    if index is not None:
        env["GIT_INDEX_FILE"] = index
    stdin = subprocess.DEVNULL if input is None else None
    try:
        if new_session:
            completed = _run_in_session(command, input, env, timeout)
        else:
            completed = subprocess.run(
                command, input=input, stdin=stdin, capture_output=True, check=False, timeout=timeout, env=env
            )
    except subprocess.TimeoutExpired as exc:
        if deadline is not None:
            raise deadline.exceeded(label) from exc
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise GitError(f"{label} timed out after {timeout}s in {cwd}", command=command, stderr=stderr) from exc
    except OSError as exc:
        raise GitError(f"git is not available: {exc}", command=command) from exc
    if completed.returncode not in ok_returncodes:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(
            f"{label} failed in {cwd}: {stderr or f'exit status {completed.returncode}'}",
            command=command,
            returncode=completed.returncode,
            stderr=stderr,
        )
    return GitResult(completed.returncode, completed.stdout)


def _run_in_session(
    command: tuple[str, ...], input: bytes | None, env: dict[str, str], timeout: float | None
) -> subprocess.CompletedProcess[bytes]:
    """Run ``command`` in a session of its own with its output captured; a timeout (``TimeoutExpired``, re-raised)
    or any other exception first kills the whole process group and reaps Git."""
    process = subprocess.Popen(
        command,
        env=env,
        stdin=subprocess.DEVNULL if input is None else subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    with process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except BaseException:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_git_text(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
    isolated_env: bool = False,
    new_session: bool = False,
) -> str:
    """``run_git`` with its output decoded as UTF-8 with ``surrogateescape`` and one trailing newline removed.

    Only a single ``\\n`` is removed, so a one-line answer (a commit id, a path) comes back bare while leading and
    other trailing whitespace, which a path may carry, is kept. A caller that needs the output byte for byte (a file's
    content from ``git show``) uses ``run_git``. Raises as ``run_git`` does.
    """
    output = run_git(
        cwd,
        *args,
        input=input,
        timeout=timeout,
        index=index,
        deadline=deadline,
        isolated_env=isolated_env,
        new_session=new_session,
    )
    return output.decode("utf-8", errors="surrogateescape").removesuffix("\n")


def is_ancestor(cwd: Path, ancestor: str, descendant: str) -> bool:
    """Whether commit ``ancestor`` is contained in ``descendant`` (a commit is its own ancestor).

    Git's exit status 1 is the answer no; any other failure (an unknown revision, as in a shallow clone, or not a
    repository) raises ``GitError``. Both revisions are passed to Git as given; a caller taking them from input
    validates them first.
    """
    try:
        run_git(cwd, "merge-base", "--is-ancestor", ancestor, descendant)
    except GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


@dataclass(frozen=True)
class WorktreeRecord:
    """One worktree of ``git worktree list --porcelain``.

    ``path`` is Git's path, not resolved. ``head`` is Git's HEAD (all zeros for an unborn branch; ``None`` when Git
    prints none, as for a bare repository). ``branch`` is the full ref, ``None`` when detached or bare. ``locked``
    and ``prunable`` are ``None`` when absent, otherwise the reason (``""`` when Git gives none).
    """

    path: Path
    head: str | None = None
    branch: str | None = None
    bare: bool = False
    detached: bool = False
    locked: str | None = None
    prunable: str | None = None


@dataclass(frozen=True)
class StatusRecord:
    """One record of ``git status --porcelain=v1 -z``.

    ``code`` is the two-letter ``XY``; ``path`` is Git's path (an untracked directory keeps its trailing ``/``);
    ``original`` is the source of a rename or copy (``R`` or ``C`` in either column), otherwise ``None``.
    """

    code: str
    path: str
    original: str | None = None


def parse_worktree_records(raw: bytes) -> list[WorktreeRecord]:
    """The records of ``git worktree list --porcelain -z`` output, in Git's order (the first is the main worktree).

    Paths decode as UTF-8 with ``surrogateescape``. Fields before the first ``worktree`` field and unknown keys are
    ignored; empty output is ``[]``.
    """
    records: list[WorktreeRecord] = []
    fields: dict[str, str] | None = None

    def close() -> None:
        if fields is not None:
            records.append(
                WorktreeRecord(
                    path=Path(fields["worktree"]),
                    head=fields.get("HEAD"),
                    branch=fields.get("branch"),
                    bare="bare" in fields,
                    detached="detached" in fields,
                    locked=fields.get("locked"),
                    prunable=fields.get("prunable"),
                )
            )

    for item in _decode(raw).split("\0"):
        key, _, value = item.partition(" ")
        if key == "worktree":
            close()
            fields = {"worktree": value}
        elif item and fields is not None:
            fields.setdefault(key, value)
    close()
    return records


def worktree_records(cwd: Path, *, deadline: Deadline | None = None) -> list[WorktreeRecord]:
    """Run ``git worktree list --porcelain -z`` in ``cwd`` and parse it; raises as ``run_git`` does."""
    return parse_worktree_records(run_git(cwd, "worktree", "list", "--porcelain", "-z", deadline=deadline))


def parse_status_records(raw: bytes) -> list[StatusRecord]:
    """The records of ``git status --porcelain=v1 -z`` output, in Git's order.

    A rename or copy (``R`` or ``C`` in either column) is followed by its source field, kept as ``original``; a
    missing source field raises ``GitError``. Empty fields (the trailing one) yield no record. Paths decode as UTF-8
    with ``surrogateescape``.
    """
    records: list[StatusRecord] = []
    fields = iter(_decode(raw).split("\0"))
    for entry in fields:
        if not entry:
            continue
        if len(entry) < 4 or entry[2] != " ":
            raise GitError(f"malformed git status record: {entry!r}")
        code, path = entry[:2], entry[3:]
        original = None
        if "R" in code or "C" in code:
            original = next(fields, "")
            if not original:
                raise GitError(f"malformed git status record: {entry!r} lacks the source of its rename or copy")
        records.append(StatusRecord(code, path, original))
    return records


def status_records(
    cwd: Path,
    *pathspecs: str,
    untracked: str = "all",
    optional_locks: bool = False,
    deadline: Deadline | None = None,
) -> list[StatusRecord]:
    """Run ``git status --porcelain=v1 -z`` in ``cwd`` and parse it; raises as ``run_git`` does.

    ``untracked`` is ``--untracked-files``'s value; ``optional_locks=False`` passes ``--no-optional-locks`` (the
    index is not refreshed on disk); ``pathspecs`` follow ``--``.
    """
    args = [
        *(() if optional_locks else ("--no-optional-locks",)),
        "status",
        "--porcelain=v1",
        "-z",
        f"--untracked-files={untracked}",
        *(("--", *pathspecs) if pathspecs else ()),
    ]
    return parse_status_records(run_git(cwd, *args, deadline=deadline))


def dirty_paths(
    cwd: Path, *, untracked: str = "all", optional_locks: bool = False, deadline: Deadline | None = None
) -> list[str]:
    """Every path ``git status`` reports in ``cwd``, both sides of a rename or copy, sorted and without duplicates.

    Built on ``status_records`` (``untracked`` and ``optional_locks`` as there); paths are Git's, so an untracked
    directory listed whole (``untracked="normal"``) keeps its trailing ``/``. Raises as ``run_git`` does.
    """
    records = status_records(cwd, untracked=untracked, optional_locks=optional_locks, deadline=deadline)
    return sorted({name for record in records for name in (record.path, record.original) if name})


def changed_paths(cwd: Path, base: str, head: str, *, deadline: Deadline | None = None) -> list[str]:
    """The paths that differ between the commits ``base`` and ``head``, in Git's order.

    Runs ``git diff --no-renames --name-only -z <base> <head> --``: without rename detection, a renamed file lists
    both its removed and its added name. Paths decode as UTF-8 with ``surrogateescape``; both revisions are passed as
    given, so a caller taking them from input validates them first. Raises as ``run_git`` does.
    """
    output = run_git(cwd, "diff", "--no-renames", "--name-only", "-z", base, head, "--", deadline=deadline)
    return [name for name in _decode(output).split("\0") if name]


def git_config(
    cwd: Path, key: str, *, local: bool = False, type: str | None = None, deadline: Deadline | None = None
) -> str | None:
    """The value of the configuration ``key`` as ``git config --get`` prints it, ``None`` when it is unset (exit 1).

    ``local=True`` reads only the repository's own configuration (``--local``); ``type`` is ``--type``'s value
    (``bool`` canonicalizes ``yes``/``on``/``1`` to ``true``). One trailing newline is removed, as by ``run_git_text``;
    a key set to the empty string is ``""``. Any other failure raises ``GitError``.
    """
    args = ["config", *(("--local",) if local else ()), *((f"--type={type}",) if type else ()), "--get", key]
    try:
        return run_git_text(cwd, *args, deadline=deadline)
    except GitError as exc:
        if exc.returncode == 1:
            return None
        raise
