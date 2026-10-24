"""``devkit spec policy``: the project policy that routing, gate and Git decisions follow, in one place.

Text output lists plan-accept, proposal-handoff, dev-integration and task intent, followed by configured custom
gates, disabled stages, Git, routing and feedback policies. A policy source is config or default. Main boundaries
and task intent permit ask or auto, never off. A key naming no gate (exception) emits SPEC_APPROVAL_KEY_IGNORED.

"""

from __future__ import annotations

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_spec.features.policy.usecases.inspect import InspectPolicyUseCase
from devkit_spec.utils.output import fields_line, sentinel

# Keys that name no gate: ``exception`` is a shared stage a person always handles (03 §2).
NOT_GATES = ("exception",)


@click.command(name="policy")
@workspace_option()
@FORMAT_OPTION
@boundary
def policy_cmd(workspace_root: str | None, output_format: str) -> None:
    """Print effective approval, stage, Git, routing and feedback policy; read it before routing or recording
    feedback."""
    root = resolve_root(workspace_root)
    policy, notices = InspectPolicyUseCase().execute(root)
    approvals = policy["approvals"]
    stages_off = policy["stages_off"]
    git = policy["git"]
    routing = policy["routing"]
    feedback = policy["feedback"]
    proposal_review = policy["proposal_review"]
    if is_json(output_format):
        echo_json(
            {
                "approvals": approvals,
                "stages_off": stages_off,
                "git": git,
                "routing": routing,
                "feedback": feedback,
                "proposal_review": proposal_review,
                "notices": [notice.to_dict() for notice in notices],
            }
        )
        exit_on_warnings(notices)
        return
    for gate, entry in approvals.items():
        click.echo(sentinel("GATE_POLICY", gate, **entry))
    for stage in stages_off:
        click.echo(sentinel("STAGE_POLICY", stage, state="off"))
    click.echo(fields_line("GIT_POLICY", **git))
    click.echo(fields_line("ROUTING_POLICY", **routing))
    click.echo(fields_line("FEEDBACK_POLICY", **feedback))
    click.echo(fields_line("PROPOSAL_REVIEW_POLICY", auto_write=str(proposal_review["auto_write"]).lower()))
    echo_notices(notices)
    exit_on_warnings(notices)
