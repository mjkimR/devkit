"""Workflow anchor ownership from committed frontmatter, without loading workflow definitions."""

from pathlib import Path, PurePosixPath

from devkit_core.core import FrontmatterError, GitError, run_git
from devkit_core.core.frontmatter import parse


def workflow_ids(data: dict) -> tuple[str, ...]:
    current = data.get("workflow")
    history = data.get("workflow_history", [])
    return tuple(
        [
            *([current] if isinstance(current, str) and current else []),
            *[item["workflow"] for item in history if isinstance(item, dict) and isinstance(item.get("workflow"), str)],
        ]
    )


def committed_anchors(root: Path, revision: str) -> dict[str, tuple[str, ...]]:
    try:
        names = run_git(
            root, "grep", "-l", "-z", "-e", "^workflow:", "-e", "^workflow_history:", revision, "--", "*.md"
        )
    except GitError as exc:
        if exc.returncode == 1:
            return {}
        raise
    result = {}
    for name in names.decode("utf-8", errors="surrogateescape").split("\0"):
        if not name:
            continue
        path = name.removeprefix(revision + ":")
        try:
            data = parse(run_git(root, "show", f"{revision}:{path}").decode("utf-8")).data or {}
        except (FrontmatterError, UnicodeError):
            continue
        if ids := workflow_ids(data):
            result[path] = ids
    return result


def touched_owners(anchors: dict[str, tuple[str, ...]], changed: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                str(PurePosixPath(anchor).parent)
                for anchor in anchors
                if any(path == anchor or path.startswith(str(PurePosixPath(anchor).parent) + "/") for path in changed)
            }
        )
    )
