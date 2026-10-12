"""``workflow`` assets: definition files evaluated by ``agent-workflow-engine``.

Distribution validates only what it needs to deploy and catalog the file: a
single Markdown document whose frontmatter declares a slug ``id`` and a
``stages`` list. Stage semantics are validated by ``agent-workflow validate``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .manifest import SLUG, BundleError


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
        lines = data.decode("utf-8").splitlines(keepends=True)
    except UnicodeError as exc:
        raise BundleError(f"{context}: workflow must be UTF-8") from exc
    if not lines or lines[0].strip() != "---":
        raise BundleError(f"{context}: workflow requires YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        raise BundleError(f"{context}: unclosed workflow frontmatter")
    try:
        metadata = yaml.safe_load("".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise BundleError(f"{context}: invalid YAML frontmatter") from exc
    if not isinstance(metadata, dict):
        raise BundleError(f"{context}: frontmatter must be a mapping")
    workflow_id = metadata.get("id")
    if not isinstance(workflow_id, str) or not SLUG.fullmatch(workflow_id):
        raise BundleError(f"{context}: id must be a lowercase slug")
    stages = metadata.get("stages")
    if not isinstance(stages, list) or not stages:
        raise BundleError(f"{context}: stages must be a nonempty list")
    title = metadata.get("title", "")
    return WorkflowHeader(workflow_id, title if isinstance(title, str) else "", len(stages))
