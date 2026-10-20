from __future__ import annotations

import pytest
from devkit.search import ModelNotFoundError


@pytest.fixture(autouse=True)
def _no_embedding_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Playbook search runs ``auto`` as lexical unless a test installs a model, whatever this checkout has fetched."""

    def missing(name: str) -> None:
        raise ModelNotFoundError(f"no installed package provides the embedding model {name!r}")

    monkeypatch.setattr("devkit.search.index.load_embedder", missing)


@pytest.fixture(autouse=True)
def _without_optional_registration_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """Asset unit tests model dist alone; registration/runtime combinations have separate lifecycle tests."""
    from devkit.host import registrations

    entry_points = registrations.metadata.entry_points
    monkeypatch.setattr(
        registrations.metadata,
        "entry_points",
        lambda group: [] if group == registrations.GROUP else entry_points(group=group),
    )
