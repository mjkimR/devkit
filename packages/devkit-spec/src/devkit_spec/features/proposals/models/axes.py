"""Planning and activity effort values shared by the adapters and workflow binding."""

TASK_KINDS = ("feature", "bugfix")
DEFAULT_TASK_KIND = "feature"
EFFORTS = ("low", "medium", "high")
DEFAULT_EFFORT = "medium"
PLANNING_EFFORT = "planning_effort"
DEV_EFFORT = "dev_effort"
PROPOSAL_WORKFLOW = "sdd-proposal"


def spec_workflow(task_kind: str) -> str:
    """Return the workflow for the task kind."""
    return f"sdd-spec-{task_kind}"


DEFAULT_WORKFLOW = spec_workflow(DEFAULT_TASK_KIND)
BUGFIX_WORKFLOW = spec_workflow("bugfix")
