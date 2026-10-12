"""The subagent role vocabulary a project has: receipt ``subagent`` assets plus ``roles_dir`` contracts.

A stage names a ``role``; ``validate`` requires that role to exist, and
``[DELEGATE]`` cites the contract that defines it. Two sources are merged:

- every ``kind = "subagent"`` asset recorded by ``devkit sync`` in the
  installation receipt (the asset id is the role; its contract path is the
  managed or overridden Markdown contract when one exists, else the first
  projected file), and
- ``<roles_dir>/<role>.md`` files the project authors itself, which shadow
  receipt entries of the same role.

When neither the receipt nor ``roles_dir`` exists the vocabulary is unknown
(``None``) and the role check is skipped, so definitions can be authored
before any bundle is synchronized.
"""

from __future__ import annotations

from pathlib import Path

from devkit.core.errors import FrontmatterError
from devkit.core.receipt import AssetRecord, Receipt, load_receipt
from devkit.workflow import frontmatter
from devkit.workflow.ids import is_ident

BUILTIN_ROLES = ("developer", "-", "")
OVERRIDES_PREFIX = ".devkit/overrides/"
MANAGED_PREFIX = ".devkit/managed/"


def is_builtin_role(role: str) -> bool:
    return role in BUILTIN_ROLES


def _contract_path(asset: AssetRecord) -> str | None:
    """The file that documents the role: a contract under ``.devkit/`` first, else any projected file."""
    markdown = asset.files(".md")
    for prefix in (OVERRIDES_PREFIX, MANAGED_PREFIX):
        for rel in markdown:
            if rel.startswith(prefix):
                return rel
    every = asset.files()
    return sorted(every)[0] if every else None


def receipt_roles(workspace_root: Path, receipt: Receipt | None) -> dict[str, str]:
    """``role -> contract path`` for every subagent asset in the receipt."""
    roles: dict[str, str] = {}
    for asset in receipt.assets("subagent") if receipt is not None else ():
        if not is_ident(asset.id):
            continue
        path = _contract_path(asset) or ""
        roles.setdefault(asset.id, path)
        contract = workspace_root / path if path else None
        if contract is not None and path.endswith(".md") and contract.is_file():
            try:
                declared = frontmatter.field(frontmatter.read(contract), "role")
            except (FrontmatterError, OSError, UnicodeError):
                declared = ""
            if is_ident(declared):
                roles.setdefault(declared, path)
    return roles


def local_roles(workspace_root: Path, roles_dir: str) -> dict[str, str]:
    """``role -> contract path`` for every ``<roles_dir>/<role>.md``."""
    directory = workspace_root / roles_dir
    if not directory.is_dir():
        return {}
    roles: dict[str, str] = {}
    for path in sorted(directory.glob("*.md")):
        if path.is_file() and is_ident(path.stem):
            roles[path.stem] = f"{roles_dir}/{path.name}"
    return roles


def discover_roles(workspace_root: Path, roles_dir: str, receipt: Receipt | None = None) -> dict[str, str] | None:
    """The project's role vocabulary, or ``None`` when no source exists at all.

    ``receipt`` defaults to the workspace's installation receipt; a malformed
    receipt raises ``devkit.core.errors.ReceiptError``.
    """
    if receipt is None:
        receipt = load_receipt(workspace_root)
    if receipt is None and not (workspace_root / roles_dir).is_dir():
        return None
    roles = receipt_roles(workspace_root, receipt)
    roles.update(local_roles(workspace_root, roles_dir))
    return roles
