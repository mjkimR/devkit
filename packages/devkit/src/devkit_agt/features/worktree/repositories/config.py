"""The ``[worktree]`` table of ``.devkit/config.toml``.

```toml
[worktree]
pull_request = "auto"   # a pull request or local integration, as the task needs; "required": pull requests only
delete_branch = true    # finish deletes the merged branch (`git branch -d`, never -D)
merge = "no-ff"         # a merge commit per task; "ff-only": fast-forward only (linear history)
setup = "uv sync"       # shell command run in a newly created worktree (default: none)
stale_after = "14d"     # an activity branch idle this long is reported by `devkit worktree status --stale` (<N>d or <N>w)
```
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devkit_dist.features.project.repositories.project import config_table, read_project_config
from devkit_dist.features.project.services.config_template import TemplateKey, TemplateTable

from devkit_agt.features.worktree.models.config import PERIOD, WorktreeConfig
from devkit_agt.features.worktree.models.errors import WorktreeConfigError

PULL_REQUEST_POLICIES = ("auto", "required")
MERGE_METHODS = ("no-ff", "ff-only")
KEYS = ("pull_request", "delete_branch", "merge", "setup", "stale_after")
POLICY_PROBLEMS = {
    "pull_request": 'pull_request must be "auto" or "required"',
    "delete_branch": "delete_branch must be true or false",
    "merge": 'merge must be "no-ff" or "ff-only"',
}
# The integration policy keys of ``[worktree]`` and their defaults.
POLICY_DEFAULTS: dict[str, Any] = {"pull_request": "auto", "delete_branch": True, "merge": "no-ff"}


def config_tables() -> tuple[TemplateTable, ...]:
    """The commented ``[worktree]`` template of ``devkit config template``, at the defaults this reader applies.

    Registered under the ``devkit.config_tables`` entry point ``worktree``.
    """
    return (
        TemplateTable(
            (
                TemplateKey(
                    "pull_request",
                    "auto",
                    "auto: a pull request or local integration, as the task needs; required refuses local integration",
                    kind='"auto" | "required"',
                ),
                TemplateKey("delete_branch", True, "worktree finish deletes the merged branch with git branch -d"),
                TemplateKey(
                    "merge",
                    "no-ff",
                    "no-ff: a merge commit per task; ff-only: fast-forward only, wins in either policy",
                    kind='"no-ff" | "ff-only"',
                ),
                TemplateKey(
                    "setup",
                    help="shell command run in a newly created worktree; unset: no setup command",
                    example="uv sync",
                ),
                TemplateKey(
                    "stale_after",
                    "14d",
                    "idle plan-*/dev-* branches are reported by devkit worktree status --stale and hygiene runs",
                    kind='"<N>d" | "<N>w"',
                ),
            ),
            help="Git worktree behavior: integration policy, branch cleanup, setup for new worktrees and stale branches.",
        ),
    )


def worktree_policy(config: dict[str, Any]) -> dict[str, Any] | None:
    """The integration policy of a parsed ``.devkit/config.toml``: ``pull_request``, ``delete_branch`` and ``merge``
    of its ``[worktree]`` table, each at its default when unset; ``None`` when ``worktree`` is not a table.

    Values are not validated: ``invalid_policy_keys`` names the invalid ones and each reader refuses them its own way.
    """
    table = config.get("worktree", {})
    if not isinstance(table, dict):
        return None
    return {key: table.get(key, default) for key, default in POLICY_DEFAULTS.items()}


def invalid_policy_keys(policy: dict[str, Any]) -> list[str]:
    """The keys of a ``worktree_policy`` whose values are invalid, in ``POLICY_DEFAULTS`` order."""
    valid = {
        "pull_request": policy["pull_request"] in PULL_REQUEST_POLICIES,
        "delete_branch": type(policy["delete_branch"]) is bool,
        "merge": policy["merge"] in MERGE_METHODS,
    }
    return [key for key in POLICY_DEFAULTS if not valid[key]]


def read_worktree_config(root: Path) -> WorktreeConfig:
    """The ``[worktree]`` settings of the project at ``root``; defaults when the table or the file is missing."""
    data = read_project_config(root).get("worktree")
    if data is None:
        return WorktreeConfig()
    table = config_table(data, "worktree", WorktreeConfigError)
    unknown = sorted(set(table) - set(KEYS))
    if unknown:
        raise WorktreeConfigError(f"config worktree: unknown fields: {unknown}")
    policy = worktree_policy({"worktree": table})
    assert policy is not None
    invalid = invalid_policy_keys(policy)
    if invalid:
        raise WorktreeConfigError(f"config worktree: {POLICY_PROBLEMS[invalid[0]]}")
    setup = table.get("setup")
    if setup is not None and (not isinstance(setup, str) or not setup.strip()):
        raise WorktreeConfigError("config worktree: setup must be a non-empty shell command")
    stale_after = table.get("stale_after", "14d")
    if not isinstance(stale_after, str) or PERIOD.fullmatch(stale_after) is None:
        raise WorktreeConfigError('config worktree: stale_after must be "<N>d" or "<N>w", such as "14d"')
    return WorktreeConfig(policy["pull_request"], policy["delete_branch"], setup, stale_after, policy["merge"])
