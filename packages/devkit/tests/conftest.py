from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_output_options_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """``DEVKIT_QUIET``/``VERBOSE``/``STRICT`` from the shell, or from ``devkit run -q``, must not change any test."""
    for name in ("DEVKIT_QUIET", "DEVKIT_VERBOSE", "DEVKIT_STRICT"):
        monkeypatch.delenv(name, raising=False)
