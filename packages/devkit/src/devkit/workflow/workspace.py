"""A workspace as the workflow engine sees it: configuration, definitions, roles, plugin checks and units.

``Workspace`` is the library entry point the CLI is built on. It loads each
source once, resolves a unit directory to its anchor, binding and workflow,
and evaluates units with the project's policies (approvals, stage switches,
lint, Git, drift). Every failure is a ``WorkflowError`` with a stable code.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.core.errors import FrontmatterError, ReceiptError
from devkit.core.project import find_project_root
from devkit.core.receipt import Receipt, load_receipt
from devkit.workflow.binding import Binding, read_binding
from devkit.workflow.checks import DECLARABLE, Registry
from devkit.workflow.config import CONFIG_PATH, ConfigError, WorkflowConfig, load_workflow_config
from devkit.workflow.decisions import RETURN_PREFIX, Decision, load_decisions, new_decision, write_decision
from devkit.workflow.definition import DefinitionError, Problem, WorkflowDocument, schema_hash
from devkit.workflow.discovery import discover, load_all, resolve
from devkit.workflow.errors import DriftError, input_error, maintenance_error
from devkit.workflow.evaluate import LintFunc, Options, evaluate
from devkit.workflow.git import is_ancestor
from devkit.workflow.layout import TemplateLayout
from devkit.workflow.lint import rules_lint
from devkit.workflow.plugins import BaseCheck, load_plugin_checks
from devkit.workflow.primitives import AncestorFunc
from devkit.workflow.results import Result
from devkit.workflow.roles import discover_roles
from devkit.workflow.validation import ValidationReport, validate, validate_workspace

UNIT_FIX = "Pass an existing unit directory (`devkit workflow list`) or create one with `devkit workflow new <slug>`"
RETURN_BY = "devkit"


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


class Workspace:
    """The workflow view of one project root (default: the project containing the current directory)."""

    def __init__(
        self,
        root: Path | str | None = None,
        *,
        lint: LintFunc | None = rules_lint,
        ancestor: AncestorFunc | None = is_ancestor,
    ) -> None:
        self.root = (Path(root) if root is not None else find_project_root(Path.cwd())).resolve()
        try:
            self.config: WorkflowConfig = load_workflow_config(self.root)
        except ConfigError as exc:
            raise input_error(
                str(exc),
                code="CONFIG_INVALID",
                target_files=[CONFIG_PATH],
                fix="Correct the [workflow] table in .devkit/config.toml",
            ) from exc
        self.lint = lint
        self.ancestor = ancestor
        self._receipt_loaded = False
        self._receipt: Receipt | None = None
        self._docs: list[WorkflowDocument] | None = None
        self._discovery_errors: list[str] = []
        self._roles_loaded = False
        self._roles: dict[str, str] | None = None
        self._plugins: list[BaseCheck] | None = None

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
        """The installation receipt, ``None`` when absent; a malformed one is ``RECEIPT_INVALID``."""
        if not self._receipt_loaded:
            try:
                self._receipt = load_receipt(self.root)
            except ReceiptError as exc:
                raise maintenance_error(
                    str(exc),
                    code="RECEIPT_INVALID",
                    fix="Run `devkit sync` to rewrite the installation receipt",
                ) from exc
            self._receipt_loaded = True
        return self._receipt

    def definitions(self) -> list[WorkflowDocument]:
        """Every discovered definition (project definitions shadow synchronized ones)."""
        if self._docs is None:
            self._docs, self._discovery_errors = discover(self.root, self.definitions_dir, self.receipt)
        return self._docs

    @property
    def discovery_errors(self) -> list[str]:
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
        """Plugin checks from receipt ``workflow-check`` assets and ``checks_dir``; a load failure is an error."""
        if self._plugins is None:
            loaded, errors = load_plugin_checks(self.root, self.config.checks_dir, self.receipt)
            if errors:
                raise maintenance_error(
                    "plugin checks could not be loaded",
                    *errors,
                    code="CHECK_LOAD_FAILED",
                    fix=f"Fix or remove the failing check file, or run `devkit sync` to restore a synchronized one ({self.config.checks_dir} holds project checks)",
                )
            self._plugins = loaded
        return self._plugins

    def registry(self, doc: WorkflowDocument) -> Registry:
        return Registry.build(self.anchor_for(doc), doc.declared_checks, self.plugins())

    # -- definitions -----------------------------------------------------------

    def layout_for(self, doc: WorkflowDocument) -> TemplateLayout:
        """The project layout with the keys the definition overrides."""
        return doc.layout.apply(self.layout) if doc.layout else self.layout

    def anchor_for(self, doc: WorkflowDocument) -> str:
        return doc.anchor(self.config.anchor)

    def validate(self, doc: WorkflowDocument, known: Iterable[str] | None = None) -> list[Problem]:
        """Validate against the project anchor, known ids, the role vocabulary and the loaded plugin checks."""
        ids = set(known) if known is not None else self.known_ids() | {doc.id}
        return validate(doc, self.config.anchor, ids, self.roles(), self.plugins())

    def load_definition(self, ref: str) -> WorkflowDocument:
        """The definition ``ref`` names (an id, or a path relative to the root), not validated."""
        try:
            return resolve(self.definitions_dir, ref, self.root)
        except DefinitionError as exc:
            raise input_error(
                str(exc),
                code="WORKFLOW_NOT_FOUND",
                fix=f"Add a definition with id {ref!r} under {self.config.definitions_dir}, sync a bundle that ships it, or pass --workflow <path>",
            ) from exc

    def definition(self, ref: str | None = None, binding: Binding | None = None) -> WorkflowDocument:
        """The validated workflow ``ref`` names, else the binding's, else the configured default."""
        chosen = ref or (binding.workflow if binding and binding.workflow else None) or self.config.default
        if not chosen:
            raise input_error(
                "no workflow selected",
                code="WORKFLOW_NOT_SELECTED",
                fix="Pass --workflow <id>, bind the unit, or set [workflow].default in .devkit/config.toml",
            )
        doc = self.load_definition(chosen)
        problems = self.validate(doc)
        if problems:
            raise input_error(
                f"workflow {doc.id} is invalid",
                *(str(p) for p in problems),
                code="WORKFLOW_INVALID",
                target_files=[self.rel(doc.path)] if doc.path else (),
                fix=f"Run `devkit workflow validate` and fix every problem in {doc.id}",
            )
        return doc

    def validate_definitions(self, paths: Sequence[Path] = ()) -> ValidationReport:
        """Validate the given definition files or directories; none means every discovered definition.

        Only a whole-workspace run compares stages shared across definitions.
        """
        docs: list[WorkflowDocument] = []
        errors: list[str] = []
        if not paths:
            docs, errors = list(self.definitions()), self.discovery_errors
        for target in paths:
            if target.is_dir():
                loaded, load_errors = load_all(target)
                docs.extend(loaded)
                errors.extend(load_errors)
                continue
            try:
                docs.append(resolve(self.definitions_dir, str(target), self.root))
            except DefinitionError as exc:
                errors.append(str(exc))
        return validate_workspace(
            docs,
            errors,
            anchor=self.config.anchor,
            known_ids=self.known_ids(),
            roles=self.roles(),
            plugins=self.plugins(),
            compare_shared=not paths,
        )

    def describe(self, doc: WorkflowDocument, binding: Binding | None = None) -> dict[str, Any]:
        """The definition as data with its problems, effective policies and anchor (``show --format json``)."""
        data = doc.to_dict()
        data["problems"] = [str(p) for p in self.validate(doc)]
        data["approvals"] = {s.gate: self.config.policy(s.gate) for s in doc.stages if s.gate}
        data["stages_off"] = [s.id for s in doc.stages if self.config.stage_policy(s.id) == "off"]
        data["anchor"] = self.anchor_for(doc)
        if binding is not None:
            drift = binding.bound and binding.workflow == doc.id and binding.hash != schema_hash(doc)
            data["binding"] = {**binding.to_dict(), "drift": drift}
        return data

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
            raise input_error(
                f"no anchor file ({tried}) found in {self.rel(unit_dir)}", code="UNIT_NOT_FOUND", fix=UNIT_FIX
            )
        raise input_error(
            f"{self.rel(unit_dir)} contains several anchor files: {', '.join(present)}",
            code="ANCHOR_AMBIGUOUS",
            fix="Pass --workflow <id> to name the workflow (and so the anchor) to evaluate against",
        )

    def read_binding(self, unit_dir: Path, anchor: str) -> Binding:
        try:
            return read_binding(unit_dir / anchor)
        except (FrontmatterError, OSError, UnicodeError) as exc:
            raise input_error(
                f"{anchor}: {exc}",
                code="ANCHOR_INVALID",
                target_files=[self.rel(unit_dir / anchor)],
                fix="Repair the anchor's YAML frontmatter",
            ) from exc

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
                raise input_error(f"{anchor} not found in {self.rel(unit_dir)}", code="UNIT_NOT_FOUND", fix=UNIT_FIX)
            return UnitRef(unit_dir, anchor, self.read_binding(unit_dir, anchor), doc, self.rel(unit_dir))
        anchor = self.locate_anchor(unit_dir)
        binding = self.read_binding(unit_dir, anchor)
        doc = self.definition(None, binding)
        expected = self.anchor_for(doc)
        if expected != anchor:
            raise input_error(
                f"unit {self.rel(unit_dir)} is identified by {anchor} but workflow {doc.id} declares anchor {expected}",
                code="ANCHOR_MISMATCH",
                target_files=[self.rel(unit_dir / anchor)],
                fix=f"Rename the anchor to {expected} (and move the unit into the workflow's layout) before binding, or pass --workflow for a definition whose anchor is {anchor}",
            )
        return UnitRef(unit_dir, anchor, binding, doc, self.rel(unit_dir))

    def check_given(self, doc: WorkflowDocument, given: Iterable[str]) -> None:
        """``--given`` names must be gates of ``doc`` or registered runner/human checks."""
        registry = self.registry(doc)
        gates = doc.gates
        for name in given:
            check = registry.lookup(name)
            if name not in gates and (check is None or check.class_ not in DECLARABLE):
                raise input_error(
                    f"--given {name!r} is not a gate of {doc.id} nor a registered runner or human check",
                    code="GIVEN_INVALID",
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
        record_returns: bool = True,
    ) -> Result:
        """Evaluate ``unit`` with the project's policies.

        Raises ``DriftError`` (``WORKFLOW_DRIFT``) when the bound definition
        changed and a stage is still current, unless ``enforce_drift`` is off.
        When approvals for stages after the current one are found (the unit
        went back), a ``return:<stage>`` decision record is written so those
        approvals must be given again (``record_returns``).
        """
        self.check_given(unit.doc, given)
        result = evaluate(unit.doc, self.options(unit, given=given, lint=lint))
        if enforce_drift and result.blocked_by_drift:
            assert result.drift is not None
            raise DriftError(
                "the bound stage schema changed under in-flight work",
                f"recorded={result.drift.recorded}",
                f"current={result.drift.current}",
                target_files=[self.rel(unit.anchor_path)],
                fix=f"Review the change to {unit.doc.id}, then run `devkit workflow bind --unit {unit.rel}` to accept it",
            )
        if record_returns and result.stale_approvals and result.stage is not None:
            stage = result.stage.id
            files = ", ".join(d.file for d in result.stale_approvals)
            record_return(
                unit,
                stage,
                note=f"the unit is back at stage {stage}; approvals for later stages ({files}) must be given again",
                by=RETURN_BY,
            )
        return result


def record_return(unit: UnitRef, to: str, *, note: str = "", by: str = "") -> Decision:
    """Record that ``unit`` went back to stage ``to``: approvals for that stage and later ones no longer count."""
    if unit.doc.stage(to) is None:
        raise input_error(
            f"{to!r} is not a stage of {unit.doc.id}",
            code="RETURN_INVALID",
            fix=f"Use one of: {', '.join(s.id for s in unit.doc.stages)}",
        )
    decisions = load_decisions(unit.dir)
    record = new_decision(decisions, RETURN_PREFIX + to, "accept", workflow=unit.doc.id, stage=to, note=note, by=by)
    return write_decision(unit.dir, record)


__all__ = ["UnitRef", "Workspace", "record_return"]
