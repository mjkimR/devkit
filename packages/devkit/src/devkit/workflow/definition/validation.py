"""Validation of workflow definitions, one at a time and across a workspace.

Problems are collected, never raised: ``DefinitionProblem`` (and its
``CheckReferenceProblem`` and ``RoleUnknownProblem`` subclasses) for one
definition, ``SharedStageMismatchError`` across definitions.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.workflow.definition.checks import DECLARABLE, Check, CheckClass, Registry
from devkit.workflow.definition.definition import (
    HANDOFF_GATE,
    ISOLATIONS,
    SCHEMA_VERSION,
    StageDefinition,
    WorkflowDocument,
)
from devkit.workflow.definition.ids import IDENT_HINT, is_ident
from devkit.workflow.errors import (
    CheckError,
    CheckReferenceProblem,
    DefinitionProblem,
    OptionalStageWarning,
    RolesUncheckedNotice,
    RoleUnknownProblem,
    SharedStageMismatchError,
    WorkflowError,
)
from devkit.workflow.project.roles import is_builtin_role

SHARED_STAGE_FIELDS = ("exit", "gate", "role", "isolation", "skills", "artifacts")
# An unmet optional stage is passed over and never becomes current, so nothing asks for its approvals.
_UNASKED = (
    "workflow {workflow}: optional stage {stage!r} has {what}, which is never requested because the stage never "
    "becomes current; only {satisfied} satisfy it"
)


def _where(stage: str, field: str) -> str:
    return f"{stage}.{field}" if stage else field


def _problem(stage: str, field: str, message: str) -> DefinitionProblem:
    return DefinitionProblem(message, where=_where(stage, field))


def _check_problem(stage: str, field: str, exc: CheckError) -> CheckReferenceProblem:
    return CheckReferenceProblem(exc.message, where=_where(stage, field))


def _registry(anchor: str, doc: WorkflowDocument) -> tuple[Registry, list[DefinitionProblem]]:
    """The definition's registry; each declared check that is rejected is reported and left out, the rest kept."""
    try:
        return Registry.build(anchor, doc.declared_checks), []
    except CheckError as exc:
        problems: list[DefinitionProblem] = [_check_problem("", "checks", exc)]
    kept: list[Check] = []
    for check in doc.declared_checks:
        try:
            Registry.build(anchor, (*kept, check))
        except CheckError as exc:
            if all(p.message != exc.message for p in problems):
                problems.append(_check_problem("", "checks", exc))
            continue
        kept.append(check)
    return Registry.build(anchor, tuple(kept)), problems


def validate_definition(
    doc: WorkflowDocument,
    anchor: str,
    known_ids: Iterable[str] | None = None,
    roles: Mapping[str, str] | None = None,
) -> list[DefinitionProblem]:
    """Every problem in the document; an empty list means it is usable.

    ``anchor`` is the project default; a definition that declares its own
    anchor is validated against that one. ``known_ids`` are the workflow ids
    that exist in the workspace; when given, a ``next`` candidate naming
    another id is reported. ``roles`` is the project's subagent vocabulary
    (``role -> contract path``); when given, a stage role outside it is
    reported, and ``None`` skips that check.
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
    registry, registry_problems = _registry(doc.anchor(anchor), doc)
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


def definition_warnings(doc: WorkflowDocument, anchor: str) -> list[OptionalStageWarning]:
    """What makes the document harder to use without making it invalid: ``OptionalStageWarning`` for each gate or
    ``human`` exit check of an optional stage, which nothing requests. Unresolvable checks are left to
    ``validate_definition``.
    """
    registry, _ = _registry(doc.anchor(anchor), doc)
    warnings: list[OptionalStageWarning] = []

    def warn(stage: StageDefinition, field: str, what: str, satisfied: str) -> None:
        message = _UNASKED.format(workflow=doc.id, stage=stage.id, what=what, satisfied=satisfied)
        fix = f"Drop optional from stage {stage.id!r}, or move the approval to a stage that is not optional"
        warnings.append(OptionalStageWarning(message, where=_where(stage.id, field), fix=fix))

    for s in doc.stages:
        if not s.optional:
            continue
        if s.gate is not None:
            satisfied = f"approvals.{s.gate}=auto, --given {s.gate} or a decision record written by a host"
            warn(s, "human_gate", f"gate {s.gate!r}", satisfied)
        for ref in s.exit:
            try:
                _, check = registry.resolve_name(ref)
            except CheckError:
                continue
            if check.class_ == CheckClass.HUMAN:
                warn(s, "exit", f"human check {ref!r}", f"--given {ref} or a decision record written by a host")
    return warnings


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
                _, check = registry.resolve_name(ref)
            except CheckError as exc:
                problems.append(_check_problem("", f"{where}.when", exc))
                continue
            # Nothing can satisfy a runner or human check while a handoff is chosen.
            if check.class_ in DECLARABLE:
                problems.append(
                    CheckReferenceProblem(
                        f"{check.class_.value} check {ref!r} cannot decide a handoff; "
                        "`when` takes checks the engine evaluates",
                        where=_where("", f"{where}.when"),
                    )
                )
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
    warnings: tuple[OptionalStageWarning, ...] = ()  # reported as notices; they never make it invalid

    @property
    def ok(self) -> bool:
        return not self.problems

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        return {
            "id": self.doc.id,
            "path": _display_path(self.doc.path, root),
            "ok": self.ok,
            "errors": [p.to_dict() for p in self.problems],
        }


@dataclass(frozen=True)
class ValidationReport:
    """Every definition checked, the files that could not be loaded and cross-definition problems."""

    definitions: tuple[DefinitionReport, ...] = ()
    load_errors: tuple[WorkflowError, ...] = ()
    shared: tuple[SharedStageMismatchError, ...] = ()
    roles_checked: bool = True
    roles_dir: str | None = None  # the project's ``[workflow] roles_dir``, named by the roles notice

    @property
    def errors(self) -> tuple[WorkflowError, ...]:
        """Every problem: load errors, shared-stage mismatches and each definition's problems."""
        return (*self.load_errors, *self.shared, *(p for r in self.definitions for p in r.problems))

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def notices(self) -> tuple[WorkflowError, ...]:
        """Each definition's warnings (``WORKFLOW_OPTIONAL_STAGE_UNASKED``), then ``WORKFLOW_ROLES_UNCHECKED`` when
        stage roles could not be checked; warnings and notices never fail validation (except a warning under
        ``--strict``)."""
        warnings = tuple(w for r in self.definitions for w in r.warnings)
        if self.roles_checked:
            return warnings
        missing = self.roles_dir or "[workflow] roles_dir directory"
        return (
            *warnings,
            RolesUncheckedNotice(f"stage roles were not checked: no installation receipt and no {missing}"),
        )

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        """``validate --format json``: definitions with their own ``errors``, load and shared-stage ``errors``,
        and ``notices``."""
        return {
            "ok": self.ok,
            "roles_checked": self.roles_checked,
            "definitions": [r.to_dict(root) for r in self.definitions],
            "errors": [e.to_dict() for e in (*self.load_errors, *self.shared)],
            "notices": [n.to_dict() for n in self.notices],
        }


def validate_definitions(
    docs: Sequence[WorkflowDocument],
    load_errors: Sequence[WorkflowError],
    *,
    anchor: str,
    known_ids: Iterable[str],
    roles: Mapping[str, str] | None,
    compare_shared: bool = True,
) -> ValidationReport:
    """Validate ``docs`` together: each one, and (with ``compare_shared``) their shared stages."""
    known = set(known_ids) | {d.id for d in docs}
    reports = tuple(
        DefinitionReport(
            d,
            tuple(validate_definition(d, anchor, known, roles)),
            tuple(definition_warnings(d, anchor)),
        )
        for d in docs
    )
    shared = tuple(compare_shared_stages(docs)) if compare_shared else ()
    return ValidationReport(reports, tuple(load_errors), shared, roles is not None)
