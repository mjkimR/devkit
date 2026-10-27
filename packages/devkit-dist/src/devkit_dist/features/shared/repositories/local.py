"""Same-user POSIX artifact storage. Reads never initialize or clean storage."""

from __future__ import annotations

import contextlib
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import stat
import tempfile
import time
import uuid
from collections.abc import Callable, Iterator
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.deadline import Deadline
from devkit_core.core.git import run_git

from devkit_dist.features.project.repositories.invocation import guard_execution
from devkit_dist.features.shared.models.api import (
    DIGEST,
    GENERATION,
    MAX_BYTES,
    TTL,
    Artifact,
    ArtifactMetadata,
    Page,
    PutRequest,
    RepositoryContext,
    SweepResult,
    decode_cursor,
    encode_cursor,
    generation,
    validate_filter,
    validate_page,
)
from devkit_dist.features.shared.models.errors import (
    AccessError,
    ExclusionError,
    ExpiredError,
    InputError,
    MissingError,
    SharedError,
    TimeoutError,
    WorkspaceError,
)

RELATIVE = ".devkit/.shared"


def deadline() -> Deadline:
    return Deadline(10, error=lambda what, _: TimeoutError(f"ten-second deadline exceeded: {what}"))


def _git(root: Path, budget: Deadline, *args: str) -> str:
    return os.fsdecode(run_git(root, *args, deadline=budget)).strip()


def _safe(path: Path, *, directory: bool) -> None:
    for part in (*reversed(path.parents), path):
        if part.is_symlink():
            raise SharedError("symlink path refused")
        if part.exists():
            mode = part.stat().st_mode
            if not (stat.S_ISDIR(mode) if part != path or directory else stat.S_ISREG(mode)):
                raise SharedError("nonregular storage path refused")


def discover(workspace: Path, budget: Deadline | None = None) -> RepositoryContext:
    budget = budget or deadline()
    try:
        workspace = workspace.absolute()
        _safe(workspace, directory=True)
        top = Path(_git(workspace, budget, "rev-parse", "--show-toplevel")).resolve()
        if top != workspace.resolve():
            raise WorkspaceError("workspace must be a Git checkout root")
        common = Path(_git(top, budget, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
        records = _git(top, budget, "worktree", "list", "--porcelain").split("\n\n")
        first = records[0].splitlines()
        if not first or "bare" in first or not first[0].startswith("worktree "):
            raise WorkspaceError("a retained non-bare main checkout is required")
        main = Path(first[0][9:])
        _safe(main, directory=True)
        if (
            not main.is_dir()
            or Path(_git(main, budget, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve() != common
            or Path(_git(main, budget, "rev-parse", "--show-toplevel")).resolve() != main.resolve()
        ):
            raise WorkspaceError("retained main checkout identity does not match")
        return RepositoryContext(top, main, common, hashlib.sha256(os.fsencode(common)).hexdigest())
    except PermissionError as exc:
        raise AccessError("workspace access denied") from exc
    except GitError as exc:
        raise WorkspaceError("cannot discover a retained main checkout") from exc


@contextlib.contextmanager
def _lock(path: Path, budget: Deadline, *, write: bool, create: bool = False) -> Iterator[None]:
    _safe(path, directory=False)
    flags = (os.O_RDWR if write else os.O_RDONLY) | os.O_NOFOLLOW | os.O_NONBLOCK
    if create:
        flags |= os.O_CREAT
    fd = os.open(path, flags, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise SharedError("lock must be regular")
        while True:
            budget.check("lock acquisition")
            try:
                fcntl.flock(fd, (fcntl.LOCK_EX if write else fcntl.LOCK_SH) | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(min(0.01, max(0, budget.remaining())))
        yield
    finally:
        os.close(fd)


def _worktrees(context: RepositoryContext, budget: Deadline) -> list[Path]:
    return [
        Path(line[9:])
        for line in _git(context.workspace, budget, "worktree", "list", "--porcelain").splitlines()
        if line.startswith("worktree ")
    ]


def _eligible(context: RepositoryContext, budget: Deadline) -> None:
    for root in _worktrees(context, budget):
        _safe(root / RELATIVE, directory=True)
        # Git check-ignore cannot report an ancestor negation for an absent child.
        # Refuse applicable higher-precedence negations before adding info/exclude.
        for base, candidate in ((root, RELATIVE), (root / ".devkit", ".shared")):
            ignore = base / ".gitignore"
            _safe(ignore, directory=False)
            if not ignore.exists():
                continue
            for line in ignore.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
                if not line.startswith("!"):
                    continue
                pattern = re.sub(r"\\(.)", r"\1", line[1:].rstrip()).removesuffix("/")
                anchored = pattern.startswith("/") or "/" in pattern
                pattern = pattern.removeprefix("/").replace("**/", "*")
                # Conservatively cover Git bracket expressions, including POSIX classes.
                pattern = re.sub(r"\[.*\]", "*", pattern)
                components = candidate.split("/")
                targets = ["/".join(components[:i]) for i in range(1, len(components) + 1)] if anchored else components
                if any(fnmatch.fnmatchcase(value.casefold(), pattern.casefold()) for value in targets):
                    raise ExclusionError("an ancestor ignore rule can re-include shared storage")
        if _git(root, budget, "ls-files", "--", RELATIVE):
            raise ExclusionError("tracked shared storage cannot be hidden")
        if _git(root, budget, "ls-files", "--others", "--exclude-standard", "--", RELATIVE):
            raise ExclusionError("exclusion would hide visible foreign content")


def _initialize(context: RepositoryContext, budget: Deadline) -> Path:
    _eligible(context, budget)  # refuse unsafe input before even creating an exclusion lock
    common_lock = context.common / "devkit-mcp.lock"
    _safe(context.common / "info", directory=True)
    _safe(context.common / "info/exclude", directory=False)
    with _lock(common_lock, budget, write=True, create=True):
        _eligible(context, budget)
        root = context.main / RELATIVE / "artifacts"
        existed = root.exists()
        if existed and not (root / ".lock").exists():
            raise SharedError("existing store is missing its stable lock")
        exclude = context.common / "info/exclude"
        data = exclude.read_bytes() if exclude.exists() else b""
        line = b"/.devkit/.shared/"
        if line not in data.splitlines():
            budget.check("exclusion publication")
            exclude.parent.mkdir(exist_ok=True)
            with open(exclude, "ab") as stream:
                stream.write((b"\n" if data and not data.endswith(b"\n") else b"") + line + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
        for root in _worktrees(context, budget):
            try:
                _git(root, budget, "check-ignore", "--", RELATIVE + "/")
            except GitError as exc:
                raise ExclusionError("shared storage is not ignored in every registered worktree") from exc
        for part in (context.main / ".devkit", context.main / RELATIVE, context.main / RELATIVE / "artifacts"):
            _safe(part, directory=True)
            part.mkdir(mode=0o700, exist_ok=True)
        root = context.main / RELATIVE / "artifacts"
        with _lock(root / ".lock", budget, write=True, create=not existed):
            pass
        return root


class LocalAdapter:
    adapter_id = "local"

    def __init__(self, context: RepositoryContext, *, clock: Callable[[], datetime] | None = None) -> None:
        self.context = context
        self.repository_namespace = context.repository_namespace
        self.root = context.main / RELATIVE / "artifacts"
        self.clock = clock or (lambda: datetime.now(UTC))

    @contextlib.contextmanager
    def _operation(self, *, write: bool = False, initialize: bool = False) -> Iterator[Deadline]:
        budget = deadline()
        try:
            if discover(self.context.workspace, budget) != self.context:
                raise WorkspaceError("repository identity changed")
            _safe(self.root, directory=True)
            if write:
                guard_execution()
            if initialize:
                _initialize(self.context, budget)
            if not self.root.exists():
                yield budget
                return
            if not (self.root / ".lock").exists():
                raise SharedError("existing store is missing its stable lock")
            with _lock(self.root / ".lock", budget, write=write):
                yield budget
        except PermissionError as exc:
            raise AccessError("artifact storage access denied") from exc
        except OSError as exc:
            raise SharedError(f"artifact storage IO failed: {type(exc).__name__}") from exc

    def _read(self, path: Path, budget: Deadline) -> Artifact:
        budget.check("read artifact")
        _safe(path, directory=False)
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except FileNotFoundError as exc:
            raise MissingError("artifact is missing") from exc
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise SharedError("artifact is not regular")
            raw = stream.read(MAX_BYTES + 8193)
        budget.check("validate artifact")
        try:
            if len(raw) > MAX_BYTES + 8192 or not raw.startswith(b"---\n"):
                raise ValueError("invalid envelope")
            header, content = raw[4:].split(b"\n---\n", 1)
            value = json.loads(header)
            meta = ArtifactMetadata(**value)
            if header != json.dumps(value, sort_keys=True, separators=(",", ":")).encode():
                raise ValueError("noncanonical metadata")
            request = PutRequest(meta.kind, meta.slug, meta.source_sha, meta.language, content.decode("utf-8"))
            request.validate()
            created, expires = datetime.fromisoformat(meta.created_at), datetime.fromisoformat(meta.expires_at)
            if (
                meta.repository_namespace != self.repository_namespace
                or not GENERATION.fullmatch(meta.generation_id)
                or path.name != meta.generation_id + ".md"
                or not DIGEST.fullmatch(meta.content_sha256)
                or meta.content_sha256 != request.content_sha256
                or meta.revision != request.content_sha256
                or type(meta.byte_count) is not int
                or meta.byte_count != len(content)
                or meta.content_type != "text/markdown"
                or created.utcoffset() != TTL * 0
                or expires - created != TTL
            ):
                raise ValueError("metadata mismatch")
            return Artifact(meta, request.content, str(path))
        except (ValueError, TypeError, KeyError, AttributeError, InputError) as exc:
            raise SharedError("artifact envelope metadata or body is corrupt") from exc

    def _paths(self, budget: Deadline, cursor: str | None = None) -> list[Path]:
        budget.check("enumerate artifacts")
        if not self.root.exists():
            return []
        paths = sorted(p for p in self.root.iterdir() if p.name != ".lock" and not p.name.startswith(".publish-"))
        budget.check("enumerate artifacts")
        return [p for p in paths if cursor is None or p.name > decode_cursor(cursor)]

    def put(self, request: PutRequest) -> Artifact:
        request.validate()
        with self._operation(write=True, initialize=True) as budget:
            _eligible(self.context, budget)
            now = self.clock()
            for path in self._paths(budget):
                artifact = self._read(path, budget)
                m = artifact.metadata
                if (m.kind, m.slug, m.source_sha, m.language, m.content_sha256) == (
                    request.kind,
                    request.slug,
                    request.source_sha,
                    request.language,
                    request.content_sha256,
                ) and m.live(now):
                    return artifact
            meta = ArtifactMetadata(
                self.repository_namespace,
                request.kind,
                request.slug,
                request.source_sha,
                request.language,
                request.content_sha256,
                uuid.uuid4().hex,
                "text/markdown",
                len(request.content.encode("utf-8")),
                now.isoformat(),
                (now + TTL).isoformat(),
                request.content_sha256,
            )
            path = self.root / (meta.generation_id + ".md")
            raw = (
                b"---\n"
                + json.dumps(asdict(meta), sort_keys=True, separators=(",", ":")).encode()
                + b"\n---\n"
                + request.content.encode("utf-8")
            )
            budget.check("publish artifact")
            fd, temporary = tempfile.mkstemp(prefix=".publish-", dir=self.root)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
                budget.check("commit artifact")
                os.replace(temporary, path)
            finally:
                Path(temporary).unlink(missing_ok=True)
            return Artifact(meta, request.content, str(path))

    def get(self, artifact_uri: str) -> Artifact:
        key = generation(artifact_uri, self.repository_namespace)
        with self._operation() as budget:
            artifact = self._read(self.root / (key + ".md"), budget)
            if not artifact.metadata.live(self.clock()):
                raise ExpiredError("artifact expired after seven days")
            return artifact

    def list(
        self,
        kind: str,
        slug: str,
        *,
        source_sha: str | None = None,
        language: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page:
        validate_filter(kind, slug, source_sha, language)
        validate_page(cursor, limit)
        if cursor is not None:
            decode_cursor(cursor)
        entries = self.list_live(
            kind=kind, slug=slug, source_sha=source_sha, language=language, cursor=cursor, limit=limit + 1
        )
        if len(entries) > limit:
            return Page(tuple(entries[:limit]), encode_cursor(entries[limit - 1].generation_id + ".md"))
        return Page(tuple(entries))

    def list_live(
        self,
        *,
        kind: str | None = None,
        slug: str | None = None,
        source_sha: str | None = None,
        language: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        skip_unreadable: bool = False,
    ) -> list[ArtifactMetadata]:
        """Live artifacts in generation order, matching every given field, stopping after ``limit`` matches.

        Filters are compared, not validated (``list`` validates its own). With ``skip_unreadable`` an artifact
        whose read fails (corrupt, vanished or refused) is left out instead of failing the whole listing.
        """
        with self._operation() as budget:
            entries: list[ArtifactMetadata] = []
            now = self.clock()
            for path in self._paths(budget, cursor):
                try:
                    meta = self._read(path, budget).metadata
                except (SharedError, OSError):
                    if skip_unreadable:
                        continue
                    raise
                if (
                    meta.live(now)
                    and (kind is None or meta.kind == kind)
                    and (slug is None or meta.slug == slug)
                    and (source_sha is None or meta.source_sha == source_sha)
                    and (language is None or meta.language == language)
                ):
                    entries.append(meta)
                    if limit is not None and len(entries) >= limit:
                        break
            return entries

    def sweep(self, *, apply: bool = False, cursor: str | None = None) -> SweepResult:
        validate_page(cursor, 100)
        if cursor is not None:
            decode_cursor(cursor)
        with self._operation(write=apply) as budget:
            paths = self._paths(budget, cursor)
            entries, invalid = [], []
            now = self.clock()
            for path in paths[:100]:
                try:
                    artifact = self._read(path, budget)
                except SharedError as exc:
                    if type(exc) is not SharedError:
                        raise
                    invalid.append(path.name)
                    continue
                if not artifact.metadata.live(now):
                    if apply:
                        budget.check("remove expired artifact")
                        path.unlink()
                    entries.append(artifact.metadata.artifact_uri)
            next_cursor = encode_cursor(paths[99].name) if len(paths) > 100 else None
            return SweepResult(tuple(entries), tuple(invalid), next_cursor, apply)
