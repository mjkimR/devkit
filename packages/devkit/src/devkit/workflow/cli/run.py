"""``next``, ``requests``, ``answer``, ``return`` and ``handoff``."""

from __future__ import annotations

import click

from devkit.core.cli import FORMAT_OPTION, Reported, boundary, echo_json, is_json
from devkit.workflow.answers import record_answer, return_to
from devkit.workflow.cli.app import NO_LINT, UNIT, WORKSPACE, cli, parse_date, workspace
from devkit.workflow.handoff import apply_handoff, plan_handoff
from devkit.workflow.render import render_evaluation, render_requests
from devkit.workflow.unit.decisions import ACTIONS


@cli.command(name="next")
@WORKSPACE
@UNIT
@click.option("--workflow", "workflow_ref", default=None, help="Evaluate against this workflow instead of the binding")
@click.option("--given", multiple=True, help="Gate, runner or human check the executor holds (repeatable)")
@NO_LINT
@FORMAT_OPTION
@boundary
def next_cmd(
    workspace_root: str | None,
    unit: str,
    workflow_ref: str | None,
    given: tuple[str, ...],
    no_lint: bool,
    output_format: str,
) -> None:
    """Report the current stage of a unit, what is unmet and what to do next.

    When the rules behind lint-clean cannot run, their error is reported
    unchanged after the result and sets the exit code.
    """
    ws = workspace(workspace_root)
    ref = ws.resolve_unit(unit, workflow_ref)
    result = ws.evaluate_unit(ref, given=given, lint=not no_lint)
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(render_evaluation(result), nl=False)
    if result.lint_error is not None:
        raise Reported(result.lint_error)


@cli.command(name="requests")
@WORKSPACE
@UNIT
@NO_LINT
@FORMAT_OPTION
@boundary
def requests_cmd(workspace_root: str | None, unit: str, no_lint: bool, output_format: str) -> None:
    """List the open human requests of a unit (approvals and choices)."""
    ws = workspace(workspace_root)
    result = ws.evaluate_unit(ws.resolve_unit(unit), lint=not no_lint)
    if is_json(output_format):
        echo_json({"requests": [r.to_dict() for r in result.requests]})
        return
    lines = render_requests(result.requests)
    click.echo("\n".join(lines) if lines else "[REQUESTS: none]")


@cli.command(name="answer")
@WORKSPACE
@UNIT
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
    decision = record_answer(ws, unit, request_id, action, values, note=note, by=by, lint=not no_lint)
    if is_json(output_format):
        echo_json(decision.to_dict())
    else:
        click.echo(f"[DECISION: {decision.file} request={decision.request} kind={decision.kind} action={action}]")


@cli.command(name="return")
@WORKSPACE
@UNIT
@click.option("--to", "stage", required=True, help="Stage the unit goes back to (the current one or an earlier one)")
@click.option("--note", default="", help="Why the unit goes back")
@click.option("--by", "by", default="", help="Who decided (person or host)")
@NO_LINT
@FORMAT_OPTION
@boundary
def return_cmd(
    workspace_root: str | None, unit: str, stage: str, note: str, by: str, no_lint: bool, output_format: str
) -> None:
    """Take a unit back to a stage; approvals for it and later stages must be given again."""
    ws = workspace(workspace_root)
    decision = return_to(ws, unit, stage, note=note, by=by, lint=not no_lint)
    if is_json(output_format):
        echo_json(decision.to_dict())
    else:
        click.echo(f"[RETURNED: {decision.file} to={stage}]")


@cli.command(name="handoff")
@WORKSPACE
@UNIT
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
    workflow_ref: str | None,
    when: str | None,
    by: str,
    no_lint: bool,
    output_format: str,
) -> None:
    """Hand a completed unit to one of its workflow's next candidates and rebind it."""
    ws = workspace(workspace_root)
    day = parse_date(when)
    ref = ws.resolve_unit(unit)
    result = ws.evaluate_unit(ref, lint=not no_lint)
    outcome = apply_handoff(plan_handoff(ws, ref, result, workflow_ref), when=day, by=by)
    if is_json(output_format):
        echo_json(outcome.to_dict())
        return
    tail = f" decision={outcome.decision}" if outcome.decision else ""
    click.echo(
        f"[HANDOFF: from={outcome.source} to={outcome.target} hash={outcome.workflow_hash} policy={outcome.policy}{tail}]"
    )
    click.echo(f"[HISTORY: {' '.join(h.workflow for h in outcome.history)}]")
