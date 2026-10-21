"""Exact immutable local reports, rendered as escaped Markdown without active content."""

from __future__ import annotations

import os
from html import escape
from http import HTTPStatus

from devkit.advisory import AdvisoryError
from devkit.core.local_config import read_effective_config
from devkit.shared.api import GENERATION
from devkit.shared.errors import ExpiredError, MissingError
from devkit.shared.local import LocalAdapter, discover

from devkit_viewer.errors import ReadError
from devkit_viewer.repositories import Repository

UNAVAILABLE_CODES = {MissingError.code, ExpiredError.code}


def report_page(repo: Repository, generation_id: str) -> bytes:
    """Read only the requested generation; never discover plugins, enumerate or initialize storage."""
    if not GENERATION.fullmatch(generation_id):
        raise ReadError(HTTPStatus.BAD_REQUEST, "VIEWER_REVIEW_INVALID", "invalid report generation")
    try:
        configured = read_effective_config(repo.root).values["shared"]["adapter"]
        if os.environ.get("DEVKIT_SHARED_ADAPTER", configured) != "local":
            raise ReadError(
                HTTPStatus.NOT_FOUND, "VIEWER_REVIEW_UNAVAILABLE", "report viewing requires the local adapter"
            )
        selected = LocalAdapter(discover(repo.root))
        # LocalAdapter.get validates namespace, kind, generation, digest, timestamps and expiry.
        artifact = selected.get(f"shared://{selected.repository_namespace}/{generation_id}")
    except MissingError as exc:
        raise ReadError(HTTPStatus.NOT_FOUND, exc.code, "report not found") from exc
    except ExpiredError as exc:
        raise ReadError(HTTPStatus.GONE, exc.code, "report expired; request a fresh report") from exc
    except AdvisoryError as exc:
        raise ReadError(HTTPStatus.BAD_REQUEST, exc.code, "report or local shared configuration is invalid") from exc
    meta = artifact.metadata
    page = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Proposal review</title></head><body><main><h1>Proposal review</h1>"
        f"<dl><dt>Repository</dt><dd>{escape(repo.id)}</dd>"
        f"<dt>Proposal</dt><dd>{escape(meta.slug)}</dd>"
        f"<dt>Source SHA</dt><dd>{escape(meta.source_sha)}</dd>"
        f"<dt>Language</dt><dd>{escape(meta.language)}</dd>"
        f"<dt>Expires</dt><dd>{escape(meta.expires_at)}</dd></dl>"
        "<p>This immutable report does not assert that the branch remains current.</p>"
        f"<pre>{escape(artifact.content)}</pre></main></body></html>"
    )
    return page.encode("utf-8")


def unavailable_page(error: ReadError) -> bytes:
    """Stable no-write unavailable page for an exact missing or expired generation."""
    return (
        '<!doctype html><html><head><meta charset="utf-8"><title>Proposal review unavailable</title></head>'
        "<body><main><h1>Proposal review unavailable</h1>"
        f"<p>{escape(error.code)}: {escape(error.message)}</p>"
        "<p>Ask the Host to regenerate the proposal review report for the current committed source "
        "and provide its new exact report link. This viewer never refreshes or publishes reports.</p>"
        "</main></body></html>"
    ).encode()
