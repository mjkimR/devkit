"""Load and validate the effective specification delivery policy."""

from dataclasses import asdict
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_agt.features.workflow import load_workflow_config
from devkit_agt.features.worktree import read_worktree_config

from devkit_spec.base.errors import ApprovalKeyIgnoredWarning
from devkit_spec.features.policy.services.config import APPROVAL_GATES, INTENT_GATE, check_approvals, read_spec_config

GATES = (*APPROVAL_GATES, INTENT_GATE)
NOT_GATES = ("exception",)


def inspect_policy(root: Path) -> tuple[dict, list[AdvisoryError]]:
    workflow = load_workflow_config(root)
    check_approvals(workflow.approvals)
    worktree = read_worktree_config(root)
    spec = read_spec_config(root)
    gates = [*GATES, *sorted(set(workflow.approvals) - set(GATES) - set(NOT_GATES))]
    notices: list[AdvisoryError] = [
        ApprovalKeyIgnoredWarning(
            f"[workflow.approvals] {key} has no effect: {key} is a stage a person always handles, not a gate",
            fix=f"Remove {key} from [workflow.approvals] in .devkit/config.toml",
        )
        for key in sorted(set(workflow.approvals) & set(NOT_GATES))
    ]
    approvals = {
        gate: {
            "policy": workflow.policy(gate),
            "source": "config" if gate in workflow.approvals else "default",
        }
        for gate in gates
    }
    stages_off = sorted(stage for stage in workflow.stages if workflow.stage_policy(stage) == "off")
    feedback = asdict(spec.feedback)
    git = {
        "worktree": spec.worktree,
        "pull_request": worktree.pull_request,
        "delete_branch": worktree.delete_branch,
        "setup": worktree.setup,
    }
    routing = {"depth_escalation": spec.depth_escalation}
    return {
        "approvals": approvals,
        "stages_off": stages_off,
        "git": git,
        "routing": routing,
        "feedback": feedback,
    }, notices
