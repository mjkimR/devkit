"""Receipt records a merge makes inconsistent (``ADR-effective-policy-digest``), and a source the reader cannot read.

A merge commit combines the receipt (``.devkit/installation.json``) and the managed files of both parents. A record
of the merged receipt whose path is tracked in the result and whose ``(recorded hash, blob)`` pair equals neither
parent's was produced by the merge itself; its blob must then match the record. Untracked projections and
inconsistencies already present on a parent are not the integration's and are skipped.

A source that changes the receipt reader may carry a receipt only its own reader accepts; ``check_reader`` names that
case before anything else reads the source's receipt.
"""

from __future__ import annotations

import os
from pathlib import Path

from devkit_core.core.git import run_git
from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.project.repositories.receipt import READER_MODULES, RECEIPT_PATH, Receipt, parse_receipt

from devkit_agt.features.integration.models.errors import ReceiptConflictError, ReceiptReaderChangedError

# Each reader module as a path suffix (``devkit_dist/features/project/repositories/receipt.py``), wherever the
# repository keeps its sources.
_READER_PATHS = tuple(f"{name.replace('.', '/')}.py" for name in READER_MODULES)


def tracked_blob(root: Path, commit: str, path: str) -> bytes | None:
    """The content of ``path`` committed at ``commit``; ``None`` when that commit does not track it.

    Raises ``GitError`` when Git cannot read the commit.
    """
    if not run_git(root, "ls-tree", "--name-only", commit, "--", path).strip():
        return None
    return run_git(root, "cat-file", "blob", f"{commit}:{path}")


def _receipt(root: Path, commit: str) -> Receipt | None:
    raw = tracked_blob(root, commit, RECEIPT_PATH)
    if raw is None:
        return None
    return parse_receipt(raw)


def _reader_path(path: str) -> bool:
    return any(path == suffix or path.endswith(f"/{suffix}") for suffix in _READER_PATHS)


def check_reader(root: Path, source_sha: str, target_sha: str) -> None:
    """Refuse a source whose receipt only a changed reader accepts (``INTEGRATION_RECEIPT_READER_CHANGED``).

    The running reader refuses the source's committed receipt, accepts the target's, and the source's range from the
    merge base changes a reader module (``READER_MODULES``). Any other combination returns and leaves the existing
    outcome, such as ``RECEIPT_INVALID`` for a corrupted receipt. Validation is unchanged: this only names the case.
    """
    try:
        _receipt(root, source_sha)
        return
    except ReceiptError as exc:
        refusal = exc
    try:
        if _receipt(root, target_sha) is None:
            return
    except ReceiptError:
        return
    prior = run_git(root, "merge-base", "--", target_sha, source_sha).decode().strip()
    output = run_git(root, "diff", "--name-only", "--no-renames", "-z", prior, source_sha, "--")
    changed = sorted(path for path in (os.fsdecode(name) for name in output.split(b"\0") if name) if _reader_path(path))
    if changed:
        raise ReceiptReaderChangedError(
            f"the source changes the receipt reader ({', '.join(changed)}) and carries a receipt this runtime's reader"
            f" refuses: {refusal.message}",
            target_files=[RECEIPT_PATH],
        ) from refusal


def _blobs(root: Path, commit: str, paths: list[str]) -> dict[str, str]:
    """The blob id of each of ``paths`` tracked as a regular file at ``commit``."""
    found: dict[str, str] = {}
    if not paths:
        return found
    output = run_git(root, "ls-tree", "-z", "--full-tree", commit, "--", *paths)
    for entry in output.split(b"\0"):
        if not entry:
            continue
        meta, _, name = entry.partition(b"\t")
        mode, kind, sha = meta.decode().split(" ")
        if kind == "blob" and mode in {"100644", "100755"}:
            found[os.fsdecode(name)] = sha
    return found


def check_merge(root: Path, result: str, parents: tuple[str, ...]) -> None:
    """Refuse ``result`` when the merge left a tracked receipt record inconsistent (``INTEGRATION_RECEIPT_CONFLICT``).

    A result without a receipt has no records; a parent without one (or with one that does not parse) contributes no
    records. A merged receipt that does not parse is a conflict.
    """
    try:
        merged = _receipt(root, result)
    except ReceiptError as exc:
        raise ReceiptConflictError(
            f"the merged {RECEIPT_PATH} does not parse; nothing was changed on the target", target_files=[RECEIPT_PATH]
        ) from exc
    if merged is None:
        return
    paths = sorted(merged.file_records)
    tracked = _blobs(root, result, paths)
    sides: list[dict[str, tuple[str | None, str | None]]] = []
    for parent in parents:
        try:
            receipt = _receipt(root, parent)
        except ReceiptError:
            receipt = None
        blobs = _blobs(root, parent, paths) if receipt is not None else {}
        sides.append({path: (receipt.file_hash(path), blobs.get(path)) for path in paths} if receipt else {})
    conflicts = []
    for path in paths:
        blob = tracked.get(path)
        if blob is None:  # an untracked projection (.agents/, .claude/, ...)
            continue
        record = merged.file_records[path]
        if any(side.get(path) == (record.sha256, blob) for side in sides):
            continue
        if not record.matches(run_git(root, "cat-file", "blob", blob)):
            conflicts.append(path)
    if conflicts:
        raise ReceiptConflictError(
            f"the merge leaves {len(conflicts)} receipt record(s) that match neither the merged file nor a parent;"
            " nothing was changed on the target",
            target_files=conflicts,
        )
