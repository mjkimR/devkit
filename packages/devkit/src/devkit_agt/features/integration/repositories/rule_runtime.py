"""Synchronized rules that import code the running runtime does not provide (``INTEGRATION_RULE_RUNTIME_MISMATCH``).

Readiness runs in the retained base checkout and imports the source's receipt-listed rule packages with that
checkout's installed code. A synchronized rule is often a shim importing its implementation from a package module; a
source that adds the rule with its module, or upgrades to a release whose new rule needs new code, carries a rule this
runtime cannot load. ``check_rule_runtime`` names that case before the provider runs, without executing source code:
it parses each rule module and resolves its module-level absolute imports against the running interpreter only.

An import is missing when its top-level package resolves here but the module does not, or when ``from M import name``
names neither a submodule nor an attribute of ``M``. Anything else (a top-level package nothing provides, a file that
cannot be read or parsed, relative and ``__future__`` imports, imports inside functions or blocks) is left to the
provider's own ``RULES_LOAD_FAILED``.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from collections.abc import Iterator, Sequence
from pathlib import Path, PurePosixPath

from devkit_core.core.git import run_git
from devkit_core.core.plugins import plugin_module_name
from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.project.models.receipt import AssetRecord, Receipt
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH, parse_receipt

from devkit_agt.features.integration.models.errors import RuleRuntimeMismatchError

RULE_KIND = "rule"
_BUNDLE_ROOTS = (".devkit/managed", ".devkit/overrides")


def _tracked(root: Path, commit: str, path: str) -> bytes | None:
    if not run_git(root, "ls-tree", "--name-only", commit, "--", path).strip():
        return None
    return run_git(root, "cat-file", "blob", f"{commit}:{path}")


def _receipt(root: Path, commit: str) -> Receipt | None:
    raw = _tracked(root, commit, RECEIPT_PATH)
    if raw is None:
        return None
    try:
        return parse_receipt(raw)
    except ReceiptError:
        return None


def _is_module(asset: AssetRecord, path: str) -> bool:
    """Whether ``path`` is one of the asset's plugin modules (tests and non-Python files are not)."""
    relative = path
    for prefix in (f"{base}/{asset.bundle}/" for base in _BUNDLE_ROOTS):
        if path.startswith(prefix):
            relative = path[len(prefix) :]
            break
    return plugin_module_name(PurePosixPath(relative).as_posix()) is not None


def _source(root: Path, commit: str, receipt: Receipt, path: str, sources: Sequence[Path]) -> bytes | None:
    """The bytes the rule gate would load: the commit's file, else a working copy matching the receipt's hash."""
    data = _tracked(root, commit, path)
    if data is not None:
        return data
    record = receipt.file(path)
    if record is None:
        return None
    for source in sources:
        candidate = source / path
        try:
            if candidate.is_symlink() or not candidate.is_file():
                continue
            data = candidate.read_bytes()
        except OSError:
            continue
        if record.matches(data):
            return data
    return None


def _imports(data: bytes) -> Iterator[tuple[str, tuple[str, ...]]]:
    """Each module-level absolute import as ``(module, names)``; ``names`` is empty for ``import M``."""
    try:
        tree = ast.parse(data)
    except (SyntaxError, ValueError):
        return
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, ()
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module and node.module != "__future__":
            yield node.module, tuple(alias.name for alias in node.names if alias.name != "*")


def _resolves(name: str) -> bool | None:
    """Whether ``name`` resolves in this runtime; ``None`` when that cannot be decided."""
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False
    except (ImportError, ValueError):
        return None


def _missing(module: str, names: tuple[str, ...]) -> list[str]:
    """The imports of one statement this runtime lacks, for a top-level package it provides."""
    if _resolves(module.partition(".")[0]) is not True:
        return []
    found = _resolves(module)
    if found is False:
        return [module]
    if found is None or not names:
        return []
    try:
        loaded = importlib.import_module(module)
    except ImportError:
        return [module]
    except Exception:
        return []
    return [
        f"{module}.{name}" for name in names if not hasattr(loaded, name) and _resolves(f"{module}.{name}") is False
    ]


def check_rule_runtime(root: Path, commit: str, sources: Sequence[Path]) -> None:
    """Refuse ``commit`` when a synchronized rule imports code this runtime lacks (``INTEGRATION_RULE_RUNTIME_MISMATCH``).

    ``sources`` are the working trees a Git-ignored managed rule file is read from, in order, when its bytes match the
    hash in the commit's receipt. A commit without a readable receipt or rule asset has nothing to check.
    """
    receipt = _receipt(root, commit)
    if receipt is None:
        return
    found: list[tuple[str, str]] = []
    for asset in receipt.assets(RULE_KIND):
        for path in asset.files():
            if not _is_module(asset, path):
                continue
            data = _source(root, commit, receipt, path, sources)
            if data is None:
                continue
            for module, names in _imports(data):
                found.extend((path, missing) for missing in _missing(module, names))
    if found:
        listed = "; ".join(f"{path} imports {missing}" for path, missing in found)
        raise RuleRuntimeMismatchError(
            f"the source's synchronized rules import code this runtime does not provide: {listed}",
            target_files=sorted({path for path, _ in found}),
        )
