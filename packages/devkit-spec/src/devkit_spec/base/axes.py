"""The delivery vocabulary every feature shares: task kinds, efforts, workflow ids and the size predicate."""

from collections.abc import Mapping

# The effort vocabulary of proposal frontmatter is the document layer's; delivery modules read it from here.
from devkit_docs.base.layout import DEV_EFFORT as DEV_EFFORT
from devkit_docs.base.layout import EFFORTS as EFFORTS
from devkit_docs.base.layout import PLANNING_EFFORT as PLANNING_EFFORT

TASK_KINDS = ("feature", "bugfix")
DEFAULT_TASK_KIND = "feature"
DEFAULT_EFFORT = "medium"
PROPOSAL_WORKFLOW = "sdd-proposal"
SPEC_WORKFLOW_PREFIX = "sdd-spec-"


def spec_workflow(task_kind: str) -> str:
    """Return the workflow for the task kind."""
    return f"{SPEC_WORKFLOW_PREFIX}{task_kind}"


DEFAULT_WORKFLOW = spec_workflow(DEFAULT_TASK_KIND)
BUGFIX_WORKFLOW = spec_workflow("bugfix")
SPEC_WORKFLOWS = frozenset(spec_workflow(kind) for kind in TASK_KINDS)

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
