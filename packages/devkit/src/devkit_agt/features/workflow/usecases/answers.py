"""Answering the engine's human requests, and recording returns to an earlier stage."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.workflow.models.decision_records import Decision
from devkit_agt.features.workflow.models.decisions import ACTIONS
from devkit_agt.features.workflow.models.errors import (
    DecisionInvalidError,
    RequestUnknownError,
    ReturnInvalidError,
    workflow_command,
)
from devkit_agt.features.workflow.models.requests import Request
from devkit_agt.features.workflow.repositories.unit.decisions import (
    FEEDBACK_PREFIX,
    RETURN_PREFIX,
    is_request_id,
    load_decisions,
    new_decision,
    write_decision,
)
from devkit_agt.features.workflow.usecases.workspace import UnitRef, Workspace


def validate_answer(request: Request, action: str, values: Sequence[str]) -> Any:
    """Check that ``action`` and ``values`` fit the open ``request``; returns the record's ``value``.

    Raises ``DecisionInvalidError`` (``DECISION_INVALID``) for a value on an
    approve request, a missing, unknown or ineligible option, several values,
    or a value without accept.
    """
    if action not in ACTIONS:
        raise DecisionInvalidError(
            f"--action {action!r} is not one of {'|'.join(ACTIONS)}",
            target_files=["--action"],
            fix=f"Pass --action {' or '.join(ACTIONS)}",
        )
    if action != "accept":
        if values:
            raise DecisionInvalidError(
                "--value is only valid with --action accept",
                target_files=["--value"],
                fix="Drop --value, or use --action accept",
            )
        return None
    if request.kind == "approve":
        if values:
            raise DecisionInvalidError(
                "an approve request takes no --value",
                target_files=["--value"],
                fix="Drop --value; pass --action accept or --action decline, optionally with --note",
            )
        return None
    eligible = [o.id for o in request.options if o.eligible]
    if len(values) != 1:
        raise DecisionInvalidError(
            "a choose request takes exactly one --value",
            target_files=["--value"],
            fix=f"Pass one --value: {', '.join(eligible)}" if eligible else "No option is eligible; decline or cancel",
        )
    options = {o.id: o for o in request.options}
    option = options.get(values[0])
    if option is None:
        raise DecisionInvalidError(
            f"{values[0]!r} is not an option of {request.id}",
            target_files=["--value"],
            fix=f"Pass --value one of: {', '.join(options)}",
        )
    if not option.eligible:
        raise DecisionInvalidError(
            f"option {values[0]!r} is not eligible: {option.description or 'preconditions do not hold'}",
            target_files=["--value"],
            fix=f"Pass --value an eligible option ({', '.join(eligible)})"
            if eligible
            else "No option is eligible; decline or cancel",
        )
    return values[0]


class RecordAnswerUseCase(BaseUseCase):
    """Execute the record answer operation."""

    def execute(
        self,
        ws: Workspace,
        unit: str | UnitRef,
        request_id: str,
        action: str,
        values: Sequence[str] = (),
        *,
        note: str = "",
        by: str = "",
        given: Sequence[str] = (),
        lint: bool = True,
    ) -> Decision:
        """Validate an answer against the unit's open requests and write its decision record.

        ``feedback:<target>`` is accepted at any time with exactly one ``--value``
        on accept. Every other id must be an open request of the unit, evaluated
        with ``given`` as ``next --given`` does. An
        ``action`` outside ``ACTIONS`` raises ``DecisionInvalidError``
        (``DECISION_INVALID``) for every request.
        """
        ref = unit if isinstance(unit, UnitRef) else ws.resolve_unit(unit)
        listing = workflow_command(f"next --view requests --unit {ref.rel}")
        if not is_request_id(request_id):
            raise RequestUnknownError(
                f"--request {request_id!r} is not a request id (an open request, or feedback:<target>)",
                target_files=["--request"],
                fix=listing,
            )
        stage = ""
        if request_id.startswith(FEEDBACK_PREFIX):
            if action not in ACTIONS:
                raise DecisionInvalidError(
                    f"--action {action!r} is not one of {'|'.join(ACTIONS)}",
                    target_files=["--action"],
                    fix=f"Pass --action {' or '.join(ACTIONS)}",
                )
            if action == "accept":
                if len(values) != 1 or not values[0].strip():
                    raise DecisionInvalidError(
                        "feedback requires exactly one --value with the text",
                        target_files=["--value"],
                        fix="Pass the feedback text as one non-empty --value",
                    )
            elif values:
                raise DecisionInvalidError(
                    "--value is only valid with --action accept", target_files=["--value"], fix="Drop --value"
                )
            value: Any = values[0] if values else None
        else:
            result = ws.evaluate_unit(ref, given=given, lint=lint)
            open_requests = {r.id: r for r in result.requests}
            request = open_requests.get(request_id)
            if request is None:
                raise RequestUnknownError(
                    f"{request_id!r} is not an open request of {ref.rel}",
                    *([f"open: {rid}" for rid in open_requests] or ["open: none"]),
                    target_files=["--request"],
                    fix=listing,
                )
            if request.answer == "envelope":
                source, _, question = request.target.name.partition("#")
                raise DecisionInvalidError(
                    f"{request_id} is a question; its answer is an answer envelope, not a decision record: pipe the"
                    f" answers as a YAML list on stdin, each with question ({question}), choice (an option id or"
                    " null) and decision (one sentence)",
                    target_files=["--request"],
                    fix=workflow_command(f"envelope answer --unit {ref.rel} --answers-to {source} --answers-file -"),
                )
            value = validate_answer(request, action, values)
            stage = request.target.stage or ""
        decisions = load_decisions(ref.dir)
        record = new_decision(
            decisions, request_id, action, workflow=ref.doc.id, stage=stage, value=value, note=note, by=by
        )
        return write_decision(ref.dir, record)


# Internal library callers share the same implementation as the transport entry point.
record_answer = RecordAnswerUseCase().execute


class ReturnToStageUseCase(BaseUseCase):
    """Execute the return to operation."""

    def execute(
        self,
        ws: Workspace,
        unit: str | UnitRef,
        stage: str,
        *,
        note: str = "",
        by: str = "",
        given: Sequence[str] = (),
        lint: bool = True,
    ) -> Decision:
        """Take the unit back to ``stage``: approvals for it and every later stage must be given again.

        ``stage`` must not come after the current stage (any stage once the workflow is complete), evaluated with
        ``given`` as ``next --given`` does.
        """
        ref = unit if isinstance(unit, UnitRef) else ws.resolve_unit(unit)
        target = ref.doc.stage_index(stage)
        if target < 0:
            raise ReturnInvalidError(
                f"{stage!r} is not a stage of {ref.doc.id}",
                target_files=["--to"],
                fix=f"Pass --to one of: {', '.join(s.id for s in ref.doc.stages)}",
            )
        result = ws.evaluate_unit(ref, given=given, lint=lint)
        if result.stage is not None and target > ref.doc.stage_index(result.stage.id):
            raise ReturnInvalidError(
                f"stage {stage!r} comes after the current stage {result.stage.id!r}",
                target_files=["--to"],
                fix=f"Pass --to {result.stage.id} or an earlier stage",
            )
        return _record_return(ref, stage, note=note, by=by)


def _record_return(unit: UnitRef, to: str, *, note: str = "", by: str = "") -> Decision:
    """Record that ``unit`` went back to stage ``to``: approvals for that stage and later ones no longer count."""
    decisions = load_decisions(unit.dir)
    record = new_decision(decisions, RETURN_PREFIX + to, "accept", workflow=unit.doc.id, stage=to, note=note, by=by)
    return write_decision(unit.dir, record)
