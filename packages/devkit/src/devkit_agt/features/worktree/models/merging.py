"""The contract through which a caller settles the conflicts of a merge built outside any checkout."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

SIDES = ("ours", "theirs")  # "ours" keeps the target's version of a path, "theirs" the source's


class ConflictSettler(Protocol):
    """Decides, for every conflicted path of one merge, which side's version the result keeps.

    ``build_result`` calls it once with the conflicted paths (sorted, ``/``-separated, relative to the repository's top
    level) and keeps each path at the returned side, ``"ours"`` (the target) or ``"theirs"`` (the source), or leaves it
    out of the result when that side deleted it. A settler that cannot settle every path raises ``MergeConflictError``
    with one detail per path it cannot settle; a path missing from the returned mapping refuses the same way.
    """

    def __call__(self, paths: tuple[str, ...], /) -> Mapping[str, str]: ...
