"""A workspace as the workflow engine sees it: configuration, definitions, roles, plugin checks and units.

``Workspace`` is the library entry point the CLI is built on. It loads each
source once (the receipt, the discovered definitions, roles and plugin checks
are cached and reused by every call), resolves a unit directory to its anchor,
binding and workflow, and evaluates units with the project's policies
(approvals, stage switches, lint, Git, drift). Every failure is an
``AdvisoryError`` with a stable code: a ``WorkflowError``, or a ``devkit.core``
error such as ``RECEIPT_INVALID``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from devkit.core.project import find_project_root
from devkit.core.receipt import Receipt, load_receipt
from devkit.workflow.definition.checks import DECLARABLE, Registry
from devkit.workflow.definition.definition import WorkflowDocument, schema_hash
from devkit.workflow.definition.discovery import (
    definition_path,
    discover_definitions,
    load_definition_dir,
    load_definition_file,
    select_definition,
)
from devkit.workflow.definition.validation import ValidationReport, validate_definition, validate_definitions
from devkit.workflow.errors import (
    AnchorAmbiguousError,
    AnchorMismatchError,
    DefinitionProblem,
    DriftError,
    GivenInvalidError,
    PluginError,
    UnitNotFoundError,
    WorkflowError,
    WorkflowInvalidError,
    WorkflowNotSelectedError,
)
from devkit.workflow.evaluation.evaluate import LintFunc, Options, evaluate_definition
from devkit.workflow.evaluation.git import is_ancestor
from devkit.workflow.evaluation.lint import lint_with_rules
from devkit.workflow.evaluation.primitives import AncestorFunc
from devkit.workflow.evaluation.results import UnitEvaluation
from devkit.workflow.project.config import WorkflowConfig, load_workflow_config
from devkit.workflow.project.layout import LayoutSpec, TemplateLayout
from devkit.workflow.project.plugins import BaseCheck, load_plugin_checks
from devkit.workflow.project.roles import discover_roles
from devkit.workflow.unit.binding import Binding, read_anchor, write_binding


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

    @property
    def drift(self) -> bool:
        """Whether the binding names this definition with another schema hash."""
        binding = self.binding
        if binding is None or not binding.bound or binding.workflow != self.doc.id:
            return False
        return binding.hash != schema_hash(self.doc)

    def to_dict(self) -> dict[str, Any]:
        data = self.doc.to_dict()
        data["approvals"] = dict(self.approvals)
        data["stages_off"] = list(self.stages_off)
        data["anchor"] = self.anchor
        if self.binding is not None:
            data["binding"] = {**self.binding.to_dict(), "drift": self.drift}
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
        self._plugins: list[BaseCheck] | None = None
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

    def plugins(self) -> list[BaseCheck]:
        """Plugin checks from receipt ``workflow-check`` assets and ``checks_dir``.

        A file that cannot be loaded raises ``PluginError``
        (``WORKFLOW_CHECK_LOAD_FAILED``); several are reported in one error.
        """
        if self._plugins is None:
            loaded, errors = load_plugin_checks(self.root, self.config.checks_dir, self.receipt)
            if len(errors) == 1:
                raise errors[0]
            if errors:
                fixes = list(dict.fromkeys(e.fix for e in errors if e.fix))
                raise PluginError(
                    "plugin checks could not be loaded",
                    *errors,
                    fix="; ".join(fixes) or None,
                    target_files=list(dict.fromkeys(t for e in errors for t in e.target_files)),
                )
            self._plugins = loaded
        return self._plugins

    def registry(self, doc: WorkflowDocument) -> Registry:
        return Registry.build(self.anchor_for(doc), doc.declared_checks, self.plugins())

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
        """Validate against the project anchor, known ids, the role vocabulary and the loaded plugin checks."""
        ids = set(known) if known is not None else self.known_ids() | {doc.id}
        return validate_definition(doc, self.config.anchor, ids, self.roles(), self.plugins())

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
        return validate_definitions(
            docs,
            errors,
            anchor=self.config.anchor,
            known_ids=self.known_ids(),
            roles=self.roles(),
            plugins=self.plugins(),
            compare_shared=not paths,
        )

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

    def locate_anchor(self, unit_dir: Path) -> str:
        """Which candidate anchor file identifies ``unit_dir``; exactly one must exist."""
        present = [a for a in self.candidate_anchors() if (unit_dir / a).is_file()]
        if len(present) == 1:
            return present[0]
        if not present:
            tried = ", ".join(self.candidate_anchors())
            raise UnitNotFoundError(f"no anchor file ({tried}) found in {self.rel(unit_dir)}")
        raise AnchorAmbiguousError(f"{self.rel(unit_dir)} contains several anchor files: {', '.join(present)}")

    def _binding(self, unit_dir: Path, anchor: str) -> Binding:
        return read_anchor(unit_dir / anchor, self.rel(unit_dir / anchor)).binding

    def resolve_unit(self, unit: str | Path, workflow: str | None = None) -> UnitRef:
        """The unit directory, its anchor file, its binding and the workflow to evaluate against.

        With ``workflow`` the named definition decides the anchor; otherwise
        the anchor present in the directory is found first and the binding (or
        the project default) selects the workflow, whose anchor must match.
        """
        unit_dir = self.unit_path(unit)
        if workflow is not None:
            doc = self.definition(workflow)
            anchor = self.anchor_for(doc)
            if not (unit_dir / anchor).is_file():
                raise UnitNotFoundError(f"{anchor} not found in {self.rel(unit_dir)}")
            return UnitRef(unit_dir, anchor, self._binding(unit_dir, anchor), doc, self.rel(unit_dir))
        anchor = self.locate_anchor(unit_dir)
        binding = self._binding(unit_dir, anchor)
        doc = self.definition(None, binding)
        expected = self.anchor_for(doc)
        if expected != anchor:
            raise AnchorMismatchError(
                f"unit {self.rel(unit_dir)} is identified by {anchor} but workflow {doc.id} declares anchor {expected}",
                target_files=[self.rel(unit_dir / anchor)],
                fix=f"Rename the anchor to {expected} (and move the unit into the workflow's layout) before binding, or pass --workflow for a definition whose anchor is {anchor}",
            )
        return UnitRef(unit_dir, anchor, binding, doc, self.rel(unit_dir))

    def bind_unit(self, unit: str | Path, workflow: str | None = None) -> UnitRef:
        """Record the workflow ``unit`` follows and the hash of its stage schema; returns the rebound unit.

        ``workflow`` defaults to the current binding, else ``[workflow].default``.
        The handoff history is kept.
        """
        ref = self.resolve_unit(unit, workflow)
        binding = Binding(ref.doc.id, schema_hash(ref.doc), ref.binding.history)
        write_binding(ref.anchor_path, Binding(binding.workflow, binding.hash))
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
            plugins=tuple(self.plugins()),
            roles=dict(self.roles() or {}),
        )

    def evaluate_unit(
        self,
        unit: UnitRef,
        *,
        given: Sequence[str] = (),
        lint: bool = True,
        enforce_drift: bool = True,
    ) -> UnitEvaluation:
        """Evaluate ``unit`` with the project's policies; never writes a file.

        Raises ``DriftError`` (``WORKFLOW_DRIFT``) when the bound definition
        changed and a stage is still current, unless ``enforce_drift`` is off.
        Approvals for stages after the current one (the unit went back) are
        listed in ``UnitEvaluation.stale_approvals`` and keep counting until
        ``return_to`` voids them.
        """
        self.check_given(unit.doc, given)
        result = evaluate_definition(unit.doc, self.options(unit, given=given, lint=lint))
        if enforce_drift and result.blocked_by_drift:
            assert result.drift is not None
            raise DriftError(
                "the bound stage schema changed under in-flight work",
                f"recorded={result.drift.recorded}",
                f"current={result.drift.current}",
                target_files=[self.rel(unit.anchor_path)],
                fix=f"Review the change to {unit.doc.id}, then run `devkit workflow bind --unit {unit.rel}` to accept it",
            )
        return result


__all__ = ["DefinitionDescription", "UnitRef", "Workspace"]
