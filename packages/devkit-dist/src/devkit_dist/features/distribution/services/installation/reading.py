"""Reading receipt-recorded files for agents (context, playbook search and retrieval)."""

from __future__ import annotations

from pathlib import Path

from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.distribution.models.content import signature
from devkit_dist.features.distribution.models.errors import NotSynchronizedError
from devkit_dist.features.distribution.services.bundles.playbooks import PlaybookHeader, read_playbook_header
from devkit_dist.features.distribution.services.installation.local_render import runtime_receipt
from devkit_dist.features.distribution.services.installation.overrides import override_rel
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.transaction import require_no_journal
from devkit_dist.features.distribution.services.installation.workspace import checked_path, snapshot
from devkit_dist.features.project.repositories.project import find_project_root
from devkit_dist.features.project.repositories.receipt import (
    MANAGED_PATH,
    OVERRIDES_PATH,
    RECEIPT_PATH,
    AssetRecord,
    Receipt,
)


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
    return runtime_receipt(root, receipt)


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


def read_playbook(root: Path, receipt: Receipt, asset: AssetRecord, name: str) -> tuple[PlaybookHeader, bytes]:
    """The playbook entrypoint ``name`` of ``asset`` as ``read_owned`` reads it: its validated header and its bytes.

    An overridden playbook is read from its override, never from the managed copy. ``RECEIPT_INVALID`` when the
    receipt records ``name`` outside the asset's paths, or outside the bundle's managed and override directories.
    """
    if (
        not name.startswith((f"{MANAGED_PATH}/{asset.bundle}/", override_rel(asset.bundle, "")))
        or name not in asset.paths
    ):
        raise ReceiptError(f"{RECEIPT_PATH}: invalid playbook entrypoint: {name}")
    data = read_owned(root, receipt, name)
    return read_playbook_header(data, name), data
