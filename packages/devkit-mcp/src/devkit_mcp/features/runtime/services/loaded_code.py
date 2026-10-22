"""The devkit source a retained service process loaded, compared with what is installed now.

A retained ``devkit mcp serve`` process keeps the modules it imported. When the installed code changes under it (a
merge into an editable base checkout, a reinstall), those modules no longer match the files, and code read fresh
from disk (managed rules, assets) can fail against them. ``record`` captures the SHA-256 of every Python source file
of the installed devkit packages (the top-level ``devkit`` namespace and every ``devkit_*`` package on ``sys.path``)
when the service starts; ``stale`` names each loaded module of those packages whose file is now absent, unreadable,
unrecorded or different. A file the process never imported does not count.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import pkgutil
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from types import MappingProxyType

NAMESPACE = "devkit"
PREFIX = "devkit_"


def _devkit(name: str) -> bool:
    top = name.partition(".")[0]
    return top == NAMESPACE or top.startswith(PREFIX)


def _digest(path: str) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _locations() -> Iterator[Path]:
    names = {NAMESPACE} | {module.name for module in pkgutil.iter_modules() if module.name.startswith(PREFIX)}
    for name in sorted(names):
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            continue
        if spec is None:
            continue
        if spec.submodule_search_locations is not None:
            yield from (Path(location) for location in spec.submodule_search_locations)
        elif spec.origin and spec.origin.endswith(".py"):
            yield Path(spec.origin)


def _sources(location: Path) -> Iterator[Path]:
    if location.is_file():
        yield location
        return
    for path in location.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def record() -> Mapping[str, str]:
    """The SHA-256 of every installed devkit Python source file, keyed by its real path."""
    baseline: dict[str, str] = {}
    for location in _locations():
        for path in _sources(location):
            real = os.path.realpath(path)
            digest = _digest(real)
            if digest is not None:
                baseline.setdefault(real, digest)
    return MappingProxyType(baseline)


def stale(baseline: Mapping[str, str]) -> tuple[str, ...]:
    """The loaded devkit modules whose source file no longer matches ``baseline``, sorted by name."""
    found: list[str] = []
    for name, module in tuple(sys.modules.items()):
        path = getattr(module, "__file__", None)
        if not _devkit(name) or not isinstance(path, str) or not path.endswith(".py"):
            continue
        real = os.path.realpath(path)
        recorded = baseline.get(real)
        if recorded is None or _digest(real) != recorded:
            found.append(name)
    return tuple(sorted(found))
