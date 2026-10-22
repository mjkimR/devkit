"""The devkit source a retained service process loaded, compared with what is installed now.

A retained ``devkit mcp serve`` process keeps the modules it imported. When the installed code changes under it (a
merge into an editable base checkout, a reinstall), those modules no longer match the files, and code read fresh
from disk (managed rules, assets) can fail against them. ``record`` captures the SHA-256 of every Python source file
of the installed devkit packages (the top-level ``devkit`` namespace and every ``devkit_*`` package on ``sys.path``)
when the service starts; ``stale`` names each loaded module of those packages whose file is now absent, unreadable,
unrecorded or different. A file the process never imported does not count, and neither does a module outside the
packages recorded at start, such as a rule or gate plugin (``devkit_rule_<sha>``) loaded from ``.devkit/managed``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import pkgutil
import sys
from collections.abc import Iterator
from pathlib import Path
from types import MappingProxyType

from devkit_mcp.features.runtime.models.loaded_code import LoadedCodeBaseline

NAMESPACE = "devkit"
PREFIX = "devkit_"


def _digest(path: str) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _locations() -> Iterator[tuple[str, tuple[Path, ...]]]:
    """Each installed devkit package (top-level name) with its import locations."""
    names = {NAMESPACE} | {module.name for module in pkgutil.iter_modules() if module.name.startswith(PREFIX)}
    for name in sorted(names):
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            continue
        if spec is None:
            continue
        if spec.submodule_search_locations is not None:
            yield name, tuple(Path(location) for location in spec.submodule_search_locations)
        elif spec.origin and spec.origin.endswith(".py"):
            yield name, (Path(spec.origin),)


def _sources(location: Path) -> Iterator[Path]:
    if location.is_file():
        yield location
        return
    for path in location.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def record() -> LoadedCodeBaseline:
    """The installed devkit packages and the SHA-256 of each of their Python source files."""
    packages: set[str] = set()
    digests: dict[str, str] = {}
    for name, locations in _locations():
        packages.add(name)
        for location in locations:
            for path in _sources(location):
                real = os.path.realpath(path)
                digest = _digest(real)
                if digest is not None:
                    digests.setdefault(real, digest)
    return LoadedCodeBaseline(frozenset(packages), MappingProxyType(digests))


def stale(baseline: LoadedCodeBaseline) -> tuple[str, ...]:
    """The loaded modules of the recorded packages whose source file no longer matches ``baseline``, sorted."""
    found: list[str] = []
    for name, module in tuple(sys.modules.items()):
        path = getattr(module, "__file__", None)
        if name.partition(".")[0] not in baseline.packages or not isinstance(path, str) or not path.endswith(".py"):
            continue
        real = os.path.realpath(path)
        recorded = baseline.digests.get(real)
        if recorded is None or _digest(real) != recorded:
            found.append(name)
    return tuple(sorted(found))
