"""The ``devkit.context_documents`` provider: a namespace's mirror of a bundle's context document directory.

``devkit get-context <bundle>`` lists the Markdown files of the directory a bundle's manifest declares (the ``docs``
bundle declares ``docs/steering``). devkit-dist reads no ``[tool.docs]`` table, so it asks the installed providers
which further directories to list for the working directory, and which to mention
(``ADR-namespace-steering-directories``). This provider answers for a ``docs/``-rooted declared directory:

- to list, the mirror ``docs/packages/<name>/<rest>`` of the namespace the working directory selects
  (``namespaces.detect``: its docs root, else the deepest source path containing it);
- to mention, the mirrors of the other registered namespaces (every one when the working directory selects none).

Nothing is returned without registered namespaces or for a directory outside ``docs/``. devkit-dist drops the
mentioned directories that do not exist and lists each returned directory with its own read rules. A malformed
registry raises ``DocsConfigError``, which devkit-dist reports as a ``CONTEXT_DOCUMENTS_EXTENSION_FAILED`` warning.
"""

from __future__ import annotations

from pathlib import Path

from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.repositories.config import read_docs_config
from devkit_docs.features.documents.services.namespaces import detect

DOCS = "docs"


def mirror(namespace: Namespace, directory: str) -> str | None:
    """``docs/packages/<name>/<rest>`` for a ``docs/<rest>`` ``directory``; ``None`` for another directory."""
    if directory == DOCS:
        return namespace.docs
    if not directory.startswith(f"{DOCS}/"):
        return None
    return f"{namespace.docs}/{directory.removeprefix(f'{DOCS}/')}"


def provide(root: Path, working: Path, directory: str) -> tuple[list[str], list[str]]:
    """The namespace directories to list and to mention for ``directory`` when an agent works in ``working``."""
    namespaces = read_docs_config(root).namespaces
    mirrors = [(namespace.name, mirrored) for namespace in namespaces if (mirrored := mirror(namespace, directory))]
    if not mirrors:
        return [], []
    selected = detect(namespaces, root, working)
    listed = [mirrored for name, mirrored in mirrors if name == selected]
    mentioned = [mirrored for name, mirrored in mirrors if name != selected]
    return listed, mentioned
