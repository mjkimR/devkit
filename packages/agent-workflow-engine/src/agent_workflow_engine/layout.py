"""Work unit layout: where units live and how their directories are named.

The engine needs two operations from a layout, creating a unit path and
discovering existing units. ``TemplateLayout`` implements both from one
``str.format`` template; a plugin layout fits behind the same protocol.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date as date_type
from pathlib import Path, PurePosixPath
from string import Formatter
from typing import Protocol

ALLOWED_FIELDS = {"slug", "date"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Layout(Protocol):
    anchor: str

    def new_unit(self, slug: str, when: date_type) -> PurePosixPath:
        """Workspace-relative directory for a new unit."""
        ...

    def discover(self, workspace_root: Path) -> list[PurePosixPath]:
        """Workspace-relative directories of existing units, sorted."""
        ...


def validate_template(template: str) -> list[tuple[str, str]]:
    """Return the template's (field, spec) pairs or raise ``ValueError``."""
    if not template.strip():
        raise ValueError("template is empty")
    if template.startswith("/") or "\\" in template or ".." in PurePosixPath(template).parts:
        raise ValueError("template must be a relative path without '..'")
    fields: list[tuple[str, str]] = []
    try:
        parsed = list(Formatter().parse(template))
    except ValueError as exc:
        raise ValueError(f"invalid format syntax: {exc}") from exc
    for _, name, spec, conversion in parsed:
        if name is None:
            continue
        if name not in ALLOWED_FIELDS:
            raise ValueError(f"unknown placeholder {{{name}}}; allowed: {{slug}}, {{date}}")
        if conversion:
            raise ValueError(f"conversion !{conversion} is not supported")
        if name == "slug" and spec:
            raise ValueError("{slug} takes no format spec")
        fields.append((name, spec or ""))
    if not any(name == "slug" for name, _ in fields):
        raise ValueError("template must contain {slug}")
    return fields


def validate_slug(slug: str) -> str:
    if not SLUG.match(slug):
        raise ValueError(f"slug {slug!r} must match [a-z0-9][a-z0-9-]*")
    return slug


@dataclass(frozen=True)
class TemplateLayout:
    work_dir: str
    unit_path: str
    anchor: str

    def __post_init__(self) -> None:
        validate_template(self.unit_path)

    def new_unit(self, slug: str, when: date_type) -> PurePosixPath:
        validate_slug(slug)
        rendered = self.unit_path.format(slug=slug, date=when)
        rel = PurePosixPath(self.work_dir) / rendered
        if ".." in rel.parts:
            raise ValueError("rendered unit path escapes the work directory")
        return rel

    def discovery_glob(self) -> str:
        """The template with every placeholder replaced by ``*``."""
        out: list[str] = []
        for literal, name, _, _ in Formatter().parse(self.unit_path):
            out.append(literal)
            if name is not None:
                out.append("*")
        pattern = "".join(out)
        # Collapse runs of stars produced by adjacent placeholders.
        return re.sub(r"\*{2,}", "*", pattern)

    def discover(self, workspace_root: Path) -> list[PurePosixPath]:
        base = workspace_root / self.work_dir
        if not base.is_dir():
            return []
        found: list[PurePosixPath] = []
        for candidate in base.glob(self.discovery_glob()):
            if candidate.is_dir() and (candidate / self.anchor).is_file():
                found.append(PurePosixPath(candidate.relative_to(workspace_root).as_posix()))
        return sorted(found)
