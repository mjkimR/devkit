from __future__ import annotations

from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG

from .reading import read_owned, synchronized_root
from .sync import read_receipt
from .transaction import JOURNAL, project_lock, snapshot


def get_context(start: Path, bundle: str) -> dict[str, object]:
    """Read synchronized constitution and instruction headers without session state."""
    if not SLUG.fullmatch(bundle):
        raise BundleError("bundle: expected a lowercase slug")
    root = synchronized_root(start)
    with project_lock(root):
        if snapshot(root, JOURNAL) is not None:
            raise BundleError("pending transaction; run devkit recover first")
        receipt = read_receipt(root)
        prefix = f".devkit/managed/{bundle}/"
        if prefix + "bundle.toml" not in receipt["files"]:
            raise BundleError(f"bundle is not synchronized: {bundle}")

        def read(name: str) -> str:
            try:
                return read_owned(root, receipt, name).decode("utf-8")
            except UnicodeError as exc:
                raise BundleError(f"context file must be UTF-8: {name}") from exc

        constitution_path = prefix + "AGENTS.md"
        constitution = read(constitution_path) if constitution_path in receipt["files"] else None
        paths = {
            name
            for asset in receipt["assets"]
            if asset["bundle"] == bundle and asset["kind"] == "instruction"
            for name in asset["paths"]
        }
        instructions = []
        for name in sorted(paths):
            if not (name.startswith(prefix) or name.startswith(f".devkit/overrides/{bundle}/")):
                raise BundleError(f"instruction outside bundle: {name}")
            lines = read(name).splitlines(keepends=True)
            if not lines or lines[0].strip() != "---":
                raise BundleError(f"instruction requires YAML frontmatter: {name}")
            end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
            if end is None:
                raise BundleError(f"instruction has unclosed YAML frontmatter: {name}")
            instructions.append({"path": str(root / name), "header": "".join(lines[1:end])})
        return {"bundle": bundle, "constitution": constitution, "instructions": instructions}
