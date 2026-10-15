"""The ``[worktree]`` table of ``.devkit/config.toml``.

```toml
[worktree]
pull_request = "auto"   # a pull request or finish --merge, as the task needs; "required": pull requests only
delete_branch = true    # finish deletes the merged branch (`git branch -d`, never -D)
setup = "uv sync"       # shell command run in a newly created worktree (default: none)
```
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.core import config_table, read_project_config
from devkit.worktree.errors import WorktreeConfigError

PULL_REQUEST_POLICIES = ("auto", "required")


@dataclass(frozen=True)
class WorktreeConfig:
    pull_request: str = "auto"
    delete_branch: bool = True
    setup: str | None = None


def read_worktree_config(root: Path) -> WorktreeConfig:
    """The ``[worktree]`` settings of the project at ``root``; defaults when the table or the file is missing."""
    data = read_project_config(root).get("worktree")
    if data is None:
        return WorktreeConfig()
    table = config_table(data, "worktree", WorktreeConfigError)
    unknown = sorted(set(table) - {"pull_request", "delete_branch", "setup"})
    if unknown:
        raise WorktreeConfigError(f"config worktree: unknown fields: {unknown}")
    if table.get("pull_request", "auto") not in PULL_REQUEST_POLICIES:
        raise WorktreeConfigError('config worktree: pull_request must be "auto" or "required"')
    if not isinstance(table.get("delete_branch", True), bool):
        raise WorktreeConfigError("config worktree: delete_branch must be true or false")
    setup = table.get("setup")
    if setup is not None and (not isinstance(setup, str) or not setup.strip()):
        raise WorktreeConfigError("config worktree: setup must be a non-empty shell command")
    return WorktreeConfig(table.get("pull_request", "auto"), table.get("delete_branch", True), setup)
