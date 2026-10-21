"""Receipt records a merge makes inconsistent (``ADR-effective-policy-digest``).

A merge commit combines the receipt (``.devkit/installation.json``) and the managed files of both parents. A record
of the merged receipt whose path is tracked in the result and whose ``(recorded hash, blob)`` pair equals neither
parent's was produced by the merge itself; its blob must then match the record. Untracked projections and
inconsistencies already present on a parent are not the integration's and are skipped.
"""

from __future__ import annotations

import os
from pathlib import Path

from devkit_core.core.git import run_git

from devkit.core.errors import ReceiptError
from devkit.core.receipt import RECEIPT_PATH, Receipt, parse_receipt
from devkit.integration.errors import ReceiptConflictError


def _blob(root: Path, commit: str, path: str) -> bytes | None:
    if not run_git(root, "ls-tree", "--name-only", commit, "--", path).strip():
        return None
    return run_git(root, "cat-file", "blob", f"{commit}:{path}")


def _receipt(root: Path, commit: str) -> Receipt | None:
    raw = _blob(root, commit, RECEIPT_PATH)
    if raw is None:
        return None
    return parse_receipt(raw)


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
