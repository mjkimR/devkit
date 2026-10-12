"""Validation of workflow definitions, one at a time and across a workspace.

Problems are collected, never raised: ``DefinitionProblem`` (and its
``CheckReferenceProblem`` and ``RoleUnknownProblem`` subclasses) for one
definition, ``SharedStageMismatchError`` across definitions.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from devkit.workflow.definition.checks import Registry
from devkit.workflow.definition.definition import (
    HANDOFF_GATE,
    ISOLATIONS,
    SCHEMA_VERSION,
    StageDefinition,
    WorkflowDocument,
    schema_hash,
)
from devkit.workflow.definition.ids import IDENT_HINT, is_ident
from devkit.workflow.errors import (
    CheckError,
    CheckReferenceProblem,
    DefinitionProblem,
    RoleUnknownProblem,
    SharedStageMismatchError,
    WorkflowError,
)
from devkit.workflow.project.roles import is_builtin_role

if TYPE_CHECKING:
    from devkit.workflow.project.plugins import BaseCheck

SHARED_STAGE_FIELDS = ("exit", "gate", "role", "isolation", "skills", "artifacts")


def _where(stage: str, field: str) -> str:
    return f"{stage}.{field}" if stage else field


def _problem(stage: str, field: str, message: str) -> DefinitionProblem:
    return DefinitionProblem(message, where=_where(stage, field))


def _check_problem(stage: str, field: str, exc: CheckError) -> CheckReferenceProblem:
    return CheckReferenceProblem(exc.message, where=_where(stage, field))


def _registry(
    anchor: str, doc: WorkflowDocument, plugins: tuple[BaseCheck, ...]
) -> tuple[Registry, list[DefinitionProblem]]:
    """The definition's registry; a declared check that collides falls back to the registry without it."""
    try:
        return Registry.build(anchor, doc.declared_checks, plugins), []
    except CheckError as exc:
        problems: list[DefinitionProblem] = [_check_problem("", "checks", exc)]
    try:
        return Registry.build(anchor, (), plugins), problems
    except CheckError:
        return Registry.build(anchor), problems


def validate_definition(
    doc: WorkflowDocument,
    anchor: str,
    known_ids: Iterable[str] | None = None,
    roles: Mapping[str, str] | None = None,
    plugins: Iterable[BaseCheck] = (),
) -> list[DefinitionProblem]:
    """Every problem in the document; an empty list means it is usable.

    ``anchor`` is the project default; a definition that declares its own
    anchor is validated against that one. ``known_ids`` are the workflow ids
    that exist in the workspace; when given, a ``next`` candidate naming
    another id is reported. ``roles`` is the project's subagent vocabulary
    (``role -> contract path``); when given, a stage role outside it is
    reported, and ``None`` skips that check. ``plugins`` are the loaded plugin
    checks that definitions may reference.
    """
    problems: list[DefinitionProblem] = []
    if not is_ident(doc.id):
        problems.append(_problem("", "id", f"{doc.id!r} must match {IDENT_HINT}"))
    if doc.schema_version != SCHEMA_VERSION:
        problems.append(
            _problem(
                "", "schema_version", f"unsupported schema_version {doc.schema_version} (expected {SCHEMA_VERSION})"
            )
        )
    for key in doc.unknown_keys:
        problems.append(_problem("", key, "unknown document key"))
    registry, registry_problems = _registry(doc.anchor(anchor), doc, tuple(plugins))
    problems.extend(registry_problems)
    gates = doc.gates
    for check in doc.declared_checks:
        if check.name in gates:
            problems.append(
                _problem(
                    "", "checks", f"declared check {check.name!r} has the name of a gate; `--given` would be ambiguous"
                )
            )
    ids = [s.id for s in doc.stages]
    seen: set[str] = set()
    for s in doc.stages:
        problems.extend(_stage_problems(s, ids, seen, registry, roles))
        seen.add(s.id)
    problems.extend(_candidate_problems(doc, registry, known_ids))
    return problems


def _candidate_problems(
    doc: WorkflowDocument, registry: Registry, known_ids: Iterable[str] | None
) -> list[DefinitionProblem]:
    problems: list[DefinitionProblem] = []
    known = set(known_ids) if known_ids is not None else None
    seen: set[str] = set()
    for i, c in enumerate(doc.next):
        where = f"next[{i}]"
        if not is_ident(c.workflow):
            problems.append(_problem("", f"{where}.workflow", f"{c.workflow!r} must match {IDENT_HINT}"))
        elif c.workflow == doc.id:
            problems.append(_problem("", f"{where}.workflow", "a workflow cannot hand off to itself"))
        elif known is not None and c.workflow not in known:
            problems.append(_problem("", f"{where}.workflow", f"unknown workflow {c.workflow!r}"))
        if c.workflow in seen:
            problems.append(_problem("", f"{where}.workflow", f"duplicate candidate {c.workflow!r}"))
        seen.add(c.workflow)
        for ref in c.when:
            try:
                registry.resolve_name(ref)
            except CheckError as exc:
                problems.append(_check_problem("", f"{where}.when", exc))
    return problems


def _stage_problems(
    s: StageDefinition, ids: list[str], seen: set[str], registry: Registry, roles: Mapping[str, str] | None
) -> list[DefinitionProblem]:
    problems: list[DefinitionProblem] = []
    if not is_ident(s.id):
        problems.append(_problem(s.id, "id", f"{s.id!r} must match {IDENT_HINT}"))
    if s.id in seen:
        problems.append(_problem(s.id, "id", "duplicate stage id"))
    for key in s.unknown_keys:
        problems.append(_problem(s.id, key, "unknown stage key"))
    if s.isolation not in ISOLATIONS:
        problems.append(_problem(s.id, "isolation", f"{s.isolation!r} not in {'|'.join(ISOLATIONS)}"))
    if roles is not None and not is_builtin_role(s.role) and s.role not in roles:
        problems.append(
            RoleUnknownProblem(f"unknown role {s.role!r} (no subagent contract found)", where=_where(s.id, "role"))
        )
    if s.gate == HANDOFF_GATE:
        problems.append(_problem(s.id, "human_gate", f"{HANDOFF_GATE!r} is reserved for workflow handoff"))
    elif s.gate is not None and not is_ident(s.gate):
        problems.append(_problem(s.id, "human_gate", f"gate name {s.gate!r} must match {IDENT_HINT}"))
    for fld in ("entry", "exit"):
        for ref in getattr(s, fld):
            try:
                registry.resolve_name(ref)
            except CheckError as exc:
                problems.append(_check_problem(s.id, fld, exc))
    for i, r in enumerate(s.returns):
        if not r.to:
            problems.append(_problem(s.id, f"returns[{i}].to", "missing target stage"))
        elif r.to not in ids:
            problems.append(_problem(s.id, f"returns[{i}].to", f"unknown stage {r.to!r}"))
        if not r.when:
            problems.append(_problem(s.id, f"returns[{i}].when", "missing reason"))
    return problems


def compare_shared_stages(docs: Iterable[WorkflowDocument]) -> list[SharedStageMismatchError]:
    """Stages that share an id across definitions but are not the same stage.

    A stage id is shared vocabulary: skills, runners and people recognize it by
    name. Two definitions that give the same id different ``exit`` checks,
    gate, role, isolation, skills or artifacts are reported once per field,
    each against the first definition that declared the id.
    """
    first: dict[str, tuple[WorkflowDocument, StageDefinition]] = {}
    problems: list[SharedStageMismatchError] = []
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
                    problems.append(
                        SharedStageMismatchError(
                            f"shared stage {stage.id!r} differs between {base_doc.id} and {doc.id}: {fld}",
                            target_files=[doc.path.as_posix()] if doc.path else [],
                            fix=f"Give stage {stage.id!r} the same {fld} in both definitions, or rename it in one",
                        )
                    )
    return problems


def _display_path(path: Path | None, root: Path | None) -> str | None:
    if path is not None and root is not None and path.is_relative_to(root):
        path = path.relative_to(root)
    return path.as_posix() if path else None


@dataclass(frozen=True)
class DefinitionReport:
    """The validation result of one loaded definition."""

    doc: WorkflowDocument
    problems: tuple[DefinitionProblem, ...]

    @property
    def ok(self) -> bool:
        return not self.problems

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        return {
            "id": self.doc.id,
            "path": _display_path(self.doc.path, root),
            "ok": self.ok,
            "hash": schema_hash(self.doc) if self.ok else None,
            "errors": [p.to_dict() for p in self.problems],
        }


@dataclass(frozen=True)
class ValidationReport:
    """Every definition checked, the files that could not be loaded and cross-definition problems."""

    definitions: tuple[DefinitionReport, ...] = ()
    load_errors: tuple[WorkflowError, ...] = ()
    shared: tuple[SharedStageMismatchError, ...] = ()
    roles_checked: bool = True

    @property
    def errors(self) -> tuple[WorkflowError, ...]:
        """Every problem: load errors, shared-stage mismatches and each definition's problems."""
        return (*self.load_errors, *self.shared, *(p for r in self.definitions for p in r.problems))

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        """``validate --format json``: definitions with their own ``errors``, plus load and shared-stage ``errors``."""
        return {
            "ok": self.ok,
            "roles_checked": self.roles_checked,
            "definitions": [r.to_dict(root) for r in self.definitions],
            "errors": [e.to_dict() for e in (*self.load_errors, *self.shared)],
        }


def validate_definitions(
    docs: Sequence[WorkflowDocument],
    load_errors: Sequence[WorkflowError],
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
    reports = tuple(DefinitionReport(d, tuple(validate_definition(d, anchor, known, roles, plugins))) for d in docs)
    shared = tuple(compare_shared_stages(docs)) if compare_shared else ()
    return ValidationReport(reports, tuple(load_errors), shared, roles is not None)
