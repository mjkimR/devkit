"""Read Git repository identity and worktree facts without index refreshes."""

import re
from pathlib import Path

from devkit_core.core import changed_paths, dirty_paths, run_git_text, worktree_records
from devkit_core.core.git import run_git_result

from devkit_adaptive.base.errors import RevisionUnresolved, WorktreeUnavailable

_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


def require_worktree(root: Path, path: Path) -> Path:
    path = path.resolve()
    record = {item.path.resolve(): item for item in worktree_records(root)}.get(path)
    if not path.is_dir() or record is None or record.bare or record.prunable is not None:
        raise WorktreeUnavailable(f"assignment worktree is unavailable: {path}")
    return path


def revision(root: Path, value: str) -> str:
    result = run_git_result(
        root, "rev-parse", "--verify", "--quiet", "--end-of-options", value + "^{commit}", ok_returncodes=(0, 1, 128)
    )
    commit = result.stdout.decode("utf-8", "replace").strip()
    # A leading ``^`` makes rev-parse print ``^<id>``: only a bare full ID is a commit.
    if result.returncode or not _COMMIT.fullmatch(commit):
        raise RevisionUnresolved(f"cannot resolve commit {value}")
    return commit


def dirty(root: Path) -> list[str]:
    """Every name status lists, both names of a rename or copy, without a directory's trailing ``/``."""
    return sorted({path.rstrip("/") for path in dirty_paths(root)})


def committed(root: Path, base: str, final: str) -> list[str]:
    return sorted(changed_paths(root, base, final))


def head(root: Path) -> str:
    return revision(root, "HEAD")


def count(root: Path, base: str, final: str) -> int:
    return int(run_git_text(root, "rev-list", "--count", f"{base}..{final}"))
