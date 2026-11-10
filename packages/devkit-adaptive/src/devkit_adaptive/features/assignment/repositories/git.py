"""Read Git repository identity and worktree facts without index refreshes."""

from pathlib import Path

from devkit_core.core import run_git, run_git_text
from devkit_core.core.git import run_git_result

from devkit_adaptive.base.errors import RevisionUnresolved, WorktreeUnavailable


def parse_worktrees(raw: bytes) -> dict[Path, dict[str, str]]:
    result: dict[Path, dict[str, str]] = {}
    record: dict[str, str] = {}
    for item in raw.decode("utf-8", "surrogateescape").split("\0"):
        if not item:
            if "worktree" in record:
                result[Path(record["worktree"]).resolve()] = record
            record = {}
        else:
            key, _, value = item.partition(" ")
            record[key] = value
    return result


def parse_status(raw: bytes) -> list[str]:
    records = iter(raw.decode("utf-8", "surrogateescape").split("\0"))
    paths: set[str] = set()
    for record in records:
        if not record:
            continue
        paths.add(record[3:].rstrip("/"))
        if "R" in record[:2] or "C" in record[:2]:
            paths.add(next(records).rstrip("/"))
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
    result = run_git_result(root, "rev-parse", "--verify", "--quiet", value + "^{commit}", ok_returncodes=(0, 1, 128))
    if result.returncode:
        raise RevisionUnresolved(f"cannot resolve commit {value}")
    return result.stdout.decode().strip()


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
