"""Structural direct unit prerequisites, shared by rules and handoff preflight."""

from __future__ import annotations

from devkit_spec.features.documents.models.ids import Kind, is_id
from devkit_spec.features.documents.models.model import Document, is_unit_anchor
from devkit_spec.features.documents.repositories.index import DocumentIndex


def target_problem(index: DocumentIndex, target: str) -> str | None:
    """Resolve a PROP/SPEC anchor by its ID or an alias (``DocumentIndex.canonical``), including completed history."""
    if not is_id(target) or not target.startswith(("PROP-", "SPEC-")):
        return f"depends_on takes PROP- or SPEC- anchor IDs, got {target!r}"
    found = index.canonical(target)
    if found is None:
        count = len(index.by_id.get(target) or index.by_alias.get(target, []))
        return f"depends_on target {target} resolves to {count} documents; expected one anchor"
    if not is_unit_anchor(found[0]):
        return f"depends_on target {target} is not a proposal/spec anchor"
    return None


def live_unit(document: Document) -> bool:
    return is_unit_anchor(document) and not (document.kind is Kind.SPEC and document.status.lower() == "completed")


def cycle_members(index: DocumentIndex) -> set[str]:
    """All live vertices on cycles; completed SPEC targets are terminal. An alias edge leads to its document."""
    graph = {
        d.id: sorted(index.canonical_id(ref.target) for ref in d.references if ref.field == "depends_on")
        for d in index.documents
        if live_unit(d)
    }
    cycles: set[str] = set()
    for source in sorted(graph):
        pending = list(graph[source])
        seen: set[str] = set()
        while pending:
            current = pending.pop()
            if current == source:
                cycles.add(source)
                break
            if current not in seen:
                seen.add(current)
                pending.extend(graph.get(current, []))
    return cycles
