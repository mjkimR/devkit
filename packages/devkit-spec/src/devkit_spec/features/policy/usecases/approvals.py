"""Resolve delegation from the owning checkout; a task branch cannot grant itself authority."""

from pathlib import Path

from devkit_agt.features.workflow import load_workflow_config
from devkit_agt.features.worktree import locate

from devkit_spec.base.errors import SpecConfigError
from devkit_spec.features.policy.repositories.branches import checkout
from devkit_spec.features.policy.services.config import check_approvals


def approval_policy(root: Path, gate: str) -> str:
    root = root.resolve()
    owner = root
    if checkout(root) is not None:
        owner = locate(root).base
    configured = load_workflow_config(owner)
    check_approvals(configured.approvals)
    policy = configured.policy(gate)
    if policy == "auto" and owner != root:
        source = load_workflow_config(root)
        check_approvals(source.approvals)
        if source.policy(gate) != "auto":
            raise SpecConfigError(f"the task checkout revokes automatic {gate} authority")
    return policy
