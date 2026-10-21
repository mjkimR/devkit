"""Named execution boundaries over one shared workflow workspace."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path

from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.workflow.models.checks import Check, Registry
from devkit_agt.features.workflow.models.results import UnitEvaluation
from devkit_agt.features.workflow.services.definition.validation import ValidationReport
from devkit_agt.features.workflow.usecases.handoff import HandoffOutcome, apply_handoff, plan_handoff
from devkit_agt.features.workflow.usecases.workspace import DefinitionDescription, UnitRef, Workspace


class BindUnitUseCase(BaseUseCase):
    """Bind a unit using the caller's workspace and caches."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(self, unit: str, workflow: str | None = None, *, anchor: str | None = None) -> UnitRef:
        return self.workspace.bind_unit(unit, workflow, anchor=anchor)


class DescribeWorkflowUseCase(BaseUseCase):
    """Describe a selected definition or a unit's current binding."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(self, ref: str | None, *, unit: str | None = None, anchor: str | None = None) -> DefinitionDescription:
        if unit is not None:
            return self.workspace.describe_unit(unit, anchor=anchor)
        assert ref is not None
        return self.workspace.describe(self.workspace.load_definition(ref))


class EvaluateUnitUseCase(BaseUseCase):
    """Resolve and evaluate a unit without constructing another workspace."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(
        self,
        unit: str,
        workflow: str | None = None,
        *,
        anchor: str | None = None,
        given: Sequence[str] = (),
        lint: bool = True,
    ) -> UnitEvaluation:
        ref = self.workspace.resolve_unit(unit, workflow, anchor=anchor)
        return self.workspace.evaluate_unit(ref, given=given, lint=lint)


class HandoffWorkflowUseCase(BaseUseCase):
    """Evaluate and apply one workflow transition."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(
        self,
        unit: str,
        workflow: str | None = None,
        *,
        anchor: str | None = None,
        when: date | None = None,
        by: str = "",
        lint: bool = True,
    ) -> HandoffOutcome:
        ref = self.workspace.resolve_unit(unit, anchor=anchor)
        result = self.workspace.evaluate_unit(ref, lint=lint)
        return apply_handoff(plan_handoff(self.workspace, ref, result, workflow), when=when, by=by)


class ListChecksUseCase(BaseUseCase):
    """List the registry associated with this workspace's configured anchor."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(self) -> list[Check]:
        return Registry.build(self.workspace.config.anchor).entries()


class ValidateWorkflowsUseCase(BaseUseCase):
    """Validate selected or discovered workflow definitions."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def execute(self, paths: Sequence[Path] = ()) -> ValidationReport:
        return self.workspace.validate_definitions(paths)
