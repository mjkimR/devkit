"""``workflow`` assets: definition files evaluated by ``devkit.workflow``.

Distribution validates only what it needs to deploy and catalog the file: a
single Markdown document whose frontmatter declares a slug ``id`` and a
``stages`` list. Stage semantics are validated by ``devkit workflow validate``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.core import frontmatter
from devkit.core.errors import FrontmatterError

from ..errors import BundleError
from .common import SLUG


@dataclass(frozen=True)
class WorkflowHeader:
    id: str
    title: str
    stages: int


def workflow_entry(root: Path, source: str) -> Path:
    path = root / source
    if not path.is_file() or path.suffix.lower() != ".md":
        raise BundleError(f"{source}: workflow must be a single Markdown file")
    return path


def read_workflow_header(data: bytes, context: str) -> WorkflowHeader:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise BundleError(f"{context}: workflow must be UTF-8") from exc
    try:
        metadata = frontmatter.parse(text).data
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc
    if metadata is None:
        raise BundleError(f"{context}: workflow requires YAML frontmatter")
    workflow_id = metadata.get("id")
    if not isinstance(workflow_id, str) or not SLUG.fullmatch(workflow_id):
        raise BundleError(f"{context}: id must be a lowercase slug")
    stages = metadata.get("stages")
    if not isinstance(stages, list) or not stages:
        raise BundleError(f"{context}: stages must be a nonempty list")
    title = metadata.get("title", "")
    return WorkflowHeader(workflow_id, title if isinstance(title, str) else "", len(stages))
