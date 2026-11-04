"""Installation ownership used only to omit generated entrypoint candidates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, RECEIPT_PATH, load_receipt


def _known_output(path: str) -> bool:
    return path in (RECEIPT_PATH, MANAGED_PATH) or path.startswith(f"{MANAGED_PATH}/")


@dataclass(frozen=True)
class ManagedOutputs:
    """Receipt-owned files and output-only directories; authored siblings remain eligible."""

    root: Path
    files: frozenset[str]

    def contains(self, path: str) -> bool:
        """Whether a normalized candidate consists exclusively of managed outputs.

        An unowned symlink is authored, including one pointing at a directory. A directory needs at least one
        receipt-owned descendant before inspecting its leaves, so unrelated source directories are never scanned.
        """
        if _known_output(path) or path in self.files:
            return True
        if not any(owned.startswith(f"{path}/") for owned in self.files):
            return False
        directory = self.root / path
        if directory.is_symlink():
            return False
        if not directory.exists():
            return True
        if not directory.is_dir():
            return False
        for leaf in directory.rglob("*"):
            if leaf.is_symlink() or not leaf.is_dir():
                relative = leaf.relative_to(self.root).as_posix()
                if not _known_output(relative) and relative not in self.files:
                    return False
        return True


def load_managed_outputs(root: Path) -> ManagedOutputs:
    """Known outputs remain excluded without a receipt; a malformed present receipt raises ReceiptError."""
    receipt = load_receipt(root)
    return ManagedOutputs(root, frozenset(receipt.file_records) if receipt is not None else frozenset())
