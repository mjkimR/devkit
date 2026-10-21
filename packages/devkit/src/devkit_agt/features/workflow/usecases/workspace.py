"""A workspace as the workflow engine sees it: configuration, definitions, roles and units.

``Workspace`` is the library entry point the CLI is built on. It loads each
source once (the receipt, the discovered definitions and roles
are cached and reused by every call), resolves a unit directory to its anchor,
binding and workflow, and evaluates units with the project's policies
(approvals, stage switches, lint, Git). Every failure is an
``AdvisoryError`` with a stable code: a ``WorkflowError``, or a ``devkit.core``
error such as ``RECEIPT_INVALID``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from devkit_dist.features.project.repositories.project import find_project_root
from devkit_dist.features.project.repositories.receipt import Receipt, load_receipt

from devkit_agt.features.workflow.models.binding import Binding
from devkit_agt.features.workflow.models.checks import DECLARABLE, Registry
from devkit_agt.features.workflow.models.definition import WorkflowDocument
from devkit_agt.features.workflow.models.errors import (
    AnchorAmbiguousError,
    AnchorMismatchError,
    DefinitionProblem,
    GivenInvalidError,
    UnitNotFoundError,
    WorkflowError,
    WorkflowInvalidError,
    WorkflowNotBindableError,
    WorkflowNotFoundError,
    WorkflowNotSelectedError,
)
from devkit_agt.features.workflow.models.layout import LayoutSpec, TemplateLayout
from devkit_agt.features.workflow.models.results import UnitEvaluation
from devkit_agt.features.workflow.repositories.definitions import (
    definition_path,
    discover_definitions,
    load_definition_dir,
    load_definition_file,
    select_definition,
)
from devkit_agt.features.workflow.repositories.git import is_ancestor
from devkit_agt.features.workflow.repositories.project.config import WorkflowConfig, load_workflow_config
from devkit_agt.features.workflow.repositories.project.roles import discover_roles
from devkit_agt.features.workflow.repositories.unit.binding import read_anchor, write_binding
from devkit_agt.features.workflow.services.definition.validation import (
    ValidationReport,
    validate_definition,
    validate_definitions,
)
from devkit_agt.features.workflow.services.evaluation.primitives import AncestorFunc
from devkit_agt.features.workflow.usecases.evaluate import LintFunc, Options, evaluate_definition
from devkit_agt.features.workflow.usecases.lint import lint_with_rules


@dataclass(frozen=True)
class UnitRef:
    """A resolved work unit: its directory, anchor file, binding and the workflow it is evaluated against."""

    dir: Path  # absolute
    anchor: str
    binding: Binding
    doc: WorkflowDocument
    rel: str  # workspace-relative when inside the workspace

    @property
    def anchor_path(self) -> Path:
        return self.dir / self.anchor


@dataclass(frozen=True)
class UnitScope:
    """A unit's anchor, binding and the id of the workflow it follows, read without validating that definition."""

    dir: Path  # absolute
    anchor: str
    binding: Binding
    workflow: str  # the binding's workflow, else ``[workflow].default``
    rel: str  # workspace-relative when inside the workspace


@dataclass(frozen=True)
class DefinitionDescription:
    """A definition with its problems, effective policies and anchor, and optionally a unit's binding (``show``)."""

    doc: WorkflowDocument
    errors: tuple[DefinitionProblem, ...]
    approvals: dict[str, str]
    stages_off: tuple[str, ...]
    anchor: str
    binding: Binding | None = None

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        data = self.doc.to_dict()
        data["approvals"] = dict(self.approvals)
        data["stages_off"] = list(self.stages_off)
        data["anchor"] = self.anchor
        if self.binding is not None:
            data["binding"] = self.binding.to_dict()
        data["ok"] = self.ok
        data["errors"] = [p.to_dict() for p in self.errors]
        return data


class Workspace:
    """The workflow view of one project root (default: the project containing the current directory)."""

    def __init__(
        self,
        root: Path | str | None = None,
        *,
        lint: LintFunc | None = lint_with_rules,
        ancestor: AncestorFunc | None = is_ancestor,
    ) -> None:
        self.root = (Path(root) if root is not None else find_project_root(Path.cwd())).resolve()
        self.config: WorkflowConfig = load_workflow_config(self.root)
        self.lint = lint
        self.ancestor = ancestor
        self._receipt_loaded = False
        self._receipt: Receipt | None = None
        self._docs: list[WorkflowDocument] | None = None
        self._discovery_errors: list[WorkflowError] = []
        self._roles_loaded = False
        self._roles: dict[str, str] | None = None
        self._layouts: dict[LayoutSpec, TemplateLayout] = {}

    # -- paths ---------------------------------------------------------------

    @property
    def layout(self) -> TemplateLayout:
        return self.config.layout

    @property
    def definitions_dir(self) -> Path:
        return self.root / self.config.definitions_dir

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def unit_path(self, unit: str | Path) -> Path:
        path = Path(unit)
        return (path if path.is_absolute() else self.root / path).resolve()

    # -- sources -------------------------------------------------------------

    @property
    def receipt(self) -> Receipt | None:
        """The installation receipt, ``None`` when absent; a malformed one raises ``ReceiptError`` (``RECEIPT_INVALID``)."""
        if not self._receipt_loaded:
            self._receipt = load_receipt(self.root)
            self._receipt_loaded = True
        return self._receipt

    def definitions(self) -> list[WorkflowDocument]:
        """Every discovered definition (project definitions shadow synchronized ones), loaded once."""
        if self._docs is None:
            self._docs, self._discovery_errors = discover_definitions(self.root, self.definitions_dir, self.receipt)
        return self._docs

    @property
    def discovery_errors(self) -> list[WorkflowError]:
        """Definitions that could not be loaded (``DefinitionError``) or are missing (``WorkflowAssetMissingError``)."""
        self.definitions()
        return list(self._discovery_errors)

    def known_ids(self) -> set[str]:
        return {d.id for d in self.definitions()}

    def roles(self) -> dict[str, str] | None:
        """The project's subagent vocabulary; ``None`` when no receipt and no roles_dir exist."""
        if not self._roles_loaded:
            self._roles = discover_roles(self.root, self.config.roles_dir, self.receipt)
            self._roles_loaded = True
        return self._roles

    def registry(self, doc: WorkflowDocument) -> Registry:
        return Registry.build(self.anchor_for(doc), doc.declared_checks)

    # -- definitions -----------------------------------------------------------

    def layout_for(self, doc: WorkflowDocument) -> TemplateLayout:
        """The project layout with the keys the definition overrides (built once per distinct layout)."""
        if doc.layout is None:
            return self.layout
        if doc.layout not in self._layouts:
            self._layouts[doc.layout] = doc.layout.apply(self.layout)
        return self._layouts[doc.layout]

    def anchor_for(self, doc: WorkflowDocument) -> str:
        return doc.anchor(self.config.anchor)

    def validate_definition(self, doc: WorkflowDocument, known: Iterable[str] | None = None) -> list[DefinitionProblem]:
        """Validate against the project anchor, known ids and the role vocabulary."""
        ids = set(known) if known is not None else self.known_ids() | {doc.id}
        return validate_definition(doc, self.config.anchor, ids, self.roles())

    def load_definition(self, ref: str) -> WorkflowDocument:
        """The definition ``ref`` names (an id, or a path relative to the root), not validated.

        Ids are looked up in the cached discovered definitions. An unknown id
        or a missing file raises ``WorkflowNotFoundError``; an unreadable file
        or an id defined twice raises ``DefinitionError``.
        """
        fix = (
            f"Add a definition with id {ref!r} under {self.config.definitions_dir}, "
            "sync a bundle that ships it, or pass --workflow <path>"
        )
        path = definition_path(ref, self.root)
        if path is not None:
            return load_definition_file(path, ref, fix)
        where = f"{self.config.definitions_dir} or the devkit installation receipt"
        return select_definition(self.definitions(), ref, self.discovery_errors, where, fix)

    def definition(self, ref: str | None = None, binding: Binding | None = None) -> WorkflowDocument:
        """The validated workflow ``ref`` names, else the binding's, else the configured default."""
        chosen = ref or (binding.workflow if binding and binding.workflow else None) or self.config.default
        if not chosen:
            raise WorkflowNotSelectedError("no workflow selected")
        doc = self.load_definition(chosen)
        problems = self.validate_definition(doc)
        if problems:
            raise WorkflowInvalidError(
                f"workflow {doc.id} is invalid",
                *problems,
                target_files=[self.rel(doc.path)] if doc.path else (),
                fix=f"Run `devkit workflow validate` and fix every problem in {doc.id}",
            )
        return doc

    def require_bindable(self, doc: WorkflowDocument, ref: str | None) -> None:
        """Refuse to bind ``doc`` when ``ref`` names it by a path later lookups by id would not find.

        A binding records only the definition's id, and every unit command
        looks the id up among the discovered definitions. A ``ref`` that is a
        path (``definition_path``) must therefore be the file discovered for
        that id; any other file raises ``WorkflowNotBindableError``
        (``WORKFLOW_NOT_BINDABLE``). An id ``ref``, or none, always passes.
        """
        if ref is None or definition_path(ref, self.root) is None:
            return
        try:
            found = select_definition(self.definitions(), doc.id, (), "").path
        except WorkflowNotFoundError:
            found = None
        if found is not None and doc.path is not None and found.resolve() == doc.path.resolve():
            return
        where = self.config.definitions_dir
        if found is None:
            raise WorkflowNotBindableError(
                f"{ref} defines workflow {doc.id}, which is not a discovered definition; a binding records only the id",
                fix=f"Move {ref} into {where} (or sync the bundle that ships it), then pass --workflow {doc.id}",
            )
        raise WorkflowNotBindableError(
            f"{ref} defines workflow {doc.id}, but that id resolves to {self.rel(found)}; a binding records only the id",
            fix=f"Pass --workflow {doc.id} to bind {self.rel(found)}, or give {ref} its own id and move it into {where}",
        )

    def validate_definitions(self, paths: Sequence[Path] = ()) -> ValidationReport:
        """Validate the given definition files or directories; none means every discovered definition.

        Only a whole-workspace run compares stages shared across definitions.
        """
        docs: list[WorkflowDocument] = []
        errors: list[WorkflowError] = []
        if not paths:
            docs, errors = list(self.definitions()), self.discovery_errors
        for target in paths:
            if target.is_dir():
                loaded, load_errors = load_definition_dir(target)
                docs.extend(loaded)
                errors.extend(load_errors)
                continue
            try:
                docs.append(load_definition_file(target, self.rel(target)))
            except WorkflowError as exc:
                errors.append(exc)
        report = validate_definitions(
            docs,
            errors,
            anchor=self.config.anchor,
            known_ids=self.known_ids(),
            roles=self.roles(),
            compare_shared=not paths,
        )
        return replace(report, roles_dir=self.config.roles_dir)

    def describe(self, doc: WorkflowDocument, binding: Binding | None = None) -> DefinitionDescription:
        """The definition with its problems, effective policies and anchor (what ``show`` reports)."""
        return DefinitionDescription(
            doc=doc,
            errors=tuple(self.validate_definition(doc)),
            approvals={s.gate: self.config.policy(s.gate) for s in doc.stages if s.gate},
            stages_off=tuple(s.id for s in doc.stages if self.config.stage_policy(s.id) == "off"),
            anchor=self.anchor_for(doc),
            binding=binding,
        )

    # -- units ---------------------------------------------------------------

    def candidate_anchors(self) -> list[str]:
        """The project anchor first, then every distinct anchor a discovered definition declares."""
        anchors = [self.config.anchor]
        for doc in self.definitions():
            anchor = self.anchor_for(doc)
            if anchor not in anchors:
                anchors.append(anchor)
        return anchors

    def present_anchors(self, unit_dir: Path) -> list[str]:
        """The candidate anchor files present in ``unit_dir``; ``UnitNotFoundError`` when there is none."""
        present = [a for a in self.candidate_anchors() if (unit_dir / a).is_file()]
        if not present:
            tried = ", ".join(self.candidate_anchors())
            raise UnitNotFoundError(f"no anchor file ({tried}) found in {self.rel(unit_dir)}")
        return present

    def locate_anchor(self, unit_dir: Path, anchor: str | None = None) -> str:
        """Which candidate anchor file identifies ``unit_dir``.

        ``anchor`` names it (``--anchor``) and must be a candidate present in
        the directory; otherwise exactly one candidate must be present, and
        several are ``AnchorAmbiguousError`` (``ANCHOR_AMBIGUOUS``).
        """
        candidates = self.candidate_anchors()
        if anchor is not None:
            if anchor not in candidates:
                raise UnitNotFoundError(
                    f"{anchor} is not the anchor of the project or of any workflow",
                    fix=f"Pass --anchor with one of: {', '.join(candidates)}",
                )
            if not (unit_dir / anchor).is_file():
                raise UnitNotFoundError(f"{anchor} not found in {self.rel(unit_dir)}")
            return anchor
        present = self.present_anchors(unit_dir)
        if len(present) > 1:
            raise AnchorAmbiguousError(
                f"{self.rel(unit_dir)} contains several anchor files: {', '.join(present)}",
                fix=f"Pass --anchor <file> with one of {', '.join(present)} to name the file that identifies the unit",
            )
        return present[0]

    def _binding(self, unit_dir: Path, anchor: str) -> Binding:
        return read_anchor(unit_dir / anchor, self.rel(unit_dir / anchor)).binding

    def resolve_unit(self, unit: str | Path, workflow: str | None = None, *, anchor: str | None = None) -> UnitRef:
        """The unit directory, its anchor file, its binding and the workflow to evaluate against.

        With ``workflow`` the named definition decides the anchor (``anchor``,
        when given, must be the same file); otherwise the anchor is located
        first (``locate_anchor``) and the binding (or the project default)
        selects the workflow, whose anchor must match.
        """
        unit_dir = self.unit_path(unit)
        if workflow is not None:
            doc = self.definition(workflow)
            expected = self.anchor_for(doc)
            if anchor is not None and anchor != expected:
                raise AnchorMismatchError(
                    f"--anchor {anchor} names another file than workflow {doc.id}'s anchor {expected}",
                    fix="Drop --anchor: --workflow selects the anchor",
                )
            if not (unit_dir / expected).is_file():
                raise UnitNotFoundError(f"{expected} not found in {self.rel(unit_dir)}")
            return UnitRef(unit_dir, expected, self._binding(unit_dir, expected), doc, self.rel(unit_dir))
        found = self.locate_anchor(unit_dir, anchor)
        binding = self._binding(unit_dir, found)
        self._require_selection(unit_dir, binding)
        doc = self.definition(None, binding)
        expected = self.anchor_for(doc)
        if expected != found:
            unit_rel = self.rel(unit_dir)
            raise AnchorMismatchError(
                f"unit {unit_rel} is identified by {found} but workflow {doc.id} declares anchor {expected}",
                target_files=[self.rel(unit_dir / found)],
                fix=(
                    f"Rename the anchor to {expected} (and move the unit into the workflow's layout), or rebind it "
                    f"with `devkit workflow bind --unit {unit_rel} --workflow <id>` naming a workflow whose anchor is {found}"
                ),
            )
        return UnitRef(unit_dir, found, binding, doc, self.rel(unit_dir))

    def unit_scope(self, unit: str | Path, *, anchor: str | None = None) -> UnitScope:
        """The unit's anchor (``locate_anchor``), binding and workflow id, without loading the definition.

        Enough to scope what is recorded in the unit (the envelope authoring
        commands), so a missing or invalid definition does not stop it. An
        unbound unit follows ``[workflow].default``; without one it is
        ``WorkflowNotSelectedError``. A default that is a definition path is
        read (unvalidated, as ``load_definition`` does) for its id, the scope
        evaluation counts envelopes in; a missing or unreadable file raises
        as ``load_definition`` does.
        """
        unit_dir = self.unit_path(unit)
        found = self.locate_anchor(unit_dir, anchor)
        binding = self._binding(unit_dir, found)
        self._require_selection(unit_dir, binding)
        workflow = binding.workflow or self.config.default or ""
        if not binding.workflow and definition_path(workflow, self.root) is not None:
            workflow = self.load_definition(workflow).id
        return UnitScope(unit_dir, found, binding, workflow, self.rel(unit_dir))

    def _require_selection(self, unit_dir: Path, binding: Binding) -> None:
        """Raise ``WorkflowNotSelectedError`` for an unbound unit when ``[workflow].default`` is unset."""
        if not binding.workflow and not self.config.default:
            raise WorkflowNotSelectedError(
                f"unit {self.rel(unit_dir)} is not bound and [workflow].default is unset",
                fix=(
                    f"Bind the unit with `devkit workflow bind --unit {self.rel(unit_dir)} --workflow <id>`, "
                    "or set [workflow].default in .devkit/config.toml"
                ),
            )

    def describe_unit(self, unit: str | Path, *, anchor: str | None = None) -> DefinitionDescription:
        """What ``show --unit`` reports: the definition the unit is bound to (else the default) with its binding.

        The definition is loaded unvalidated, so its problems are reported
        under ``errors`` instead of raised.
        """
        unit_dir = self.unit_path(unit)
        binding = self._binding(unit_dir, self.locate_anchor(unit_dir, anchor))
        self._require_selection(unit_dir, binding)
        return self.describe(self.load_definition(binding.workflow or self.config.default or ""), binding)

    def bind_unit(self, unit: str | Path, workflow: str | None = None, *, anchor: str | None = None) -> UnitRef:
        """Record the workflow ``unit`` follows; returns the rebound unit.

        ``workflow`` defaults to the current binding, else ``[workflow].default``;
        ``anchor`` is as for ``resolve_unit``. The handoff history is kept. A
        definition path outside the discovered definitions is refused
        (``require_bindable``) before anything is written.
        """
        ref = self.resolve_unit(unit, workflow, anchor=anchor)
        self.require_bindable(ref.doc, workflow)
        binding = Binding(ref.doc.id, ref.binding.history)
        write_binding(ref.anchor_path, Binding(binding.workflow))
        return replace(ref, binding=binding)

    def check_given(self, doc: WorkflowDocument, given: Iterable[str]) -> None:
        """``--given`` names must be gates of ``doc`` or registered runner/human checks."""
        registry = self.registry(doc)
        gates = doc.gates
        for name in given:
            check = registry.lookup(name)
            if name not in gates and (check is None or check.class_ not in DECLARABLE):
                raise GivenInvalidError(
                    f"--given {name!r} is not a gate of {doc.id} nor a registered runner or human check",
                    fix=f"Use a gate name ({', '.join(sorted(gates)) or 'none'}) or a runner/human check from `devkit workflow checks`",
                )

    def options(self, unit: UnitRef, *, given: Sequence[str] = (), lint: bool = True) -> Options:
        return Options(
            workspace_root=self.root,
            unit_dir=unit.dir,
            anchor=unit.anchor,
            approvals=dict(self.config.approvals),
            stages=dict(self.config.stages),
            given=tuple(given),
            lint=self.lint,
            skip_lint=not lint,
            ancestor=self.ancestor,
            roles=dict(self.roles() or {}),
        )

    def evaluate_unit(
        self,
        unit: UnitRef,
        *,
        given: Sequence[str] = (),
        lint: bool = True,
    ) -> UnitEvaluation:
        """Evaluate ``unit`` with the project's policies; never writes a file.

        Approvals for stages after the current one (the unit went back) are
        listed in ``UnitEvaluation.stale_approvals`` and keep counting until
        ``ReturnToStageUseCase`` voids them.
        """
        self.check_given(unit.doc, given)
        result = evaluate_definition(unit.doc, self.options(unit, given=given, lint=lint))
        return result


__all__ = ["DefinitionDescription", "UnitRef", "UnitScope", "Workspace"]
