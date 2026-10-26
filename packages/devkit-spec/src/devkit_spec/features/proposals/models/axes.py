"""Planning and activity effort values, and the size predicate, shared by the adapters and workflow binding."""

from collections.abc import Mapping

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

SIZE = "size"
SIZES = ("S", "M", "L")
DECOMPOSE_EXITS = "split with --decomposed-from or promote to a milestone"
ALLOWED_SIZES = "allowed: S, M, L or absent"


def size_blocker(meta: Mapping[str, object]) -> str | None:
    """``None`` when ``size`` is absent or exactly ``S``, ``M`` or ``L``; else ``size: <value>`` as read.

    The one size predicate of the decomposition gate, read like the ``sdd-proposal`` exit check
    ``frontmatter(proposal.md size S|M|L|)`` (an empty value is absent): ``XL``, ``xl``, a number or a typo fail it.
    """
    value = meta.get(SIZE)
    if value is None or value == "" or (isinstance(value, str) and value in SIZES):
        return None
    return f"{SIZE}: {value}"
