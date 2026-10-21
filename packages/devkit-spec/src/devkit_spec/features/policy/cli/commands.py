"""``devkit spec policy``: the project policy that routing, gate and Git decisions follow, in one place.

Text output: ``[GATE_POLICY: <gate> policy= source=]`` for the gates of the spec workflows (``plan-intent``,
``plan-accept``, ``dev-integration``) and any other gate the project configures, ``[STAGE_POLICY: <stage> state=off]``
per stage the project switched off, ``[GIT_POLICY: worktree= pull_request= delete_branch= setup=]``,
``[ROUTING_POLICY: depth_escalation=]`` and ``[FEEDBACK_POLICY: capture= coverage= detail= reminder=]``.
``source`` is ``fixed`` for a gate a person always decides (``plan-intent``, ``plan-accept``), ``config`` when
``.devkit/config.toml`` sets the value, else ``default``. A policy key for a fixed gate, or ``dev-integration =
"off"``, is ``SPEC_CONFIG_INVALID``; a key that names no gate (``exception``) is a ``SPEC_APPROVAL_KEY_IGNORED``
warning and is not listed.
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

from devkit_spec.features.policy.usecases.inspect import inspect_policy
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
    policy, notices = inspect_policy(root)
    approvals = policy["approvals"]
    stages_off = policy["stages_off"]
    git = policy["git"]
    routing = policy["routing"]
    feedback = policy["feedback"]
    if is_json(output_format):
        echo_json(
            {
                "approvals": approvals,
                "stages_off": stages_off,
                "git": git,
                "routing": routing,
                "feedback": feedback,
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
    echo_notices(notices)
    exit_on_warnings(notices)
