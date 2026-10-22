"""The installed devkit source a retained service recorded when it started."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class LoadedCodeBaseline:
    """The installed devkit packages (top-level import names) and the SHA-256 of each source file, by real path."""

    packages: frozenset[str]
    digests: Mapping[str, str]
