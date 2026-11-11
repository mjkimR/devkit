"""The registry operations a worktree performs on its own task: creation registration and release.

A worktree runs one task: every dirty path Git reports there at creation is attributed to it. Libraries never print:
each function returns its result with the warnings to report (``notices``).
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from devkit.advisory import Actor, AdvisoryError, Level, Retry
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core.logs import get_logger
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT

from devkit_spec.base.errors import (
    ScopeRecordInvalidWarning,
    ScopeSharedPathError,
    ScopeSharedWorktreeWarning,
    ScopeTokenExistsError,
)
from devkit_spec.features.policy.services.config import read_spec_config
from devkit_spec.features.scope.models.deadline import ROLLBACK_SECONDS, Deadline
from devkit_spec.features.scope.models.model import Problem, Record, ScopeSet
from devkit_spec.features.scope.models.registry import Registry, token_hash
from devkit_spec.features.scope.repositories.localfs import LocalRegistry
from devkit_spec.features.scope.repositories.location import (
    Location,
    base_ref,
    head_revision,
    incomplete_token,
    load_token,
    locate,
    remove_token,
    save_token,
)
from devkit_spec.features.scope.repositories.source import FilesystemReader, ReadBudget
from devkit_spec.features.scope.services.observation import add_paths, dirty
from devkit_spec.features.scope.usecases.inputs import from_spec


@dataclass(frozen=True)
class Session:
    """An open registry: the location of this workspace, the adapter and the command's deadline."""

    location: Location
    registry: LocalRegistry
    deadline: Deadline


def open_session(root: Path) -> Session:
    """Read ``[tool.spec.scope]``, locate the registry for the workspace at ``root`` and start the deadline."""
    config = read_spec_config(root).scope
    deadline = Deadline(config.timeout)
    location = locate(root, config, deadline)
    return Session(location, LocalRegistry(location.shared_path), deadline)


# --- register -----------------------------------------------------------------------------------------------------


@dataclass
class Registered:
    location: Location
    record: Record
    token: str
    notices: list[AdvisoryError] = field(default_factory=list)


def creation_scope(location: Location, spec_dir: str, deadline: Deadline) -> ScopeSet:
    """The declared scope of the bundle plus the worktree's staged, unstaged and untracked paths, read through
    collect's observation service (``services.observation``). The committed range is empty at creation (it starts at
    the registration HEAD), so none is read; a dirty path outside the path contract is unresolved (``invalid-path``).
    """
    scope = from_spec(location.root, spec_dir)
    reader = FilesystemReader(location.root, deadline, ReadBudget())
    add_paths(scope, dirty(location.root, deadline), reader, deadline)
    scope.observed.sort(key=lambda path: path.path)
    return scope


class RegisterScopeUseCase(BaseUseCase):
    def execute(self, session: Session, spec_dir: str, task_id: str | None = None) -> Registered:
        """Register the bundle at the workspace-relative ``spec_dir`` as this worktree's task and save its token.

        ``task_id`` defaults to the spec ID. The record keeps HEAD as ``base_revision`` and the branch the base checkout
        is on as ``base_ref``. Raises ``ScopeTokenExistsError`` when this worktree already holds a token, also when a
        concurrent registration saved its token first; a record whose token could not be saved is removed again.
        """
        location, registry, deadline = session.location, session.registry, session.deadline
        if location.token_path.exists():
            raise ScopeTokenExistsError("this worktree already registered a task")
        base = head_revision(location.root, deadline)
        ref = base_ref(location, deadline)
        scope = creation_scope(location, spec_dir, deadline)
        record = Record(
            namespace=location.namespace,
            task_id=task_id or scope.id,
            worktree=str(location.root),
            base_revision=base,
            base_ref=ref,
            spec=spec_dir,
            scopes=tuple(scope.all_paths()),
            unresolved=tuple(scope.unresolved),
        )
        token, stored = registry.register(record, deadline)
        try:
            save_token(location.token_path, token)
        except OSError as exc:
            # never leave a record nobody can release; a failed rollback is a detail of the original error
            details = _rollback(registry, stored, token)
            target = [str(location.token_path)]
            if isinstance(exc, FileExistsError):
                raise ScopeTokenExistsError(
                    "another registration in this worktree saved its token first", *details, target_files=target
                ) from exc
            raise ScopeSharedPathError(f"the token could not be saved: {exc}", *details, target_files=target) from exc
        notices: list[AdvisoryError] = []
        if stored.shared_worktree:
            notices.append(
                ScopeSharedWorktreeWarning(
                    f"another task registered this worktree too; changes observed in {stored.worktree} count for both",
                    target_files=[stored.worktree],
                )
            )
        return Registered(location, stored, token, notices)


def _rollback(registry: Registry, stored: Record, token: str) -> list[str]:
    """Release the record just registered, under its own deadline; the failure as a detail line, if any."""
    try:
        registry.release(stored.namespace, stored.task_id, token, Deadline(ROLLBACK_SECONDS))
    except (AdvisoryError, OSError) as exc:
        message = exc.message if isinstance(exc, AdvisoryError) else str(exc)
        return [f"the record of task {stored.task_id} could not be removed again and has no token: {message}"]
    return []


def auto_register(root: Path, spec_dir: str) -> Registered | None:
    """Retain best-effort creation snapshots without giving workers maintenance duties: every registration notice
    and failure is only a verbose diagnostic."""
    try:
        session = open_session(root)
        if not session.location.linked:
            return None
        registered = RegisterScopeUseCase().execute(session, spec_dir)
        for notice in registered.notices:
            _automatic_diagnostic(notice.code)
        registered.notices = []
        return registered
    except Exception as exc:
        # Cancellation/termination are BaseException and intentionally remain outside this boundary.
        _automatic_diagnostic(getattr(exc, "code", "SPEC_SCOPE_AUTO_REGISTER_FAILED"))
        return None


_log = get_logger(__name__)


def _automatic_diagnostic(code: str) -> None:
    with contextlib.suppress(Exception):
        _log.info("SPEC_SCOPE_AUTO_REGISTER_DIAGNOSTIC cause=%s", code)


# --- own record ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Own:
    token: str
    record: Record
    others: list[Record]
    problems: list[Problem]


def own(session: Session, *, cleanup: bool = True) -> Own | None:
    """This worktree's record (found by its token) and the other records of the namespace.

    ``None`` without a token or when its record is gone (released or swept). Raises ``SPEC_SCOPE_RECORD_INVALID`` at
    ``ERROR`` (``INTERACTION``) when the record is not found while unreadable record files may hold it
    (``Registry.may_hold``); unreadable files that cannot be it are only ``problems``.
    """
    location = session.location
    token = load_token(location.token_path, cleanup=cleanup)
    if token is None:
        return None
    records, problems = session.registry.query(location.namespace, session.deadline)
    digest = token_hash(token)
    mine = [record for record in records if record.token_hash == digest]
    if not mine:
        suspects = _suspects(session, problems, digest)
        if suspects:
            raise _unreadable(location, suspects, _OWN_UNREADABLE)
        return None
    others = [record for record in records if record.token_hash != digest]
    return Own(token, mine[0], others, problems)


_OWN_UNREADABLE = (
    "this worktree's record is not among the readable records and may be one of the record files that cannot be read"
)


def _suspects(session: Session, problems: Sequence[Problem], digest: str) -> list[Problem]:
    """The unreadable record files that may be the record of the token hashed to ``digest``."""
    namespace = session.location.namespace
    return [problem for problem in problems if session.registry.may_hold(namespace, problem, digest)]


def _unreadable(location: Location, problems: Sequence[Problem], message: str) -> ScopeRecordInvalidWarning:
    """The record looked for may be one of the unreadable ``problems``: an ``ERROR`` the user resolves
    (``INTERACTION``), because only a person can tell whether those files may be repaired or deleted. Until then
    nothing is removed and this worktree's token is kept."""
    directory = location.shared_path / location.namespace
    return ScopeRecordInvalidWarning(
        f"{message}; this worktree's token is kept until the files are repaired or removed",
        *(f"{problem.file}: {problem.reason}" for problem in problems),
        level=Level.ERROR,
        actor=Actor.USER,
        retry=Retry.AFTER_FIX,
        what_to_report=(
            "The record files in [TARGET] cannot be read and may hold the record this command needs; "
            "this worktree's token is kept"
        ),
        fix=(
            "Once the user decides, repair the record files in [TARGET] or delete those whose tasks are finished "
            f"({DEVKIT} spec scope sweep lists them with verdict=error), then rerun the same command"
        ),
        target_files=[location.shown(directory / problem.file) for problem in problems],
    )


# --- release ------------------------------------------------------------------------------------------------------


@dataclass
class Released:
    """``task`` is ``""`` when this worktree held no token (``registered`` false) or its record was already gone."""

    task: str
    revision: int
    registered: bool
    already: bool
    notices: list[AdvisoryError] = field(default_factory=list)


class ReleaseScopeUseCase(BaseUseCase):
    def execute(self, session: Session, task_id: str | None = None) -> Released:
        """Remove this worktree's record with its token and delete the token; repeating is a no-op.

        Without a token nothing happens (``registered`` false), with or without ``task_id``; an incomplete token file
        (one ``load_token`` takes for no token) is removed. With ``task_id`` the token must own that record
        (``ScopeTokenMismatchError``). A token whose record is gone
        is removed (orphaned), unless an unreadable record file may hold that record. ``SPEC_SCOPE_RECORD_INVALID`` at
        ``ERROR`` (the token kept) is raised only when the record looked for may be unreadable: with ``task_id`` when
        that task's own record file cannot be read, without it when an unreadable file may hold this token's record.
        """
        location, registry, deadline = session.location, session.registry, session.deadline
        token = load_token(location.token_path)
        if token is None:
            # Nothing of this worktree is registered: there is nothing to release, with or without --task-id.
            if incomplete_token(location.token_path):
                remove_token(location.token_path)  # a token nobody can present: an interrupted save
            return Released("", 0, registered=False, already=False)
        records, problems = registry.query(location.namespace, deadline)
        digest = token_hash(token)
        suspects = _suspects(session, problems, digest)
        if task_id:
            target = next((record for record in records if record.task_id == task_id), None)
            named = [problem for problem in problems if problem.file == registry.record_file(task_id)]
            if target is None and named:
                raise _unreadable(location, named, f"the record of task {task_id} cannot be read")
        else:
            target = next((record for record in records if record.token_hash == digest), None)
            if target is None and suspects:
                raise _unreadable(location, suspects, _OWN_UNREADABLE)
        if target is None:
            if not suspects and not any(record.token_hash == digest for record in records):
                remove_token(location.token_path)  # orphaned: its record was released or swept
            return Released(task_id or "", 0, registered=True, already=True)
        registry.release(location.namespace, target.task_id, token, deadline)
        remove_token(location.token_path)
        return Released(target.task_id, target.revision, registered=True, already=False)
