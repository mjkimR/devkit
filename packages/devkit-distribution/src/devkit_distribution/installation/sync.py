from __future__ import annotations

import re
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG

from .discovery import InstalledBundle
from .inventory import AGENTS, Content, desired_inventory
from .transaction import (
    JOURNAL,
    RECEIPT,
    apply_changes,
    json_content,
    project_lock,
    project_path,
    read_json,
    recover_locked,
    signature,
    snapshot,
)


def read_receipt(root: Path) -> dict:
    receipt = read_json(root, RECEIPT)
    if not receipt:
        if snapshot(root, RECEIPT) is not None:
            raise BundleError("invalid empty installation receipt")
        return {}
    if (
        set(receipt) != {"schema", "packages", "selection", "assets", "files"}
        or type(receipt["schema"]) is not int
        or receipt["schema"] != 1
    ):
        raise BundleError("unsupported installation receipt")
    files = receipt["files"]
    if not isinstance(files, dict):
        raise BundleError("invalid receipt files")
    for name, meta in files.items():
        if name in {RECEIPT, JOURNAL}:
            raise BundleError("receipt cannot own installation metadata")
        project_path(root, name)
        if (
            not isinstance(meta, dict)
            or set(meta) != {"sha256", "mode"}
            or not isinstance(meta["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", meta["sha256"])
            or type(meta["mode"]) is not int
            or meta["mode"] not in {0o644, 0o755}
        ):
            raise BundleError(f"invalid receipt hash/mode: {name}")
    selection = receipt["selection"]
    if not isinstance(selection, dict) or set(selection) != {"agents", "presets"}:
        raise BundleError("invalid receipt selection")
    agents, presets = selection["agents"], selection["presets"]
    if not isinstance(agents, list) or not all(isinstance(v, str) and v in AGENTS for v in agents):
        raise BundleError("invalid receipt agents")
    if not isinstance(presets, dict) or not all(
        isinstance(k, str) and SLUG.fullmatch(k) and isinstance(v, str) and SLUG.fullmatch(v)
        for k, v in presets.items()
    ):
        raise BundleError("invalid receipt presets")
    if not isinstance(receipt["packages"], list) or not isinstance(receipt["assets"], list):
        raise BundleError("invalid receipt catalog")
    return receipt


def sync_project(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, str] | None = None,
    all_assets: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    with project_lock(root):
        if snapshot(root, JOURNAL) is not None:
            raise BundleError("pending transaction; run devkit recover first")
        previous = read_receipt(root)
        selection = previous.get("selection", {"agents": [], "presets": {}})
        active_agents = sorted(set(agents if agents is not None else selection["agents"]))
        names = {item.bundle.name for item in installed}
        active_presets = {} if all_assets else {k: v for k, v in selection["presets"].items() if k in names}
        active_presets.update(presets or {})
        desired, assets, packages = desired_inventory(installed, active_presets, active_agents)
        old_files = previous.get("files", {})
        changes: dict[str, Content | None] = {}
        actions = []
        for name in sorted(old_files.keys() | desired.keys()):
            current = snapshot(root, name)
            after = desired.get(name)
            if name in old_files:
                if current is not None and signature(current) != old_files[name]:
                    raise BundleError(f"user-modified deployment file: {name}")
            elif current is not None:
                raise BundleError(f"unowned destination already exists: {name}")
            if current != after:
                changes[name] = after
                actions.append(
                    {"path": name, "action": "remove" if after is None else ("create" if current is None else "update")}
                )
        receipt = {
            "schema": 1,
            "packages": packages,
            "selection": {"agents": active_agents, "presets": active_presets},
            "assets": assets,
            "files": {name: signature(content) for name, content in sorted(desired.items())},
        }
        # Preserve exact receipt bytes on a no-op (including a fresh checkout restore).
        if receipt != previous:
            changes[RECEIPT] = json_content(receipt)
            actions.append({"path": RECEIPT, "action": "update" if previous else "create"})
        if not dry_run:
            apply_changes(root, changes)
        return {"dry_run": dry_run, "packages": packages, "assets": assets, "actions": actions}


def recover_project(root: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    with project_lock(root):
        return recover_locked(root)
