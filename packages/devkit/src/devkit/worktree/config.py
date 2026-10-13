"""The ``[worktree]`` table of ``.devkit/config.toml``.

```toml
[worktree]
pull_request = true     # finish integrates through a pull request; `finish --merge` is refused
delete_branch = true    # finish deletes the merged branch (`git branch -d`, never -D)
setup = "uv sync"       # shell command run in a newly created worktree (default: none)
```
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.core import config_table, read_project_config
from devkit.worktree.errors import WorktreeConfigError


@dataclass(frozen=True)
class WorktreeConfig:
    pull_request: bool = True
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
    for key in ("pull_request", "delete_branch"):
        if key in table and not isinstance(table[key], bool):
            raise WorktreeConfigError(f"config worktree: {key} must be true or false")
    setup = table.get("setup")
    if setup is not None and (not isinstance(setup, str) or not setup.strip()):
        raise WorktreeConfigError("config worktree: setup must be a non-empty shell command")
    return WorktreeConfig(table.get("pull_request", True), table.get("delete_branch", True), setup)
