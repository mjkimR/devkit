"""devkit-docs' project settings: the ``[tool.docs]`` table of ``.devkit/config.toml``.

devkit passes ``[tool.<name>]`` tables through unread, so devkit-docs owns this one.

```toml
[[tool.docs.namespaces]]   # a package of a monorepo with its own Living Spec under docs/packages/<name>/
name = "api"
path = "services/api"
```

``template`` is the ``devkit.config_template`` extension: ``devkit config template`` writes this table into
``.devkit/config.toml`` as comments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from devkit_core.core import is_safe_relpath
from devkit_dist.features.project.models.templates import TemplateKey, TemplateTable
from devkit_dist.features.project.repositories.project import read_project_config

from devkit_docs.base.errors import DocsConfigError
from devkit_docs.features.documents.models.namespace import GLOBAL, NAMESPACE_NAME, PACKAGES_DIR, Namespace

TABLE = "docs"


@dataclass(frozen=True)
class DocsConfig:
    namespaces: tuple[Namespace, ...] = field(default=())


def template() -> list[TemplateTable]:
    """``[tool.docs]`` for devkit's commented config template."""
    return [
        TemplateTable(
            (
                TemplateKey(
                    "name",
                    help=f"lowercase words joined by -, not {GLOBAL!r}; its Living Spec is {PACKAGES_DIR}/<name>/",
                    kind="string",
                    example="api",
                ),
                TemplateKey(
                    "path",
                    help="the package's workspace-relative source directory",
                    kind="string",
                    example="services/api",
                ),
            ),
            path=("namespaces",),
            help="A package of a monorepo with its own Living Spec; one table per package.",
            array=True,
        ),
    ]


def read_docs_config(root: Path) -> DocsConfig:
    """The ``[tool.docs]`` table of the project at ``root``; defaults when absent."""
    tool = read_project_config(root).get("tool", {})
    table = tool.get(TABLE, {}) if isinstance(tool, dict) else None
    if not isinstance(table, dict):
        raise DocsConfigError("config tool.docs: expected a table")
    unknown = sorted(set(table) - {"namespaces"})
    if unknown:
        raise DocsConfigError(f"config tool.docs: unknown keys: {', '.join(unknown)}")
    return DocsConfig(namespaces=_namespaces(table.get("namespaces", [])))


def _namespaces(value: object) -> tuple[Namespace, ...]:
    if not isinstance(value, list):
        raise DocsConfigError("config tool.docs.namespaces: expected an array of tables")
    found: list[Namespace] = []
    for position, entry in enumerate(value):
        where = f"config tool.docs.namespaces[{position}]"
        if not isinstance(entry, dict) or set(entry) != {"name", "path"}:
            raise DocsConfigError(f"{where}: expected exactly the keys name and path")
        name, path = entry["name"], entry["path"]
        if not isinstance(name, str) or not NAMESPACE_NAME.match(name) or name == GLOBAL:
            raise DocsConfigError(f"{where}: name must be lowercase words joined by - and not {GLOBAL!r}, got {name!r}")
        if not isinstance(path, str) or not is_safe_relpath(path):
            raise DocsConfigError(f"{where}: path must be a workspace-relative directory, got {path!r}")
        if not is_safe_relpath(path, canonical=True):
            canonical = PurePosixPath(path).as_posix()
            raise DocsConfigError(
                f"{where}: path must be in canonical form (no ./, //, or trailing /), got {path!r}",
                fix=f"Write path = {canonical!r} in [[tool.docs.namespaces]] of .devkit/config.toml",
            )
        if any(other.name == name for other in found) or any(other.path == path for other in found):
            raise DocsConfigError(f"{where}: name {name!r} or path {path!r} is already registered")
        found.append(Namespace(name, path))
    return tuple(found)
