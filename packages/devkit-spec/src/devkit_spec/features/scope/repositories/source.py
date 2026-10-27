"""Bounded declaration readers using a single filesystem or immutable Git tree."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Protocol

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import Granularity
from devkit_spec.features.scope.repositories.collection_git import InputLimitError, git

DOCUMENT_BYTES = 1024 * 1024
TOTAL_DOCUMENT_BYTES = 16 * DOCUMENT_BYTES


class Reader(Protocol):
    def read(self, path: str) -> str: ...
    def kind(self, path: str) -> Granularity: ...


class ReaderPath:
    def __init__(self, reader: Reader, relative: str = "") -> None:
        self.reader, self.relative = reader, relative

    @property
    def name(self) -> str:
        return PurePosixPath(self.relative).name

    def __truediv__(self, value: str) -> ReaderPath:
        return ReaderPath(self.reader, str(PurePosixPath(self.relative) / value))

    def is_file(self) -> bool:
        return self.reader.kind(self.relative) is Granularity.FILE

    def is_dir(self) -> bool:
        return self.reader.kind(self.relative) is Granularity.DIR

    def read_text(self, *, encoding: str = "utf-8") -> str:
        return self.reader.read(self.relative)


class ReadBudget:
    def __init__(self) -> None:
        self.remaining = TOTAL_DOCUMENT_BYTES

    def consume(self, size: int) -> None:
        self.remaining -= size
        if size > DOCUMENT_BYTES or self.remaining < 0:
            raise InputLimitError("Declaration input limit exceeded")


class TreeReader:
    def __init__(self, root: Path, sha: str, deadline: Deadline, budget: ReadBudget) -> None:
        self.root, self.sha, self.deadline, self.budget = root, sha, deadline, budget
        self.prefix = git(root, "rev-parse", "--show-prefix", deadline=deadline).decode().removesuffix("\n")
        self.entries: dict[str, str] = {"": "tree", ".": "tree"}
        for entry in git(root, "ls-tree", "-rz", "--full-tree", sha, deadline=deadline).split(b"\0"):
            deadline.check("scope tree inventory")
            if not entry:
                continue
            meta, raw = entry.split(b"\t", 1)
            mode, kind, _ = meta.decode().split()
            path = raw.decode("utf-8", errors="surrogateescape")
            if self.prefix and not path.startswith(self.prefix):
                continue
            path = path.removeprefix(self.prefix)
            self.entries[path] = "blob" if kind == "blob" and mode != "120000" else "unsupported"
            for parent in PurePosixPath(path).parents:
                self.entries.setdefault(str(parent), "tree")

    def kind(self, path: str) -> Granularity:
        self.deadline.check("scope tree kind")
        return {"blob": Granularity.FILE, "tree": Granularity.DIR}.get(self.entries.get(path, ""), Granularity.UNKNOWN)

    def read(self, path: str) -> str:
        self.deadline.check("scope tree read")
        if self.kind(path) is not Granularity.FILE:
            raise OSError("Declaration is absent or not a regular blob")
        data = git(self.root, "show", f"{self.sha}:{self.prefix}{path}", deadline=self.deadline, limit=DOCUMENT_BYTES)
        self.budget.consume(len(data))
        return data.decode("utf-8")


class FilesystemReader:
    def __init__(self, root: Path, deadline: Deadline, budget: ReadBudget) -> None:
        self.root, self.deadline, self.budget = root.resolve(), deadline, budget
        self.fingerprints: dict[str, str] = {}

    def _path(self, path: str) -> Path:
        self.deadline.check("scope filesystem read")
        try:
            target = (self.root / path).resolve()
        except RuntimeError as exc:
            raise OSError("Declaration symlink cannot be resolved") from exc
        if not target.is_relative_to(self.root):
            raise OSError("Declaration path escapes the worktree")
        return target

    def kind(self, path: str) -> Granularity:
        target = self._path(path)
        try:
            mode = target.stat().st_mode
        except FileNotFoundError:
            return Granularity.UNKNOWN
        if stat.S_ISREG(mode):
            return Granularity.FILE
        if stat.S_ISDIR(mode):
            return Granularity.DIR
        raise OSError("Scope input is not a regular file or directory")

    def _bytes(self, path: str) -> bytes:
        fd = os.open(self._path(path), os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise OSError("Scope declaration is not a regular file")
            data = stream.read(DOCUMENT_BYTES + 1)
        if len(data) > DOCUMENT_BYTES:
            raise InputLimitError("Declaration document is too large")
        return data

    def read(self, path: str) -> str:
        data = self._bytes(path)
        self.budget.consume(len(data))
        self.fingerprints[path] = hashlib.sha256(data).hexdigest()
        return data.decode("utf-8")

    def unchanged(self) -> bool:
        return all(
            hashlib.sha256(self._bytes(path)).hexdigest() == fingerprint
            for path, fingerprint in self.fingerprints.items()
        )
