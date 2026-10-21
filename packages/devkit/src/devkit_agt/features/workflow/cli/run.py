"""``next``, ``answer``, ``return`` and ``handoff``."""

from __future__ import annotations

import click
from devkit_dist.adapters.cli import FORMAT_OPTION, Reported, boundary, echo_json, is_json

from devkit_agt.features.workflow.cli.app import ANCHOR, NO_LINT, UNIT, WORKSPACE, cli, parse_date, workspace
from devkit_agt.features.workflow.cli.render import quote, render_evaluation, render_requests
from devkit_agt.features.workflow.models.decisions import ACTIONS
from devkit_agt.features.workflow.usecases.answers import record_answer, return_to
from devkit_agt.features.workflow.usecases.handoff import apply_handoff, plan_handoff


@cli.command(name="next")
@WORKSPACE
@UNIT
@ANCHOR
@click.option("--workflow", "workflow_ref", default=None, help="Evaluate against this workflow instead of the binding")
@click.option("--given", multiple=True, help="Gate, runner or human check the executor holds (repeatable)")
@click.option(
    "--view",
    type=click.Choice(["next", "requests"]),
    default="next",
    show_default=True,
    help="Full next step or only open requests",
)
@NO_LINT
@FORMAT_OPTION
@boundary
def next_cmd(
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    workflow_ref: str | None,
    given: tuple[str, ...],
    view: str,
    no_lint: bool,
    output_format: str,
) -> None:
    """Report the current stage of a unit, what is unmet and what to do next.

    When the rules behind lint-clean cannot run, their error is reported
    unchanged after the result and sets the exit code.
    """
    ws = workspace(workspace_root)
    ref = ws.resolve_unit(unit, workflow_ref, anchor=anchor)
    result = ws.evaluate_unit(ref, given=given, lint=not no_lint)
    lint_error = result.lint_error
    if view == "requests":
        if is_json(output_format):
            errors = [lint_error.to_dict()] if lint_error is not None else []
            echo_json({"requests": [r.to_dict() for r in result.requests], "errors": errors})
        else:
            lines = render_requests(result.requests) or ["[REQUESTS: none]"]
            if lint_error is not None:
                lines.append(f"[LINT_ERROR: {quote(lint_error.message)}]")
            click.echo("\n".join(lines))
    elif is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(render_evaluation(result), nl=False)
    if lint_error is not None:
        raise Reported(lint_error)


@cli.command(name="answer")
@WORKSPACE
@UNIT
@ANCHOR
@click.option(
    "--request",
    "request_id",
    required=True,
    help="Open request id (gate:<gate>, check:<name>, handoff) or feedback:<target>",
)
@click.option("--action", required=True, type=click.Choice(list(ACTIONS)), help="accept, decline or cancel")
@click.option("--value", "values", multiple=True, help="Chosen option id (choose) or the text (feedback)")
@click.option("--note", default="", help="Free-text note, recommended on decline")
@click.option("--by", "by", default="", help="Who answered (person or host)")
@NO_LINT
@FORMAT_OPTION
@boundary
def answer_cmd(
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    request_id: str,
    action: str,
    values: tuple[str, ...],
    note: str,
    by: str,
    no_lint: bool,
    output_format: str,
) -> None:
    """Record a decision for an open request as <unit>/decisions/NN-<request>.yaml."""
    ws = workspace(workspace_root)
    decision = record_answer(
        ws, ws.resolve_unit(unit, anchor=anchor), request_id, action, values, note=note, by=by, lint=not no_lint
    )
    if is_json(output_format):
        echo_json(decision.to_dict())
    else:
        click.echo(f"[DECISION: {decision.file} request={decision.request} kind={decision.kind} action={action}]")


@cli.command(name="return")
@WORKSPACE
@UNIT
@ANCHOR
@click.option("--to", "stage", required=True, help="Stage the unit goes back to (the current one or an earlier one)")
@click.option("--note", default="", help="Why the unit goes back")
@click.option("--by", "by", default="", help="Who decided (person or host)")
@NO_LINT
@FORMAT_OPTION
@boundary
def return_cmd(
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    stage: str,
    note: str,
    by: str,
    no_lint: bool,
    output_format: str,
) -> None:
    """Take a unit back to a stage; approvals for it and later stages must be given again."""
    ws = workspace(workspace_root)
    decision = return_to(ws, ws.resolve_unit(unit, anchor=anchor), stage, note=note, by=by, lint=not no_lint)
    if is_json(output_format):
        echo_json(decision.to_dict())
    else:
        click.echo(f"[RETURNED: {decision.file} to={stage}]")


@cli.command(name="handoff")
@WORKSPACE
@UNIT
@ANCHOR
@click.option(
    "--workflow",
    "workflow_ref",
    default=None,
    help="Candidate to continue with (recorded as the handoff decision); default: the recorded or automatic choice",
)
@click.option(
    "--date", "when", default=None, help="Completion date recorded in the history, YYYY-MM-DD (default: today)"
)
@click.option("--by", "by", default="", help="Who chose the candidate given with --workflow")
@NO_LINT
@FORMAT_OPTION
@boundary
def handoff_cmd(
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    workflow_ref: str | None,
    when: str | None,
    by: str,
    no_lint: bool,
    output_format: str,
) -> None:
    """Hand a completed unit to one of its workflow's next candidates and rebind it."""
    ws = workspace(workspace_root)
    day = parse_date(when)
    ref = ws.resolve_unit(unit, anchor=anchor)
    result = ws.evaluate_unit(ref, lint=not no_lint)
    outcome = apply_handoff(plan_handoff(ws, ref, result, workflow_ref), when=day, by=by)
    if is_json(output_format):
        echo_json(outcome.to_dict())
        return
    tail = f" decision={outcome.decision}" if outcome.decision else ""
    click.echo(f"[HANDOFF: from={outcome.source} to={outcome.target} policy={outcome.policy}{tail}]")
    click.echo(f"[HISTORY: {' '.join(h.workflow for h in outcome.history)}]")
