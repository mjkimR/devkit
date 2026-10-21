"""Adapter selection from explicit workspace configuration and installed factories."""

from __future__ import annotations

import inspect
import os
from importlib import metadata
from pathlib import Path
from typing import Any

from devkit.core.local_config import read_effective_config
from devkit.shared.api import Artifact, ArtifactMetadata, Page, PutRequest, SharedArtifactAdapter, SweepResult
from devkit.shared.errors import AdapterError, InputError
from devkit.shared.local import LocalAdapter, discover

GROUP = "devkit.shared.adapters"


def adapter(workspace: Path) -> SharedArtifactAdapter:
    configured = read_effective_config(workspace).values["shared"]["adapter"]
    selected = os.environ.get("DEVKIT_SHARED_ADAPTER", configured)
    context = discover(workspace)
    entries = list(metadata.entry_points(group=GROUP))
    names = [entry.name for entry in entries]
    if "local" in names or len(set(names)) != len(names):
        raise AdapterError("duplicate or reserved adapter registration")
    if selected == "local":
        return LocalAdapter(context)
    matches = [entry for entry in entries if entry.name == selected]
    if len(matches) != 1:
        raise AdapterError("selected adapter is not installed")
    try:
        instance = matches[0].load()(context)
        if (
            not isinstance(instance, SharedArtifactAdapter)
            or instance.adapter_id != selected
            or not isinstance(instance.repository_namespace, str)
            or not instance.repository_namespace
            or any(not callable(getattr(instance, name, None)) for name in ("put", "get", "list", "sweep"))
        ):
            raise TypeError("invalid adapter implementation")
        shapes = {
            "put": ((PutRequest("proposal-review", "validation", "a" * 40, "en", ""),), {}),
            "get": (("shared://namespace/generation",), {}),
            "list": (
                ("proposal-review", "validation"),
                {"source_sha": None, "language": None, "cursor": None, "limit": 100},
            ),
            "sweep": ((), {"apply": False, "cursor": None}),
        }
        for name, (args, kwargs) in shapes.items():
            inspect.signature(getattr(instance, name)).bind(*args, **kwargs)
        return CheckedAdapter(instance)
    except Exception as exc:
        raise AdapterError(f"adapter factory failed: {type(exc).__name__}") from exc


class CheckedAdapter:
    """Enforce public input/result shapes at the installed adapter boundary."""

    def __init__(self, delegate: SharedArtifactAdapter) -> None:
        self.delegate = delegate
        self.adapter_id = delegate.adapter_id
        self.repository_namespace = delegate.repository_namespace

    def _call(self, name: str, expected: type, *args, **kwargs) -> Any:
        try:
            value = getattr(self.delegate, name)(*args, **kwargs)
        except (TypeError, AttributeError) as exc:
            raise AdapterError("adapter violated its invocation contract") from exc
        try:
            if not isinstance(value, expected):
                raise TypeError("invalid result type")
            if isinstance(value, Artifact):
                if not isinstance(value.metadata, ArtifactMetadata) or not isinstance(value.content, str):
                    raise TypeError("invalid artifact result")
                PutRequest(
                    value.metadata.kind,
                    value.metadata.slug,
                    value.metadata.source_sha,
                    value.metadata.language,
                    value.content,
                ).validate()
                if value.metadata.repository_namespace != self.repository_namespace:
                    raise TypeError("invalid result namespace")
            if isinstance(value, Page) and (
                not isinstance(value.entries, tuple)
                or any(not isinstance(entry, ArtifactMetadata) for entry in value.entries)
            ):
                raise TypeError("invalid page result")
            return value
        except (TypeError, AttributeError, InputError) as exc:
            raise AdapterError("adapter returned an invalid result or violated its invocation contract") from exc

    def put(self, request: PutRequest) -> Artifact:
        request.validate()
        return self._call("put", Artifact, request)

    def get(self, artifact_uri: str) -> Artifact:
        from devkit.shared.api import generation

        generation(artifact_uri, self.repository_namespace)
        return self._call("get", Artifact, artifact_uri)

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
        from devkit.shared.api import validate_filter, validate_page

        validate_filter(kind, slug, source_sha, language)
        validate_page(cursor, limit)
        return self._call(
            "list", Page, kind, slug, source_sha=source_sha, language=language, cursor=cursor, limit=limit
        )

    def sweep(self, *, apply: bool = False, cursor: str | None = None) -> SweepResult:
        from devkit.shared.api import validate_page

        validate_page(cursor, 100)
        return self._call("sweep", SweepResult, apply=apply, cursor=cursor)
