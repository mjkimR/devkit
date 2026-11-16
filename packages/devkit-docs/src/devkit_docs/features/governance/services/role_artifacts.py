"""Narrow classification of parent-owned supporting Markdown under formal role roots."""

from __future__ import annotations

import re

from devkit_agt.features.rules import RuleContext
from devkit_core.core import FrontmatterError

from devkit_docs.features.documents.models.ids import is_word_led_slug
from devkit_docs.features.documents.models.markdown import body_start, visible_lines
from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.services.namespaces import living_path
from devkit_docs.features.governance.services.documents import document_index

ROLE_DIRECTORIES = {"designs": "DESIGN", "domain": "DOMAIN", "operations": "OPS"}
ROLE_KINDS = frozenset(ROLE_DIRECTORIES.values())


def artifact_parent(path: str, registered: tuple[Namespace, ...]) -> str | None:
    """Canonical parent coordinate for a role artifact path, without reading its contents."""
    parts = living_path(path, namespaces=registered).split("/")
    if len(parts) < 5 or parts[1] not in ROLE_DIRECTORIES or parts[3] != "artifacts":
        return None
    original = path.split("/")
    directory_index = len(original) - len(parts) + 1
    return "/".join([*original[: directory_index + 1], f"{parts[2]}.md"])


def artifact_state(ctx: RuleContext, path: str, registered: tuple[Namespace, ...]) -> tuple[bool, str]:
    """Whether this is a role artifact path, and its problem (empty for valid ID-free support)."""
    parent_path = artifact_parent(path, registered)
    if parent_path is None:
        return False, ""
    parts = living_path(path, namespaces=registered).split("/")
    parent = parts[2]
    prefix = ROLE_DIRECTORIES[parts[1]]
    if not parent.startswith(f"{prefix}-") or not is_word_led_slug(parent.removeprefix(f"{prefix}-")):
        return True, "role artifact needs a same-kind canonical parent ID directory"
    parent_file = ctx.workspace_root / parent_path
    if any(
        candidate.is_symlink()
        for candidate in (parent_file, *parent_file.parents)
        if candidate != ctx.workspace_root and candidate.is_relative_to(ctx.workspace_root)
    ):
        return True, "role artifact has no eligible canonical parent document in the same docs root"
    eligible = any(document.path == parent_path and document.id == parent for document in document_index(ctx).documents)
    if not eligible:
        return True, "role artifact has no eligible canonical parent document in the same docs root"
    if not path.endswith(".md"):
        return True, ""
    try:
        data = ctx.cache.get_frontmatter(path)
        text = ctx.cache.read_text(path)
        start, line_number = body_start(text)
    except FrontmatterError:
        return True, "role artifact has malformed frontmatter"
    heading = next(
        (
            line.text
            for line in visible_lines(text, start=start, first_line=line_number, mask_links=False, keep_id_spans=True)
            if line.text.startswith("# ")
        ),
        "",
    )
    if (data is not None and "id" in data) or re.match(r"# (?:\[|`)[A-Z]+-", heading):
        return True, "role artifact must be ID-free; promote independent Markdown to a canonical peer"
    if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(parent)}(?![A-Za-z0-9_-])", text) is None:
        return True, "role artifact must name its canonical parent in its text"
    return True, ""
