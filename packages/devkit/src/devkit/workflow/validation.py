"""Validation of workflow definitions, one at a time and across a workspace."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from devkit.workflow.checks import CheckError, Registry
from devkit.workflow.definition import (
    HANDOFF_GATE,
    ISOLATIONS,
    SCHEMA_VERSION,
    Problem,
    Stage,
    WorkflowDocument,
    schema_hash,
)
from devkit.workflow.ids import IDENT_HINT, is_ident
from devkit.workflow.roles import is_builtin_role

if TYPE_CHECKING:
    from devkit.workflow.plugins import BaseCheck


def validate(
    doc: WorkflowDocument,
    anchor: str,
    known_ids: Iterable[str] | None = None,
    roles: Mapping[str, str] | None = None,
    plugins: Iterable[BaseCheck] = (),
) -> list[Problem]:
    """Every problem in the document; an empty list means it is usable.

    ``anchor`` is the project default; a definition that declares its own
    anchor is validated against that one. ``known_ids`` are the workflow ids
    that exist in the workspace; when given, a ``next`` candidate naming
    another id is reported. ``roles`` is the project's subagent vocabulary
    (``role -> contract path``); when given, a stage role outside it is
    reported, and ``None`` skips that check. ``plugins`` are the loaded plugin
    checks that definitions may reference.
    """
    problems: list[Problem] = []
    anchor = doc.anchor(anchor)
    plugins = tuple(plugins)
    if not is_ident(doc.id):
        problems.append(Problem("", "id", f"{doc.id!r} must match {IDENT_HINT}"))
    if doc.schema_version != SCHEMA_VERSION:
        problems.append(
            Problem(
                "", "schema_version", f"unsupported schema_version {doc.schema_version} (expected {SCHEMA_VERSION})"
            )
        )
    for key in doc.unknown_keys:
        problems.append(Problem("", key, "unknown document key"))
    try:
        registry = Registry.build(anchor, doc.declared_checks, plugins)
    except CheckError as exc:
        problems.append(Problem("", "checks", str(exc)))
        try:
            registry = Registry.build(anchor, (), plugins)
        except CheckError:
            registry = Registry.build(anchor)
    gates = doc.gates
    for check in doc.declared_checks:
        if check.name in gates:
            problems.append(
                Problem(
                    "", "checks", f"declared check {check.name!r} has the name of a gate; `--given` would be ambiguous"
                )
            )

    ids = [s.id for s in doc.stages]
    seen: set[str] = set()
    for s in doc.stages:
        problems.extend(_stage_problems(s, ids, seen, registry, roles))
        seen.add(s.id)
    known = set(known_ids) if known_ids is not None else None
    seen_candidates: set[str] = set()
    for i, c in enumerate(doc.next):
        where = f"next[{i}]"
        if not is_ident(c.workflow):
            problems.append(Problem("", f"{where}.workflow", f"{c.workflow!r} must match {IDENT_HINT}"))
        elif c.workflow == doc.id:
            problems.append(Problem("", f"{where}.workflow", "a workflow cannot hand off to itself"))
        elif known is not None and c.workflow not in known:
            problems.append(Problem("", f"{where}.workflow", f"unknown workflow {c.workflow!r}"))
        if c.workflow in seen_candidates:
            problems.append(Problem("", f"{where}.workflow", f"duplicate candidate {c.workflow!r}"))
        seen_candidates.add(c.workflow)
        for ref in c.when:
            try:
                registry.resolve_name(ref)
            except CheckError as exc:
                problems.append(Problem("", f"{where}.when", str(exc)))
    return problems


def _stage_problems(
    s: Stage, ids: list[str], seen: set[str], registry: Registry, roles: Mapping[str, str] | None
) -> list[Problem]:
    problems: list[Problem] = []
    if not is_ident(s.id):
        problems.append(Problem(s.id, "id", f"{s.id!r} must match {IDENT_HINT}"))
    if s.id in seen:
        problems.append(Problem(s.id, "id", "duplicate stage id"))
    for key in s.unknown_keys:
        problems.append(Problem(s.id, key, "unknown stage key"))
    if s.isolation not in ISOLATIONS:
        problems.append(Problem(s.id, "isolation", f"{s.isolation!r} not in {'|'.join(ISOLATIONS)}"))
    if roles is not None and not is_builtin_role(s.role) and s.role not in roles:
        problems.append(Problem(s.id, "role", f"unknown role {s.role!r} (no subagent contract found)"))
    if s.gate == HANDOFF_GATE:
        problems.append(Problem(s.id, "human_gate", f"{HANDOFF_GATE!r} is reserved for workflow handoff"))
    elif s.gate is not None and not is_ident(s.gate):
        problems.append(Problem(s.id, "human_gate", f"gate name {s.gate!r} must match {IDENT_HINT}"))
    for fld in ("entry", "exit"):
        for ref in getattr(s, fld):
            try:
                registry.resolve_name(ref)
            except CheckError as exc:
                problems.append(Problem(s.id, fld, str(exc)))
    for i, r in enumerate(s.returns):
        if not r.to:
            problems.append(Problem(s.id, f"returns[{i}].to", "missing target stage"))
        elif r.to not in ids:
            problems.append(Problem(s.id, f"returns[{i}].to", f"unknown stage {r.to!r}"))
        if not r.when:
            problems.append(Problem(s.id, f"returns[{i}].when", "missing reason"))
    return problems


SHARED_STAGE_FIELDS = ("exit", "gate", "role", "isolation", "skills", "artifacts")


def shared_stage_problems(docs: Iterable[WorkflowDocument]) -> list[str]:
    """Stages that share an id across definitions but are not the same stage.

    A stage id is shared vocabulary: skills, runners and people recognize it by
    name. Two definitions that give the same id different ``exit`` checks,
    gate, role, isolation, skills or artifacts are reported once per field,
    each against the first definition that declared the id.
    """
    first: dict[str, tuple[WorkflowDocument, Stage]] = {}
    problems: list[str] = []
    for doc in docs:
        for stage in doc.stages:
            if stage.id not in first:
                first[stage.id] = (doc, stage)
                continue
            base_doc, base = first[stage.id]
            if base_doc.id == doc.id:
                continue
            for fld in SHARED_STAGE_FIELDS:
                if getattr(base, fld) != getattr(stage, fld):
                    problems.append(f"shared stage {stage.id!r} differs between {base_doc.id} and {doc.id}: {fld}")
    return problems


@dataclass(frozen=True)
class DefinitionReport:
    """The validation result of one loaded definition."""

    doc: WorkflowDocument
    problems: tuple[Problem, ...]

    @property
    def ok(self) -> bool:
        return not self.problems

    def to_dict(self, root: Path | None = None) -> dict[str, object]:
        path = self.doc.path
        if path is not None and root is not None and path.is_relative_to(root):
            path = path.relative_to(root)
        return {
            "id": self.doc.id,
            "path": path.as_posix() if path else None,
            "valid": self.ok,
            "hash": None if self.problems else schema_hash(self.doc),
            "problems": [str(p) for p in self.problems],
        }


@dataclass(frozen=True)
class ValidationReport:
    """Every definition checked, the files that could not be loaded and cross-definition problems."""

    definitions: tuple[DefinitionReport, ...] = ()
    load_errors: tuple[str, ...] = ()
    shared: tuple[str, ...] = ()
    roles_checked: bool = True

    @property
    def ok(self) -> bool:
        return not self.load_errors and not self.shared and all(r.ok for r in self.definitions)


def validate_workspace(
    docs: Sequence[WorkflowDocument],
    load_errors: Sequence[str],
    *,
    anchor: str,
    known_ids: Iterable[str],
    roles: Mapping[str, str] | None,
    plugins: Iterable[BaseCheck] = (),
    compare_shared: bool = True,
) -> ValidationReport:
    """Validate ``docs`` together: each one, and (with ``compare_shared``) their shared stages."""
    known = set(known_ids) | {d.id for d in docs}
    plugins = tuple(plugins)
    reports = tuple(DefinitionReport(d, tuple(validate(d, anchor, known, roles, plugins))) for d in docs)
    shared = tuple(shared_stage_problems(docs)) if compare_shared else ()
    return ValidationReport(reports, tuple(load_errors), shared, roles is not None)
