"""The entrypoint path contract: literal workspace-relative paths and which documents carry them.

An entrypoint is a file or directory relative to the workspace root, written with ``/``. ``./`` and a trailing
``/`` are normalized away; ``.`` names the whole workspace. An empty value, an absolute path, a ``..`` segment, a
backslash, a colon (drive), a glob character (``*?[]``), NUL or a line break is invalid. Paths compare by whole
segments and case-sensitively: ``src/a`` covers ``src/a/b.py`` but not ``src/ab``.

Capabilities and use cases carry ``entrypoints``: documents under ``docs/capabilities/`` or ``docs/usecases/``, and
under the same directories of a namespace's docs root ``docs/packages/<name>/``. Their paths stay
workspace-relative, never package-relative.
"""

from __future__ import annotations

from pathlib import Path

from devkit_core.core import UnsafePathError, resolve_within

from devkit_spec.features.documents.services.namespaces import living_path
from devkit_spec.utils.paths import ROOT
from devkit_spec.utils.paths import covers as covers
from devkit_spec.utils.paths import normalize as normalize
from devkit_spec.utils.paths import overlaps as overlaps

_LIVING_DIRECTORIES = ("docs/capabilities/", "docs/usecases/")


def entrypoint_bearing(path: str) -> bool:
    """Whether the workspace-relative ``path`` is a capability or use case file, which may declare ``entrypoints``.

    Every ``docs/packages/<name>/`` counts, registered as a namespace or not, so callers need no configuration.
    """
    living = living_path(path, namespaces=None)
    return living.startswith(_LIVING_DIRECTORIES) and living.endswith(".md")


def exists(root: Path, path: str, *, directory: bool = False) -> bool:
    """Whether the normalized ``path`` is a file or directory inside ``root``, symbolic links resolved; with
    ``directory`` only a directory counts."""
    if path == ROOT:
        return True
    try:
        resolved = resolve_within(root, path)
    except UnsafePathError:
        return False
    return resolved.is_dir() or (not directory and resolved.is_file())
