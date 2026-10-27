"""Work unit layout: where units live and how their directories are named.

``TemplateLayout`` computes new unit paths and discovery patterns from one
``str.format`` template; repositories discover existing units on disk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date as date_type
from pathlib import PurePosixPath
from string import Formatter

from devkit_core.base.errors import UnsafePathError
from devkit_core.core.paths import normalize_relpath

from devkit_agt.features.workflow.models.errors import LayoutError, SlugError

ALLOWED_FIELDS = {"slug", "date"}
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
LAYOUT_KEYS = ("work_dir", "unit_path", "anchor")


def validate_template(template: str) -> list[tuple[str, str]]:
    """Return the template's (field, spec) pairs or raise ``LayoutError``."""
    if not template.strip():
        raise LayoutError("template is empty")
    if template.startswith("/") or "\\" in template or ".." in PurePosixPath(template).parts:
        raise LayoutError("template must be a relative path without '..'")
    fields: list[tuple[str, str]] = []
    try:
        parsed = list(Formatter().parse(template))
    except ValueError as exc:  # str.format syntax
        raise LayoutError(f"invalid format syntax: {exc}") from exc
    for _, name, spec, conversion in parsed:
        if name is None:
            continue
        if name not in ALLOWED_FIELDS:
            raise LayoutError(f"unknown placeholder {{{name}}}; allowed: {{slug}}, {{date}}")
        if conversion:
            raise LayoutError(f"conversion !{conversion} is not supported")
        if name == "slug" and spec:
            raise LayoutError("{slug} takes no format spec")
        fields.append((name, spec or ""))
    if not any(name == "slug" for name, _ in fields):
        raise LayoutError("template must contain {slug}")
    # A {date} spec renders verbatim, so a spec such as "/abs/%Y" or "%Y/.." escapes
    # the work directory; check a sample rendering and the discovery pattern too.
    try:
        rendered = template.format(slug="x", date=_SAMPLE_DATE)
    except (ValueError, KeyError, IndexError) as exc:
        raise LayoutError(f"invalid format syntax: {exc}") from exc
    _relative(rendered)
    _relative(_glob(template))
    return fields


_SAMPLE_DATE = date_type(2000, 1, 1)


def _relative(value: str) -> PurePosixPath:
    """``value`` as a normalized relative path; ``LayoutError`` when it is absolute or contains ``..``."""
    try:
        return normalize_relpath(value)
    except UnsafePathError as exc:
        raise LayoutError(f"template must render a relative path without '..': {exc.message}") from exc


def _glob(template: str) -> str:
    """The template with every placeholder replaced by ``*`` (see ``TemplateLayout.discovery_glob``)."""
    out: list[str] = []
    for literal, name, spec, _ in Formatter().parse(template):
        out.append(literal)
        if name is not None:
            out.append("/".join("*" for _ in range((spec or "").count("/") + 1)))
    pattern = "".join(out)
    # Collapse runs of stars produced by adjacent placeholders.
    return re.sub(r"\*{2,}", "*", pattern)


def validate_slug(slug: str) -> str:
    """``slug`` when it matches ``[a-z0-9][a-z0-9-]*`` in full; otherwise ``SlugError`` (``SLUG_INVALID``)."""
    if not isinstance(slug, str) or SLUG.fullmatch(slug) is None:
        raise SlugError(f"slug {slug!r} must match [a-z0-9][a-z0-9-]*")
    return slug


def validate_relative_dir(value: object) -> str:
    """A workspace-relative POSIX path (``devkit_core.core.paths.normalize_relpath``) without backslashes, normalized."""
    if not isinstance(value, str) or not value.strip():
        raise LayoutError("expected a nonempty string")
    message = "must be a workspace-relative path without '..' or backslashes"
    if "\\" in value:
        raise LayoutError(message)
    try:
        return normalize_relpath(value).as_posix()
    except UnsafePathError as exc:
        raise LayoutError(message) from exc


def validate_file_name(value: object) -> str:
    """A bare file name: no directory separators, not ``.`` or ``..``."""
    if not isinstance(value, str) or not value.strip() or "/" in value or "\\" in value or value in {".", ".."}:
        raise LayoutError("expected a bare file name")
    return value


def validate_unit_path(value: object) -> str:
    """A ``unit_path`` template string (``validate_template``)."""
    if not isinstance(value, str):
        raise LayoutError("expected a string")
    validate_template(value)
    return value


LAYOUT_VALIDATORS = {
    "work_dir": validate_relative_dir,
    "unit_path": validate_unit_path,
    "anchor": validate_file_name,
}


def validate_layout_key(key: str, value: object) -> str:
    """The validated value of one layout key; ``LayoutError`` names the problem, the caller names the key."""
    return LAYOUT_VALIDATORS[key](value)


@dataclass(frozen=True)
class LayoutSpec:
    """The layout keys a workflow definition may declare; ``None`` means "use the project default"."""

    work_dir: str | None = None
    unit_path: str | None = None
    anchor: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {"work_dir": self.work_dir, "unit_path": self.unit_path, "anchor": self.anchor}

    def apply(self, base: TemplateLayout) -> TemplateLayout:
        """``base`` with the keys this spec declares replaced."""
        return TemplateLayout(
            self.work_dir or base.work_dir, self.unit_path or base.unit_path, self.anchor or base.anchor
        )


def parse_layout_spec(raw: object) -> LayoutSpec:
    """Validate a ``layout`` mapping; every key is optional. Raises ``LayoutError`` naming the key."""
    if not isinstance(raw, dict):
        raise LayoutError("layout: expected a mapping with work_dir, unit_path, anchor")
    unknown = set(raw) - set(LAYOUT_KEYS)
    if unknown:
        raise LayoutError(f"layout: unknown keys {sorted(unknown)}")
    values: dict[str, str | None] = dict.fromkeys(LAYOUT_KEYS)
    for key in LAYOUT_KEYS:
        if raw.get(key) is None:
            continue
        try:
            values[key] = validate_layout_key(key, raw[key])
        except LayoutError as exc:
            raise LayoutError(f"layout.{key}: {exc}") from exc
    return LayoutSpec(values["work_dir"], values["unit_path"], values["anchor"])


@dataclass(frozen=True)
class TemplateLayout:
    work_dir: str
    unit_path: str
    anchor: str

    def __post_init__(self) -> None:
        validate_template(self.unit_path)

    def new_unit(self, slug: str, when: date_type) -> PurePosixPath:
        """The workspace-relative unit directory for ``slug`` and ``when``.

        Raises ``LayoutError`` when the rendering is absolute or contains ``..``
        (it would leave ``work_dir``).
        """
        validate_slug(slug)
        try:
            rendered = _relative(self.unit_path.format(slug=slug, date=when))
        except LayoutError as exc:
            raise LayoutError(
                f"unit path {self.unit_path!r} escapes the work directory {self.work_dir}",
                fix="Change unit_path so it renders a relative path without '..'",
            ) from exc
        return PurePosixPath(self.work_dir) / rendered

    def discovery_glob(self) -> str:
        """The template with every placeholder replaced by ``*``.

        A ``/`` inside a ``{date}`` format spec (``{date:%Y/%m}``) renders as a
        directory separator, so it becomes ``*/*`` to match the same depth.
        """
        return _glob(self.unit_path)
