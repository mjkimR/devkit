"""Reading receipt-recorded files for agents (context, playbook search)."""

from __future__ import annotations

from pathlib import Path

from devkit.core.receipt import Receipt

from ..bundles.common import BundleError
from .receipt import read_receipt
from .transaction import require_no_journal
from .workspace import OVERRIDES, RECEIPT, checked_path, signature, snapshot


def synchronized_root(start: Path) -> Path:
    """The nearest directory at or above ``start`` with a receipt."""
    start = start.resolve()
    root = next((path for path in (start, *start.parents) if (path / RECEIPT).exists()), None)
    if root is None:
        raise BundleError("no synchronized project found; run devkit sync first")
    return root


def read_synchronized(root: Path) -> Receipt:
    """The receipt of a synchronized project; call while holding the project lock."""
    require_no_journal(root)
    receipt = read_receipt(root)
    if receipt is None:
        raise BundleError("no synchronized project found; run devkit sync first")
    return receipt


def read_owned(root: Path, receipt: Receipt, name: str) -> bytes:
    """A file the receipt records: a project override as it is, any other file only while it matches its hash."""
    if name.startswith(f"{OVERRIDES}/"):
        path = checked_path(root, name)
        if not path.is_file():
            raise BundleError(f"missing override file: {name}; reconcile with devkit sync")
        return path.read_bytes()
    content = snapshot(root, name)
    record = receipt.file(name)
    if content is None or record is None or signature(content) != (record.sha256, record.mode):
        raise BundleError(f"missing or modified context file: {name}; reconcile with devkit sync")
    return content.data
