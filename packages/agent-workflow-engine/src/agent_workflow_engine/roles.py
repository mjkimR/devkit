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

import re
from pathlib import Path

from agent_workflow_engine import frontmatter
from agent_workflow_engine.receipt import asset_paths, receipt_assets, receipt_exists

ROLE_ID = re.compile(r"^[a-z][a-z0-9-]*$")
BUILTIN_ROLES = ("developer", "-", "")
OVERRIDES_PREFIX = ".devkit/overrides/"
MANAGED_PREFIX = ".devkit/managed/"


def is_builtin_role(role: str) -> bool:
    return role in BUILTIN_ROLES


def _contract_path(asset: dict) -> str | None:
    """The file that documents the role: a contract under ``.devkit/`` first, else any projected file."""
    markdown = asset_paths(asset, ".md")
    for prefix in (OVERRIDES_PREFIX, MANAGED_PREFIX):
        for rel in markdown:
            if rel.startswith(prefix):
                return rel
    every = asset_paths(asset, "")
    return sorted(every)[0] if every else None


def receipt_roles(workspace_root: Path) -> dict[str, str]:
    """``role -> contract path`` for every subagent asset in the receipt."""
    roles: dict[str, str] = {}
    for asset in receipt_assets(workspace_root, "subagent"):
        role = asset.get("id")
        if not isinstance(role, str) or not ROLE_ID.match(role):
            continue
        path = _contract_path(asset) or ""
        roles.setdefault(role, path)
        contract = workspace_root / path if path else None
        if contract is not None and path.endswith(".md") and contract.is_file():
            try:
                declared = frontmatter.field(frontmatter.read(contract), "role")
            except (frontmatter.FrontmatterError, OSError, UnicodeError):
                declared = ""
            if declared and ROLE_ID.match(declared):
                roles.setdefault(declared, path)
    return roles


def local_roles(workspace_root: Path, roles_dir: str) -> dict[str, str]:
    """``role -> contract path`` for every ``<roles_dir>/<role>.md``."""
    directory = workspace_root / roles_dir
    if not directory.is_dir():
        return {}
    roles: dict[str, str] = {}
    for path in sorted(directory.glob("*.md")):
        if path.is_file() and ROLE_ID.match(path.stem):
            roles[path.stem] = f"{roles_dir}/{path.name}"
    return roles


def discover_roles(workspace_root: Path, roles_dir: str) -> dict[str, str] | None:
    """The project's role vocabulary, or ``None`` when no source exists at all."""
    has_dir = (workspace_root / roles_dir).is_dir()
    if not has_dir and not receipt_exists(workspace_root):
        return None
    roles = receipt_roles(workspace_root)
    roles.update(local_roles(workspace_root, roles_dir))
    return roles
