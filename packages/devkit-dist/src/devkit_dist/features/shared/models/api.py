"""Public immutable artifact and adapter contracts; no transport dependencies."""

from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol, runtime_checkable

from devkit_dist.features.shared.models.errors import InputError

MAX_BYTES = 1024 * 1024
TTL = timedelta(days=7)
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
GENERATION = re.compile(r"[0-9a-f]{32}\Z")


@dataclass(frozen=True)
class RepositoryContext:
    workspace: Path
    main: Path
    common: Path
    repository_namespace: str


@dataclass(frozen=True)
class PutRequest:
    kind: str
    slug: str
    source_sha: str
    language: str
    content: str

    def validate(self) -> None:
        if self.source_sha is None or self.language is None:
            raise InputError("put requires a commit SHA and language")
        validate_filter(self.kind, self.slug, self.source_sha, self.language)
        try:
            valid = isinstance(self.content, str) and len(self.content.encode("utf-8")) <= MAX_BYTES
        except UnicodeError:
            valid = False
        if not valid:
            raise InputError("content must be UTF-8 Markdown of at most 1 MiB")

    @property
    def content_sha256(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def validate_filter(kind: str, slug: str, source_sha: str | None, language: str | None) -> None:
    if (
        kind != "proposal-review"
        or not isinstance(slug, str)
        or not SLUG.fullmatch(slug)
        or len(slug) > 120
        or (source_sha is not None and (not isinstance(source_sha, str) or not SHA.fullmatch(source_sha)))
        or (language is not None and language not in ("ko", "en"))
    ):
        raise InputError("expected proposal-review, lowercase kebab slug, full lowercase commit SHA and ko/en language")


@dataclass(frozen=True)
class ArtifactMetadata:
    repository_namespace: str
    kind: str
    slug: str
    source_sha: str
    language: str
    content_sha256: str
    generation_id: str
    content_type: str
    byte_count: int
    created_at: str
    expires_at: str
    revision: str

    @property
    def artifact_uri(self) -> str:
        return f"shared://{self.repository_namespace}/{self.generation_id}"

    def live(self, now: datetime) -> bool:
        return now < datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> dict:
        return {**asdict(self), "artifact_uri": self.artifact_uri}


@dataclass(frozen=True)
class Artifact:
    metadata: ArtifactMetadata
    content: str
    local_path: str | None = None

    def to_dict(self) -> dict:
        value = {
            "artifact_uri": self.metadata.artifact_uri,
            "metadata": self.metadata.to_dict(),
            "content": self.content,
        }
        if self.local_path is not None:
            value.update(local_path=self.local_path, file_uri=Path(self.local_path).as_uri())
        return value


@dataclass(frozen=True)
class Page:
    entries: tuple[ArtifactMetadata, ...]
    cursor: str | None = None

    def to_dict(self) -> dict:
        return {"entries": [entry.to_dict() for entry in self.entries], "cursor": self.cursor}


@dataclass(frozen=True)
class SweepResult:
    entries: tuple[str, ...]
    invalid: tuple[str, ...]
    cursor: str | None
    applied: bool

    def to_dict(self) -> dict:
        return asdict(self)


@runtime_checkable
class SharedArtifactAdapter(Protocol):
    adapter_id: str
    repository_namespace: str

    def put(self, request: PutRequest) -> Artifact: ...
    def get(self, artifact_uri: str) -> Artifact: ...
    def list(
        self,
        kind: str,
        slug: str,
        *,
        source_sha: str | None = None,
        language: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page: ...
    def sweep(self, *, apply: bool = False, cursor: str | None = None) -> SweepResult: ...


def encode_cursor(name: str) -> str:
    return base64.urlsafe_b64encode(name.encode("utf-8", errors="surrogateescape")).decode("ascii")


def decode_cursor(cursor: str) -> str:
    try:
        value = base64.b64decode(cursor, altchars=b"-_", validate=True).decode("utf-8", errors="surrogateescape")
        if not value or len(value) > 255 or "/" in value or value in (".", "..") or "\x00" in value:
            raise ValueError("unsafe cursor")
        return value
    except (ValueError, UnicodeError) as exc:
        raise InputError("cursor must be a returned opaque continuation token") from exc


def validate_page(cursor: str | None, limit: int) -> None:
    if type(limit) is not int or not 1 <= limit <= 100:
        raise InputError("limit must be 1..100")
    if cursor is not None and not isinstance(cursor, str):
        raise InputError("cursor must be a string")


def generation(artifact_uri: str, namespace: str) -> str:
    prefix = f"shared://{namespace}/"
    if not isinstance(artifact_uri, str) or not artifact_uri.startswith(prefix):
        raise InputError("artifact URI belongs to another namespace or is malformed")
    value = artifact_uri[len(prefix) :]
    if not GENERATION.fullmatch(value):
        raise InputError("artifact URI has an invalid generation")
    return value
