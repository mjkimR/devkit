"""Answering the engine's human requests, and recording returns to an earlier stage."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from devkit.workflow.errors import DecisionInvalidError, RequestUnknownError, ReturnInvalidError
from devkit.workflow.evaluation.requests import Request
from devkit.workflow.unit.decisions import (
    ACTIONS,
    FEEDBACK_PREFIX,
    RETURN_PREFIX,
    Decision,
    is_request_id,
    load_decisions,
    new_decision,
    write_decision,
)
from devkit.workflow.workspace import UnitRef, Workspace


def validate_answer(request: Request, action: str, values: Sequence[str]) -> Any:
    """Check that ``action`` and ``values`` fit the open ``request``; returns the record's ``value``.

    Raises ``DecisionInvalidError`` (``DECISION_INVALID``) for a value on an
    approve request, a missing, unknown or ineligible option, several values,
    or a value without accept.
    """
    if action not in ACTIONS:
        raise DecisionInvalidError(f"--action {action!r} is not one of {'|'.join(ACTIONS)}")
    if action != "accept":
        if values:
            raise DecisionInvalidError(
                "--value is only valid with --action accept",
                fix="Drop --value, or use --action accept",
            )
        return None
    if request.kind == "approve":
        if values:
            raise DecisionInvalidError(
                "an approve request takes no --value",
                fix="Pass --action accept or --action decline, optionally with --note",
            )
        return None
    eligible = [o.id for o in request.options if o.eligible]
    if len(values) != 1:
        raise DecisionInvalidError(
            "a choose request takes exactly one --value",
            fix=f"Choose one of: {', '.join(eligible) or 'none eligible'}",
        )
    options = {o.id: o for o in request.options}
    option = options.get(values[0])
    if option is None:
        raise DecisionInvalidError(
            f"{values[0]!r} is not an option of {request.id}",
            fix=f"Choose one of: {', '.join(options)}",
        )
    if not option.eligible:
        raise DecisionInvalidError(
            f"option {values[0]!r} is not eligible: {option.description or 'preconditions do not hold'}",
            fix="Satisfy its preconditions first, or choose an eligible option",
        )
    return values[0]


def record_answer(
    ws: Workspace,
    unit: str | UnitRef,
    request_id: str,
    action: str,
    values: Sequence[str] = (),
    *,
    note: str = "",
    by: str = "",
    lint: bool = True,
) -> Decision:
    """Validate an answer against the unit's open requests and write its decision record.

    ``feedback:<target>`` is accepted at any time with exactly one ``--value``
    on accept. Every other id must be an open request of the unit. An
    ``action`` outside ``ACTIONS`` raises ``DecisionInvalidError``
    (``DECISION_INVALID``) for every request.
    """
    ref = unit if isinstance(unit, UnitRef) else ws.resolve_unit(unit)
    if not is_request_id(request_id):
        raise RequestUnknownError(
            f"--request {request_id!r} is not a request id",
            fix="Use an id printed by `devkit workflow requests`, or feedback:<target>",
        )
    stage = ""
    if request_id.startswith(FEEDBACK_PREFIX):
        if action not in ACTIONS:
            raise DecisionInvalidError(f"--action {action!r} is not one of {'|'.join(ACTIONS)}")
        if action == "accept":
            if len(values) != 1 or not values[0].strip():
                raise DecisionInvalidError(
                    "feedback requires exactly one --value with the text",
                    fix="Pass --value <text>",
                )
        elif values:
            raise DecisionInvalidError("--value is only valid with --action accept", fix="Drop --value")
        value: Any = values[0] if values else None
    else:
        result = ws.evaluate_unit(ref, lint=lint)
        open_requests = {r.id: r for r in result.requests}
        request = open_requests.get(request_id)
        if request is None:
            raise RequestUnknownError(
                f"{request_id!r} is not an open request of {ref.rel}",
                *([f"open: {rid}" for rid in open_requests] or ["open: none"]),
                fix="Run `devkit workflow requests --unit <dir>` and answer one of the listed ids",
            )
        value = validate_answer(request, action, values)
        stage = request.target.stage or ""
    decisions = load_decisions(ref.dir)
    record = new_decision(
        decisions, request_id, action, workflow=ref.doc.id, stage=stage, value=value, note=note, by=by
    )
    return write_decision(ref.dir, record)


def return_to(
    ws: Workspace, unit: str | UnitRef, stage: str, *, note: str = "", by: str = "", lint: bool = True
) -> Decision:
    """Take the unit back to ``stage``: approvals for it and every later stage must be given again.

    ``stage`` must not come after the current stage (any stage once the workflow is complete).
    """
    ref = unit if isinstance(unit, UnitRef) else ws.resolve_unit(unit)
    target = ref.doc.stage_index(stage)
    if target < 0:
        raise ReturnInvalidError(
            f"{stage!r} is not a stage of {ref.doc.id}",
            fix=f"Use one of: {', '.join(s.id for s in ref.doc.stages)}",
        )
    result = ws.evaluate_unit(ref, lint=lint)
    if result.stage is not None and target > ref.doc.stage_index(result.stage.id):
        raise ReturnInvalidError(
            f"stage {stage!r} comes after the current stage {result.stage.id!r}",
            fix=f"Return to {result.stage.id!r} or an earlier stage",
        )
    return _record_return(ref, stage, note=note, by=by)


def _record_return(unit: UnitRef, to: str, *, note: str = "", by: str = "") -> Decision:
    """Record that ``unit`` went back to stage ``to``: approvals for that stage and later ones no longer count."""
    decisions = load_decisions(unit.dir)
    record = new_decision(decisions, RETURN_PREFIX + to, "accept", workflow=unit.doc.id, stage=to, note=note, by=by)
    return write_decision(unit.dir, record)
