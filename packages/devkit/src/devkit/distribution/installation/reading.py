"""Reading receipt-recorded files for agents (context, playbook search)."""

from __future__ import annotations

from pathlib import Path

from devkit.core.project import find_project_root
from devkit.core.receipt import OVERRIDES_PATH, RECEIPT_PATH, Receipt
from devkit.distribution.content import signature
from devkit.distribution.errors import NotSynchronizedError
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.transaction import require_no_journal
from devkit.distribution.installation.workspace import checked_path, snapshot


def synchronized_project_root(start: Path) -> Path:
    """The project root of ``start`` (``find_project_root``); ``NotSynchronizedError`` when it has no receipt.

    Checked before the project lock is taken, which would create ``.devkit/``.
    """
    root = find_project_root(start)
    if not (root / RECEIPT_PATH).exists():
        raise NotSynchronizedError(f"no synchronized project at {root}: {RECEIPT_PATH} does not exist")
    return root


def read_synchronized(root: Path) -> Receipt:
    """The receipt of a synchronized project; call while holding the project lock."""
    require_no_journal(root)
    receipt = read_receipt(root)
    if receipt is None:
        raise NotSynchronizedError(f"no synchronized project at {root}: {RECEIPT_PATH} does not exist")
    return receipt


def read_owned(root: Path, receipt: Receipt, name: str) -> bytes:
    """A file the receipt records: a project override as it is, any other file only while it matches its hash."""
    if name.startswith(f"{OVERRIDES_PATH}/"):
        path = checked_path(root, name)
        if not path.is_file():
            raise NotSynchronizedError(f"missing override file: {name}", target_files=[name])
        return path.read_bytes()
    content = snapshot(root, name)
    record = receipt.file(name)
    if content is None or record is None or signature(content) != (record.sha256, record.mode):
        raise NotSynchronizedError(f"missing or modified context file: {name}", target_files=[name])
    return content.data
