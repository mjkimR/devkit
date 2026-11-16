"""The entrypoint path contract: which documents carry entrypoints, and whether an entrypoint exists.

An entrypoint is a file or directory relative to the workspace root, written with ``/``; ``devkit_docs.utils.paths``
normalizes and compares the values (``normalize``, ``covers``, ``overlaps``). ``./`` and a trailing ``/`` are
normalized away; ``.`` names the whole workspace. An empty value, an absolute path, a ``..`` segment, a backslash, a
colon (drive), a glob character (``*?[]``), NUL or a line break is invalid. Paths compare by whole segments and
case-sensitively: ``src/a`` covers ``src/a/b.py`` but not ``src/ab``.

The kinds whose table row allows ``entrypoints`` carry them: capability and use case documents under
``docs/capabilities/`` or ``docs/usecases/``, and design bundle anchors ``docs/designs/<area>/DESIGN-<slug>/design.md``
(the kind's ``area-bundle`` layout), and the same paths under a namespace's docs root ``docs/packages/<name>/``.
Their paths stay workspace-relative, never package-relative.
"""

from __future__ import annotations

from pathlib import Path

from devkit_core.core import UnsafePathError, resolve_within

from devkit_docs.features.documents import definitions
from devkit_docs.features.documents.models.ids import is_word_led_slug
from devkit_docs.features.documents.services.namespaces import living_path
from devkit_docs.utils.paths import ROOT


def entrypoint_bearing(path: str) -> bool:
    """Whether the workspace-relative ``path`` is a document that may declare ``entrypoints``: a Markdown file under
    the directory of a kind that allows them, or, for an ``area-bundle`` kind, its bundle anchor
    ``<directory>/<area>/<PREFIX>-<slug>/<layout_anchor>``.

    Every ``docs/packages/<name>/`` counts, registered as a namespace or not, so callers need no configuration.
    """
    living = living_path(path, namespaces=None)
    for row in definitions():
        if not row.entrypoints or not living.startswith(f"docs/{row.directory}/"):
            continue
        if not row.bundled:
            return living.endswith(".md")
        parts = living.split("/")
        return (
            len(parts) == 5
            and parts[4] == row.layout_anchor
            and parts[3].startswith(f"{row.prefix}-")
            and is_word_led_slug(parts[3].removeprefix(f"{row.prefix}-"))
        )
    return False


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
