"""Read Git repository identity and worktree facts without index refreshes."""

import re
from pathlib import Path

from devkit_core.core import parse_status_records, parse_worktree_records, run_git, run_git_text
from devkit_core.core.git import run_git_result

from devkit_adaptive.base.errors import RevisionUnresolved, WorktreeUnavailable

_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


def parse_worktrees(raw: bytes) -> dict[Path, dict[str, str]]:
    """Each worktree's present porcelain keys by resolved path; a flag without a reason maps to ``""``."""
    result: dict[Path, dict[str, str]] = {}
    for record in parse_worktree_records(raw):
        fields = {"worktree": str(record.path)}
        for key, value in (
            ("HEAD", record.head),
            ("branch", record.branch),
            ("bare", "" if record.bare else None),
            ("detached", "" if record.detached else None),
            ("locked", record.locked),
            ("prunable", record.prunable),
        ):
            if value is not None:
                fields[key] = value
        result[record.path.resolve()] = fields
    return result


def parse_status(raw: bytes) -> list[str]:
    """Every name status lists, both names of a rename or copy, without a directory's trailing ``/``."""
    paths: set[str] = set()
    for record in parse_status_records(raw):
        paths.add(record.path.rstrip("/"))
        if record.original is not None:
            paths.add(record.original.rstrip("/"))
    return sorted(paths)


def worktrees(root: Path) -> dict[Path, dict[str, str]]:
    return parse_worktrees(run_git(root, "worktree", "list", "--porcelain", "-z"))


def require_worktree(root: Path, path: Path) -> Path:
    path = path.resolve()
    record = worktrees(root).get(path)
    if not path.is_dir() or record is None or "bare" in record or "prunable" in record:
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
    return parse_status(run_git(root, "--no-optional-locks", "status", "--porcelain=v1", "-z", "--untracked-files=all"))


def committed(root: Path, base: str, final: str) -> list[str]:
    return sorted(
        filter(
            None,
            run_git(root, "diff", "--no-renames", "--name-only", "-z", base, final, "--")
            .decode("utf-8", "surrogateescape")
            .split("\0"),
        )
    )


def head(root: Path) -> str:
    return revision(root, "HEAD")


def count(root: Path, base: str, final: str) -> int:
    return int(run_git_text(root, "rev-list", "--count", f"{base}..{final}"))
