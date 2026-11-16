"""Narrow classification of parent-owned supporting Markdown under formal role roots."""

from __future__ import annotations

import re

from devkit_agt.features.rules import RuleContext
from devkit_core.core import FrontmatterError

from devkit_docs.features.documents.models.ids import is_word_led_slug
from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.services.namespaces import living_path

ROLE_DIRECTORIES = {"designs": "DESIGN", "domain": "DOMAIN", "operations": "OPS"}
ROLE_KINDS = frozenset(ROLE_DIRECTORIES.values())


def artifact_state(ctx: RuleContext, path: str, registered: tuple[Namespace, ...]) -> tuple[bool, str]:
    """Whether this is a role artifact path, and its problem (empty for valid ID-free support)."""
    parts = living_path(path, namespaces=registered).split("/")
    if len(parts) < 5 or parts[1] not in ROLE_DIRECTORIES or parts[3] != "artifacts":
        return False, ""
    parent = parts[2]
    prefix = ROLE_DIRECTORIES[parts[1]]
    if not parent.startswith(f"{prefix}-") or not is_word_led_slug(parent.removeprefix(f"{prefix}-")):
        return True, "role artifact needs a same-kind canonical parent ID directory"
    original = path.split("/")
    directory_index = len(original) - len(parts) + 1
    parent_path = "/".join([*original[: directory_index + 1], f"{parent}.md"])
    try:
        parent_text = ctx.cache.read_text_strict(parent_path)
    except FileNotFoundError:
        parent_text = None
    if parent_text is None:
        return True, "role artifact has no canonical parent file in the same docs root"
    try:
        owner = ctx.cache.get_frontmatter(parent_path)
        data = ctx.cache.get_frontmatter(path) if path.endswith(".md") else None
    except FrontmatterError:
        return True, "role artifact or parent has malformed frontmatter"
    if owner is None or owner.get("id") != parent:
        return True, "role artifact parent must declare its canonical ID"
    if not path.endswith(".md"):
        return True, ""
    text = ctx.cache.read_text(path)
    heading = next((line for line in text.splitlines() if line.startswith("# ")), "")
    if (data is not None and "id" in data) or re.match(r"# (?:\[|`)[A-Z]+-", heading):
        return True, "role artifact must be ID-free; promote independent Markdown to a canonical peer"
    if parent not in text:
        return True, "role artifact must name its canonical parent in its text"
    return True, ""
