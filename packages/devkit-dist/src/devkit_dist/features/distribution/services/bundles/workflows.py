"""``workflow`` assets: definition files evaluated by ``devkit_agt.features.workflow``.

Distribution validates only what it needs to deploy and catalog the file: a
single Markdown document whose frontmatter declares a slug ``id`` and a
``stages`` list. Stage semantics are validated by ``devkit workflow validate``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles.common import SLUG, read_frontmatter


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
    _, _, metadata = read_frontmatter(data, context, "workflow")
    workflow_id = metadata.get("id")
    if not isinstance(workflow_id, str) or not SLUG.fullmatch(workflow_id):
        raise BundleError(f"{context}: id must be a lowercase slug")
    stages = metadata.get("stages")
    if not isinstance(stages, list) or not stages:
        raise BundleError(f"{context}: stages must be a nonempty list")
    title = metadata.get("title", "")
    return WorkflowHeader(workflow_id, title if isinstance(title, str) else "", len(stages))
