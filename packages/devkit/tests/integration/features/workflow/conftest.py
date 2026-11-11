from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from devkit_agt.features.workflow.models.envelope import Envelope, EnvelopeFlags, Envelopes
from devkit_agt.features.workflow.services.envelope import compose_envelope
from testsupport.workflow import WORKFLOW


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A workspace with one valid definition under the default definitions_dir."""
    defs = tmp_path / ".devkit" / "workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW, encoding="utf-8")
    return tmp_path


Compose = Callable[..., Envelope]


@pytest.fixture
def compose() -> Compose:
    """``compose_envelope`` for a unit outside any workflow: ``compose(unit_dir, envelopes, kind, **flags)``, the
    ``flags`` as ``EnvelopeFlags`` fields; ``loaded`` defaults to ``envelopes``."""

    def run(
        unit_dir: Path, envelopes: Envelopes, kind: str, *, loaded: Envelopes | None = None, **flags: Any
    ) -> Envelope:
        return compose_envelope(
            unit_dir=unit_dir,
            envelopes=envelopes,
            loaded=envelopes if loaded is None else loaded,
            kind=kind,
            flags=EnvelopeFlags(**flags),
            workflow="",
            segment=None,
            unit="",
        )

    return run
