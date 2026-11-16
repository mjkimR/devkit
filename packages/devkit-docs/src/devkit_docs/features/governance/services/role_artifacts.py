"""Narrow classification of parent-owned support files under formal role roots, by the kind table's layout.

- An ``area-bundle`` kind (design): every file of ``<root>/<directory>/<area>/<ID>/`` other than the bundle's
  ``layout_anchor`` (``design.md``), at any depth, is support of that anchor. Supporting Markdown is ID-free and
  names its parent; identified Markdown, a nested bundle anchor included, is a stray to promote to a peer bundle.
- A ``flat`` or ``area`` kind (operations, domain): files under ``<ID>/artifacts/`` beside the document, in its
  directory (in its area directory for an ``area`` kind), are support of ``<ID>.md``.

``README.md`` in a bundle is exempt from the identity and parent-naming checks, as in area directories; under
``<ID>/artifacts/`` it is supporting Markdown like any other. A non-Markdown file under a role directory that is
neither support nor in a document location (``off_grammar``), such as one left at the flat ``<ID>/artifacts/`` path of
an ``area`` kind, fits no path of its kind.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from devkit_agt.features.rules import RuleContext
from devkit_core.core import FrontmatterError

from devkit_docs.features.documents import Kind, KindDefinition, KindTableError, definition
from devkit_docs.features.documents.models.ids import is_word_led_slug
from devkit_docs.features.documents.models.markdown import body_start, visible_lines
from devkit_docs.features.documents.models.model import IDENTITY_FIELDS
from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.services.namespaces import living_path
from devkit_docs.features.governance.services.documents import document_index

ROLE_KINDS = (Kind.DESIGN, Kind.DOMAIN, Kind.OPERATIONS)
README = "README.md"

ORPHAN = "role artifact has no eligible canonical parent document in the same docs root"
BUNDLE_ORPHAN = "bundle has no eligible {anchor} anchor whose ID is the bundle directory name"
BUNDLE_STRAY = "identified Markdown inside a {prefix} bundle is a stray; only its {anchor} anchor carries an ID"
BUNDLE_STRAY_REMEDIATION = (
    "Promote it to a peer bundle {root}/{directory}/{{area}}/{prefix}-{{slug}}/{anchor} with its own ID, or remove"
    " its ID and name the parent {parent} in its text"
)
OFF_GRAMMAR = "file under {directory}/ fits no {prefix} document or support path"
OFF_GRAMMAR_REMEDIATION = "Move it to {location}, or remove it"


def role_rows() -> tuple[KindDefinition, ...]:
    """The formal role kinds' rows, read when called."""
    return tuple(definition(kind) for kind in ROLE_KINDS)


def role_row(directory: str) -> KindDefinition | None:
    """The formal role row stored under ``directory`` (``designs``), or ``None``."""
    return next((row for row in role_rows() if row.directory == directory), None)


@dataclass(frozen=True, slots=True)
class Support:
    """A support file's owner: ``parent_path`` is the workspace path of the parent document, ``parent_id`` the ID
    its path requires (the bundle or ``<ID>`` directory name) and ``docs_root`` its docs root."""

    row: KindDefinition
    parent_path: str
    parent_id: str
    docs_root: str


def _located(path: str, registered: tuple[Namespace, ...]) -> tuple[KindDefinition, list[str], list[str], int] | None:
    """The role row of ``path``, its parts under ``docs/`` (``living_path``), its own parts and the index of its role
    directory in them; ``None`` outside a role directory."""
    parts = living_path(path, namespaces=registered).split("/")
    row = role_row(parts[1]) if len(parts) > 1 and parts[0] == "docs" else None
    if row is None:
        return None
    original = path.split("/")
    return row, parts, original, len(original) - len(parts) + 1


def support_of(path: str, registered: tuple[Namespace, ...]) -> Support | None:
    """The owner of the role support file at ``path``, from its path alone, or ``None`` when it is not support."""
    located = _located(path, registered)
    if located is None:
        return None
    row, parts, original, directory_index = located
    docs_root = "/".join(original[:directory_index])
    if row.bundled:
        # <directory>/<area>/<ID>/<file...>: anything in the bundle but its anchor.
        if len(parts) < 5 or parts[4:] == [row.layout_anchor]:
            return None
        bundle = original[: directory_index + 3]
        return Support(row, "/".join([*bundle, row.layout_anchor]), parts[3], docs_root)
    owner = 3 if row.area_scoped else 2  # the index of the <ID> directory
    if len(parts) < owner + 3 or parts[owner + 1] != "artifacts":
        return None
    parent = original[: directory_index + owner - 1]
    return Support(row, "/".join([*parent, f"{parts[owner]}.md"]), parts[owner], docs_root)


def off_grammar(path: str, registered: tuple[Namespace, ...]) -> tuple[str, str] | None:
    """The problem and remediation of a non-Markdown file under a formal role directory that is not support of a
    document of the kind, or ``None`` (Markdown, a dotfile such as ``.gitkeep``, support, or outside a role
    directory). A file at the flat ``<ID>/artifacts/`` path of an ``area`` kind is pointed at its area path."""
    located = _located(path, registered)
    name = path.rsplit("/", 1)[-1]
    if located is None or name.endswith(".md") or name.startswith(".") or support_of(path, registered) is not None:
        return None
    row, parts, original, directory_index = located
    base = "/".join([*original[:directory_index], row.directory])
    slug = f"{row.prefix}-{{word-led-slug}}"
    if (
        row.area_scoped
        and not row.bundled
        and len(parts) >= 5
        and parts[3] == "artifacts"
        and _owner_named(row.prefix, parts[2])
    ):
        slug = parts[2]  # the flat ``<ID>/artifacts/`` shape the area layout replaced
    if row.bundled:
        location = f"the bundle {base}/{{area}}/{slug}/ beside its {row.layout_anchor}"
    elif row.area_scoped:
        location = f"{base}/{{area}}/{slug}/artifacts/ beside {base}/{{area}}/{slug}.md"
    else:
        location = f"{base}/{slug}/artifacts/ beside {base}/{slug}.md"
    return (
        OFF_GRAMMAR.format(directory=base, prefix=row.prefix),
        OFF_GRAMMAR_REMEDIATION.format(location=location),
    )


def artifact_parent(path: str, registered: tuple[Namespace, ...]) -> str | None:
    """Canonical parent coordinate for a role artifact path, without reading its contents."""
    support = support_of(path, registered)
    return support.parent_path if support else None


def _identified(ctx: RuleContext, path: str) -> bool | None:
    """Whether the Markdown at ``path`` declares an ID field or opens its first visible H1 with an ID token;
    ``None`` for malformed frontmatter."""
    try:
        data = ctx.cache.get_frontmatter(path)
        text = ctx.cache.read_text(path)
        start, line_number = body_start(text)
    except FrontmatterError:
        return None
    heading = next(
        (
            line.text
            for line in visible_lines(text, start=start, first_line=line_number, mask_links=False, keep_id_spans=True)
            if line.text.startswith("# ")
        ),
        "",
    )
    return bool(data is not None and any(field in data for field in IDENTITY_FIELDS)) or bool(
        re.match(r"# (?:\[|`)[A-Z]+-", heading)
    )


def stray_remediation(path: str, registered: tuple[Namespace, ...]) -> str:
    """The remediation of an identified Markdown file inside a bundle; ``KindTableError`` outside one."""
    support = support_of(path, registered)
    if support is None or not support.row.bundled:
        raise KindTableError(f"{path} is not a bundle support file")
    row = support.row
    return BUNDLE_STRAY_REMEDIATION.format(
        root=support.docs_root,
        directory=row.directory,
        prefix=row.prefix,
        anchor=row.layout_anchor,
        parent=support.parent_id,
    )


def _owner_named(prefix: str, parent: str) -> bool:
    return parent.startswith(f"{prefix}-") and is_word_led_slug(parent.removeprefix(f"{prefix}-"))


def artifact_state(ctx: RuleContext, path: str, registered: tuple[Namespace, ...]) -> tuple[bool, str]:
    """Whether this is a role artifact path, and its problem (empty for valid ID-free support)."""
    support = support_of(path, registered)
    if support is None:
        return False, ""
    row, parent = support.row, support.parent_id
    # A bundle's README.md is navigation, exempt like an area directory's; under <ID>/artifacts/ it is support.
    markdown = path.endswith(".md") and not (row.bundled and path.rsplit("/", 1)[-1] == README)
    if row.bundled:
        if markdown:  # a stray is reported whatever its bundle holds
            identified = _identified(ctx, path)
            if identified is None:
                return True, "role artifact has malformed frontmatter"
            if identified:
                return True, BUNDLE_STRAY.format(prefix=row.prefix, anchor=row.layout_anchor)
        orphan = BUNDLE_ORPHAN.format(anchor=row.layout_anchor)
        if not _owner_named(row.prefix, parent):
            return True, f"bundle directory must be named {row.prefix}-{{word-led-slug}}"
    else:
        orphan = ORPHAN
        if not _owner_named(row.prefix, parent):
            return True, "role artifact needs a same-kind canonical parent ID directory"
    parent_file = ctx.workspace_root / support.parent_path
    if any(
        candidate.is_symlink()
        for candidate in (parent_file, *parent_file.parents)
        if candidate != ctx.workspace_root and candidate.is_relative_to(ctx.workspace_root)
    ):
        return True, orphan
    documents = document_index(ctx).documents
    if not any(document.path == support.parent_path and document.id == parent for document in documents):
        return True, orphan
    if not markdown:
        return True, ""
    if not row.bundled:
        identified = _identified(ctx, path)
        if identified is None:
            return True, "role artifact has malformed frontmatter"
        if identified:
            return True, "role artifact must be ID-free; promote independent Markdown to a canonical peer"
    if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(parent)}(?![A-Za-z0-9_-])", ctx.cache.read_text(path)) is None:
        return True, "role artifact must name its canonical parent in its text"
    return True, ""
