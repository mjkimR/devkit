"""``RULE-proposal-boundaries``: a proposal's ``target_area`` and ``boundaries.owns`` name existing paths.

Checks every proposal anchor (``docs/proposals/PROP-<slug>/proposal.md`` or ``docs/proposals/PROP-<slug>.md``) whose
``status`` is ``draft``, ``reviewing`` or ``accepted`` (``ADR-proposal-boundaries-name-existing-paths``):

- ``target_area`` (optional) is a string, ``boundaries`` a mapping and ``boundaries.owns`` a list of strings;
- an entry containing ``<...>`` is the template placeholder, reported under its own message;
- every other entry is a literal repository-relative path (``devkit_spec.features.entrypoints.normalize``) that resolves,
  tried in order, relative to the repository root, to the proposal's namespace docs root (``docs/packages/<name>/``,
  when ``namespace`` names a registered namespace), to ``docs/``, then as a capability area under the namespace's and
  the global ``capabilities/``. A trailing ``/`` requires a directory. A snapshot run (``check --staged``, ``--ci``)
  resolves in the snapshot's tree.

``boundaries.excludes`` is not checked. A warning, not fixable: the rule cannot know the intended area. Reported for
the targeted anchors (devkit's targeting), with no rescan for deleted paths.
"""

from __future__ import annotations

import re
from typing import Any

import yaml
from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate
from devkit_core.core.yaml import safe_compose

from devkit_spec.base.errors import EntrypointsPathError
from devkit_spec.features.documents import Document
from devkit_spec.features.entrypoints import exists, normalize
from devkit_spec.features.governance import document_index, is_proposal_anchor, namespaces

RULE_ID = "RULE-proposal-boundaries"
CHECKED_STATUSES = frozenset({"draft", "reviewing", "accepted"})
TARGET_AREA = "target_area"
BOUNDARIES = "boundaries"
OWNS = "owns"
OWNS_FIELD = f"{BOUNDARIES}.{OWNS}"
PLACEHOLDER = re.compile(r"<[^<>]*>")
REMEDIATION = (
    "Name an existing repository path, docs-root path or capability area; for a path the Development will create, "
    "name its nearest existing parent directory and the new path in the proposal text"
)
PLACEHOLDER_REMEDIATION = "Replace the placeholder with the capability area (for example delivery/) or repository path"


class ProposalBoundariesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="proposal-boundaries",
            description="A proposal's target_area and boundaries.owns entries name existing paths.",
            phase=Phase.LINTER,
            severity=Severity.WARNING,
            guide="guide.md",
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        found: list[Violation] = []
        docs_roots: dict[str, str] | None = None
        for document in index.documents:
            if not is_proposal_anchor(document.path) or not ctx.is_file_targeted(document.path):
                continue
            if document.status.strip().lower() not in CHECKED_STATUSES:
                continue
            if docs_roots is None:
                docs_roots = {namespace.name: namespace.docs for namespace in namespaces(ctx)}
            found.extend(self._check(ctx, document, docs_roots))
        return found

    def _check(self, ctx: RuleContext, document: Document, docs_roots: dict[str, str]) -> list[Violation]:
        lines = _Lines.read(ctx.cache.read_text(document.path))
        namespace = document.frontmatter.get("namespace")
        docs_root = docs_roots.get(namespace) if isinstance(namespace, str) else None
        roots = ["", *([f"{docs_root}/"] if docs_root else []), "docs/"]
        areas = [*([f"{docs_root}/capabilities/"] if docs_root else []), "docs/capabilities/"]
        candidates = [*roots, *areas]
        found: list[Violation] = []

        def entry(field: str, item: Any, line: int) -> None:
            message, remediation = _entry_problem(ctx, field, item, candidates)
            if message:
                found.append(self._violation(document, line, message, remediation))

        frontmatter = document.frontmatter
        if TARGET_AREA in frontmatter and frontmatter[TARGET_AREA] is not None:
            value = frontmatter[TARGET_AREA]
            if isinstance(value, str):
                entry(TARGET_AREA, value, lines.target_area)
            else:
                found.append(self._violation(document, lines.target_area, f"{TARGET_AREA} must be a path string"))
        boundaries = frontmatter.get(BOUNDARIES)
        if boundaries is None:
            return found
        if not isinstance(boundaries, dict):
            found.append(self._violation(document, lines.boundaries, f"{BOUNDARIES} must be a mapping with {OWNS}"))
            return found
        owns = boundaries.get(OWNS)
        if owns is None:
            return found
        if not isinstance(owns, list):
            found.append(self._violation(document, lines.owns, f"{OWNS_FIELD} must be a list of path strings"))
            return found
        for position, item in enumerate(owns):
            line = lines.owns_items[position] if position < len(lines.owns_items) else lines.owns
            if isinstance(item, str):
                entry(OWNS_FIELD, item, line)
            else:
                found.append(self._violation(document, line, f"{OWNS_FIELD} must contain only path strings"))
        return found

    def _violation(self, document: Document, line: int, message: str, remediation: str = REMEDIATION) -> Violation:
        return Violation(rule_id=self.id, file=document.path, line=line, message=message, remediation=remediation)


def _entry_problem(ctx: RuleContext, field: str, item: str, candidates: list[str]) -> tuple[str, str]:
    """The message and remediation for one entry, or empty strings when it resolves."""
    if PLACEHOLDER.search(item):
        return f"{field} entry {item!r} is the template placeholder; name the area", PLACEHOLDER_REMEDIATION
    try:
        path = normalize(item)
    except EntrypointsPathError:
        return f"{field} entry {item!r} is not a literal repository-relative path", REMEDIATION
    directory = item.strip().endswith("/")
    for prefix in candidates:
        if exists(ctx.workspace_root, normalize(f"{prefix}{path}"), directory=directory):
            return "", ""
    kind = "directory" if directory else "path"
    return (
        f"{field} entry {item!r} names no existing {kind} (repository path, docs-root path or capability area)",
        REMEDIATION,
    )


class _Lines:
    """The 1-based frontmatter lines of ``target_area``, ``boundaries``, ``boundaries.owns`` and each owns item."""

    def __init__(self, first: int = 1) -> None:
        self.target_area = self.boundaries = self.owns = first
        self.owns_items: list[int] = []

    @classmethod
    def read(cls, text: str) -> _Lines:
        try:
            block = locate(text)
        except FrontmatterError:
            return cls()
        if block is None:
            return cls()
        first = text.count("\n", 0, block.header_start) + 1
        lines = cls(first)
        try:
            root: Any = safe_compose(block.header, source="proposal frontmatter")
        except yaml.YAMLError:
            return lines
        if not isinstance(root, yaml.MappingNode):
            return lines
        for key, value in root.value:
            if not isinstance(key, yaml.ScalarNode):
                continue
            if key.value == TARGET_AREA:
                lines.target_area = first + key.start_mark.line
            elif key.value == BOUNDARIES:
                lines.boundaries = lines.owns = first + key.start_mark.line
                if isinstance(value, yaml.MappingNode):
                    lines._owns(value, first)
        return lines

    def _owns(self, boundaries: yaml.MappingNode, first: int) -> None:
        for key, value in boundaries.value:
            if isinstance(key, yaml.ScalarNode) and key.value == OWNS:
                self.owns = first + key.start_mark.line
                if isinstance(value, yaml.SequenceNode):
                    self.owns_items = [first + item.start_mark.line for item in value.value]
