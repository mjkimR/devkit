"""Answering the engine's human requests, and recording returns to an earlier stage."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from devkit.workflow.decisions import (
    ACTIONS,
    FEEDBACK_PREFIX,
    REQUEST_ID,
    Decision,
    load_decisions,
    new_decision,
    write_decision,
)
from devkit.workflow.errors import input_error
from devkit.workflow.requests import Request
from devkit.workflow.workspace import UnitRef, Workspace, record_return


def validate_answer(request: Request, action: str, values: Sequence[str]) -> Any:
    """Check that ``action`` and ``values`` fit the open ``request``; returns the record's ``value``.

    Raises ``DECISION_INVALID`` for a value on an approve request, a missing,
    unknown or ineligible option, several values, or a value without accept.
    """
    if action not in ACTIONS:
        raise input_error(f"--action {action!r} is not one of {'|'.join(ACTIONS)}", code="DECISION_INVALID")
    if action != "accept":
        if values:
            raise input_error(
                "--value is only valid with --action accept",
                code="DECISION_INVALID",
                fix="Drop --value, or use --action accept",
            )
        return None
    if request.kind == "approve":
        if values:
            raise input_error(
                "an approve request takes no --value",
                code="DECISION_INVALID",
                fix="Pass --action accept or --action decline, optionally with --note",
            )
        return None
    eligible = [o.id for o in request.options if o.eligible]
    if len(values) != 1:
        raise input_error(
            "a choose request takes exactly one --value",
            code="DECISION_INVALID",
            fix=f"Choose one of: {', '.join(eligible) or 'none eligible'}",
        )
    options = {o.id: o for o in request.options}
    option = options.get(values[0])
    if option is None:
        raise input_error(
            f"{values[0]!r} is not an option of {request.id}",
            code="DECISION_INVALID",
            fix=f"Choose one of: {', '.join(options)}",
        )
    if not option.eligible:
        raise input_error(
            f"option {values[0]!r} is not eligible: {option.description or 'preconditions do not hold'}",
            code="DECISION_INVALID",
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
    on accept. Every other id must be an open request of the unit.
    """
    ref = unit if isinstance(unit, UnitRef) else ws.resolve_unit(unit)
    if not REQUEST_ID.match(request_id):
        raise input_error(
            f"--request {request_id!r} is not a request id",
            code="REQUEST_UNKNOWN",
            fix="Use an id printed by `devkit workflow requests`, or feedback:<target>",
        )
    stage = ""
    if request_id.startswith(FEEDBACK_PREFIX):
        if action == "accept":
            if len(values) != 1 or not values[0].strip():
                raise input_error(
                    "feedback requires exactly one --value with the text",
                    code="DECISION_INVALID",
                    fix="Pass --value <text>",
                )
        elif values:
            raise input_error("--value is only valid with --action accept", code="DECISION_INVALID", fix="Drop --value")
        value: Any = values[0] if values else None
    else:
        result = ws.evaluate_unit(ref, lint=lint)
        open_requests = {r.id: r for r in result.requests}
        request = open_requests.get(request_id)
        if request is None:
            raise input_error(
                f"{request_id!r} is not an open request of {ref.rel}",
                *([f"open: {rid}" for rid in open_requests] or ["open: none"]),
                code="REQUEST_UNKNOWN",
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
        raise input_error(
            f"{stage!r} is not a stage of {ref.doc.id}",
            code="RETURN_INVALID",
            fix=f"Use one of: {', '.join(s.id for s in ref.doc.stages)}",
        )
    result = ws.evaluate_unit(ref, lint=lint, record_returns=False)
    if result.stage is not None and target > ref.doc.stage_index(result.stage.id):
        raise input_error(
            f"stage {stage!r} comes after the current stage {result.stage.id!r}",
            code="RETURN_INVALID",
            fix=f"Return to {result.stage.id!r} or an earlier stage",
        )
    return record_return(ref, stage, note=note, by=by)
