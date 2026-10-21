"""Reusable semantic assertions for third-party adapter authors (no pytest dependency)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta

from devkit.shared.api import TTL, PutRequest, SharedArtifactAdapter
from devkit.shared.errors import ExpiredError, InputError, MissingError


def assert_conformance(adapter: SharedArtifactAdapter, advance: Callable[[timedelta], None]) -> None:
    """Exercise an empty isolated adapter with an injected clock advanced by the fixture.

    The caller owns fixture setup/teardown and authentication/infrastructure checks. This function
    performs bounded writes and expiry cleanup; never run against a production namespace.
    """
    request = PutRequest("proposal-review", "conformance", "a" * 40, "en", "# Report\n")
    first = adapter.put(request)
    assert adapter.put(request).metadata == first.metadata
    assert adapter.get(first.metadata.artifact_uri).content == request.content
    other = adapter.put(PutRequest(request.kind, request.slug, request.source_sha, request.language, "other"))
    assert other.metadata.artifact_uri != first.metadata.artifact_uri
    page = adapter.list(request.kind, request.slug, limit=1)
    assert len(page.entries) == 1 and page.cursor
    rest = adapter.list(request.kind, request.slug, limit=1, cursor=page.cursor)
    assert len(rest.entries) == 1 and rest.entries != page.entries
    try:
        adapter.put(PutRequest(request.kind, "../bad", request.source_sha, request.language, "x"))
    except InputError:
        pass
    else:
        raise AssertionError("invalid input accepted")
    advance(TTL)
    assert not adapter.list(request.kind, request.slug).entries
    try:
        adapter.get(first.metadata.artifact_uri)
    except ExpiredError:
        pass
    else:
        raise AssertionError("expiry must be inclusive")
    fresh = adapter.put(request)
    assert fresh.metadata.artifact_uri != first.metadata.artifact_uri
    assert set(adapter.sweep().entries) == {first.metadata.artifact_uri, other.metadata.artifact_uri}
    adapter.sweep(apply=True)
    try:
        adapter.get(first.metadata.artifact_uri)
    except MissingError:
        pass
    else:
        raise AssertionError("swept URI must be missing")
