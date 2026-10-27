"""The repository's local shared space, read only through devkit-dist's ``LocalAdapter``."""

from __future__ import annotations

import os
from http import HTTPStatus

from devkit.advisory import AdvisoryError
from devkit_dist.features.project.repositories.local_config import read_effective_config
from devkit_dist.features.shared.models.api import Artifact
from devkit_dist.features.shared.models.errors import ExpiredError, MissingError
from devkit_dist.features.shared.repositories.local import LocalAdapter, discover

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository


def local_adapter(repo: Repository, code: str, message: str) -> LocalAdapter:
    """The local adapter, or ``ReadError(404, code, message)`` before any storage discovery when another is selected."""
    configured = read_effective_config(repo.root).values["shared"]["adapter"]
    if os.environ.get("DEVKIT_SHARED_ADAPTER", configured) != "local":
        raise ReadError(HTTPStatus.NOT_FOUND, code, message)
    return LocalAdapter(discover(repo.root))


def get_artifact(
    repo: Repository,
    generation_id: str,
    *,
    unavailable: tuple[str, str],
    not_found: str,
    expired: str,
    invalid: str | None = None,
) -> Artifact:
    """One exact live generation, with each shared failure mapped to a request error.

    ``unavailable`` is the code and message when the local adapter is not selected; ``invalid`` replaces the
    advisory's own message for any other shared or configuration failure.
    """
    try:
        selected = local_adapter(repo, *unavailable)
        # LocalAdapter.get validates namespace, kind, generation, digest, timestamps and expiry.
        return selected.get(f"shared://{selected.repository_namespace}/{generation_id}")
    except MissingError as exc:
        raise ReadError(HTTPStatus.NOT_FOUND, exc.code, not_found) from exc
    except ExpiredError as exc:
        raise ReadError(HTTPStatus.GONE, exc.code, expired) from exc
    except AdvisoryError as exc:
        raise ReadError(HTTPStatus.BAD_REQUEST, exc.code, invalid or str(exc)) from exc
