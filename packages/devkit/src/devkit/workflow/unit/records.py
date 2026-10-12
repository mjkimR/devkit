"""Helpers shared by the numbered record files of a unit: ``decisions/NN-*.yaml`` and ``envelopes/<kind>-NN.yaml``."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any


def as_text(value: Any) -> str:
    """``value`` as a string; ``None`` is ``""``."""
    return "" if value is None else str(value)


def write_numbered(directory: Path, seq: int, name_for: Callable[[int], str], body: str) -> tuple[Path, int]:
    """Write ``body`` to ``directory / name_for(seq)``, moving to the next sequence while that file exists.

    Each attempt creates the file exclusively, so concurrent writers never
    overwrite each other. Returns the path written and its sequence number.
    """
    directory.mkdir(parents=True, exist_ok=True)
    while True:
        path = directory / name_for(seq)
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(body)
        except FileExistsError:
            seq += 1
            continue
        return path, seq
