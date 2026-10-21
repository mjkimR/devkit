"""The ``[worktree]`` table of ``.devkit/config.toml``.

```toml
[worktree]
pull_request = "auto"   # a pull request or finish --merge, as the task needs; "required": pull requests only
delete_branch = true    # finish deletes the merged branch (`git branch -d`, never -D)
merge = "no-ff"         # a merge commit per task; "ff-only": fast-forward only (linear history)
setup = "uv sync"       # shell command run in a newly created worktree (default: none)
stale_after = "14d"     # an activity branch idle this long is reported by `devkit worktree stale` (<N>d or <N>w)
```
"""

from __future__ import annotations

import re
from pathlib import Path

from devkit_dist.features.project.repositories.project import config_table, read_project_config
from devkit_dist.features.project.services.config_template import TemplateKey, TemplateTable

from devkit_agt.features.worktree.models.config import WorktreeConfig as WorktreeConfig
from devkit_agt.features.worktree.models.config import parse_period as parse_period
from devkit_agt.features.worktree.models.errors import WorktreeConfigError

PULL_REQUEST_POLICIES = ("auto", "required")
MERGE_METHODS = ("no-ff", "ff-only")
PERIOD = re.compile(r"([1-9][0-9]{0,3})([dw])")
KEYS = ("pull_request", "delete_branch", "merge", "setup", "stale_after")


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
                    "auto: a pull request or worktree finish --merge, as the task needs; required refuses --merge",
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
                    "idle plan-*/dev-* branches are reported by devkit worktree stale and hygiene runs",
                    kind='"<N>d" | "<N>w"',
                ),
            ),
            help="Git worktree behavior: integration policy, branch cleanup, setup for new worktrees and stale branches.",
        ),
    )


def read_worktree_config(root: Path) -> WorktreeConfig:
    """The ``[worktree]`` settings of the project at ``root``; defaults when the table or the file is missing."""
    data = read_project_config(root).get("worktree")
    if data is None:
        return WorktreeConfig()
    table = config_table(data, "worktree", WorktreeConfigError)
    unknown = sorted(set(table) - set(KEYS))
    if unknown:
        raise WorktreeConfigError(f"config worktree: unknown fields: {unknown}")
    if table.get("pull_request", "auto") not in PULL_REQUEST_POLICIES:
        raise WorktreeConfigError('config worktree: pull_request must be "auto" or "required"')
    if not isinstance(table.get("delete_branch", True), bool):
        raise WorktreeConfigError("config worktree: delete_branch must be true or false")
    if table.get("merge", "no-ff") not in MERGE_METHODS:
        raise WorktreeConfigError('config worktree: merge must be "no-ff" or "ff-only"')
    setup = table.get("setup")
    if setup is not None and (not isinstance(setup, str) or not setup.strip()):
        raise WorktreeConfigError("config worktree: setup must be a non-empty shell command")
    stale_after = table.get("stale_after", "14d")
    if not isinstance(stale_after, str) or PERIOD.fullmatch(stale_after) is None:
        raise WorktreeConfigError('config worktree: stale_after must be "<N>d" or "<N>w", such as "14d"')
    return WorktreeConfig(
        table.get("pull_request", "auto"),
        table.get("delete_branch", True),
        setup,
        stale_after,
        table.get("merge", "no-ff"),
    )
