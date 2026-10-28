"""Committed integration snapshot and matching managed asset inputs."""

from collections.abc import Sequence
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.core import is_safe_relpath, run_git
from devkit_dist.features.project.repositories.receipt import load_receipt

from devkit_agt.features.rules import Snapshot

REGULAR_MODES = {"100644", "100755"}
SYMLINK_MODE = "120000"
GITLINK_MODE = "160000"


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


def _snapshot_root(base: Path, worktree: Path) -> Path:
    if worktree.is_dir() and (worktree / ".devkit" / "managed").is_dir():
        return worktree.resolve()
    return base.resolve()


def build_snapshot(root: Path, source_sha: str, target_sha: str, result_sha: str | None = None) -> Snapshot:
    """The tree to check and its diff: the source from the merge base, or the result from the build target."""
    tree = run_git(root, "rev-parse", "--verify", "--quiet", f"{result_sha or source_sha}^{{tree}}").decode().strip()
    prior = target_sha if result_sha else run_git(root, "merge-base", "--", target_sha, source_sha).decode().strip()
    output = run_git(root, "diff", "--name-status", "-z", "--no-renames", prior, tree, "--")
    parts = [part for part in output.split(b"\0") if part]
    changed: list[str] = []
    deleted: list[str] = []
    for status, name in zip(parts[0::2], parts[1::2], strict=True):
        path = _decode(name)
        changed.append(path)
        if status.startswith(b"D"):
            deleted.append(path)
    files: list[tuple[str, str, str]] = []
    regular: set[str] = set()
    for entry in run_git(root, "ls-tree", "-r", "--full-tree", "-z", tree).split(b"\0"):
        if not entry:
            continue
        meta, _, raw_path = entry.partition(b"\t")
        file_mode, _kind, sha = meta.decode().split(" ")
        name = _decode(raw_path)
        if file_mode not in REGULAR_MODES | {SYMLINK_MODE, GITLINK_MODE} or not is_safe_relpath(name, canonical=True):
            continue
        files.append((name, sha, file_mode))
        if file_mode in REGULAR_MODES:
            regular.add(name)
    return Snapshot(
        root=root,
        mode="ci",
        tree=tree,
        base=prior,
        changed=tuple(path for path in changed if path in regular),
        deleted=tuple(deleted),
        files=tuple(files),
    )


def populate_managed_files(workspace: Path, sources: Sequence[Path]) -> None:
    try:
        receipt = load_receipt(workspace)
    except AdvisoryError:
        return
    if receipt is None:
        return
    for rel, record in receipt.file_records.items():
        dest = workspace / rel
        if dest.exists() or dest.is_symlink():
            continue
        for src in sources:
            candidate = src / rel
            try:
                if not candidate.is_file() or candidate.is_symlink():
                    continue
                data = candidate.read_bytes()
                if not record.matches(data):
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                if record.mode == 0o755:
                    dest.chmod(0o755)
                break
            except OSError:
                continue
