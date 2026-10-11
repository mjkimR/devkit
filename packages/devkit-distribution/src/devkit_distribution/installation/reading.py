from __future__ import annotations

from pathlib import Path

from devkit_distribution.bundles import BundleError

from .transaction import RECEIPT, signature, snapshot


def synchronized_root(start: Path) -> Path:
    start = start.resolve()
    root = next((path for path in (start, *start.parents) if (path / RECEIPT).exists()), None)
    if root is None:
        raise BundleError("no synchronized project found; run devkit sync first")
    return root


def read_owned(root: Path, receipt: dict, name: str) -> bytes:
    content = snapshot(root, name)
    if content is None or signature(content) != receipt["files"].get(name):
        raise BundleError(f"missing or modified context file: {name}; reconcile with devkit sync")
    return content.data
