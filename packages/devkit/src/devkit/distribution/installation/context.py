"""``devkit get-context``: a bundle's constitution and instruction header catalog."""

from __future__ import annotations

from pathlib import Path

from ..bundles.common import SLUG, BundleError
from ..bundles.instructions import read_instruction_header
from .overrides import override_rel
from .reading import read_owned, read_synchronized, synchronized_root
from .results import ContextResult, InstructionJSON
from .transaction import project_lock
from .workspace import MANAGED


def get_context(start: Path, bundle: str) -> ContextResult:
    """Read the synchronized constitution and instruction headers; bodies are never returned."""
    if not SLUG.fullmatch(bundle):
        raise BundleError("bundle: expected a lowercase slug")
    root = synchronized_root(start)
    with project_lock(root, shared=True):
        receipt = read_synchronized(root)
        prefix = f"{MANAGED}/{bundle}/"
        if receipt.file(prefix + "bundle.toml") is None:
            raise BundleError(f"bundle is not synchronized: {bundle}")

        def read(name: str) -> bytes:
            return read_owned(root, receipt, name)

        constitution_path = prefix + "AGENTS.md"
        constitution = None
        if receipt.file(constitution_path) is not None:
            try:
                constitution = read(constitution_path).decode("utf-8")
            except UnicodeError as exc:
                raise BundleError(f"context file must be UTF-8: {constitution_path}") from exc
        paths = {name for asset in receipt.assets("instruction") if asset.bundle == bundle for name in asset.paths}
        instructions: list[InstructionJSON] = []
        for name in sorted(paths):
            if not (name.startswith(prefix) or name.startswith(override_rel(bundle, ""))):
                raise BundleError(f"instruction outside bundle: {name}")
            instructions.append({"path": str(root / name), "header": read_instruction_header(read(name), name)})
        return {"bundle": bundle, "constitution": constitution, "instructions": instructions}
