from __future__ import annotations

import re
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG

from .config import parse_presets, read_config
from .discovery import InstalledBundle
from .inventory import AGENTS, Content, desired_inventory
from .transaction import (
    CONFIG,
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

MANAGED = ".devkit/managed"


def stray_managed_files(root: Path, owned: set[str]) -> list[str]:
    """Files under the managed root that neither the receipt nor the desired inventory owns.

    The managed root is a regenerated cache; a file placed there by hand is
    never deployed, never removed, and may be picked up by consumers that scan
    the directory (such as rule loading). It is reported, not deleted.
    """
    managed = root / MANAGED
    if not managed.is_dir():
        return []
    stray = []
    for path in sorted(managed.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel not in owned:
            stray.append(rel)
    return stray


def read_receipt(root: Path) -> dict:
    receipt = read_json(root, RECEIPT)
    if not receipt:
        if snapshot(root, RECEIPT) is not None:
            raise BundleError("invalid empty installation receipt")
        return {}
    valid_keys = {"schema", "packages", "selection", "assets", "files", "overrides"}
    if (
        not ({"schema", "packages", "selection", "assets", "files"} <= set(receipt) <= valid_keys)
        or type(receipt["schema"]) is not int
        or receipt["schema"] != 1
    ):
        raise BundleError("unsupported installation receipt")
    files = receipt["files"]
    if not isinstance(files, dict):
        raise BundleError("invalid receipt files")
    for name, meta in files.items():
        if name in {RECEIPT, JOURNAL, CONFIG} or name.startswith(".devkit/overrides/"):
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
    if not isinstance(presets, dict) or not all(isinstance(v, list) for v in presets.values()):
        raise BundleError("invalid receipt presets")
    parse_presets(presets, "receipt")
    if not isinstance(receipt["packages"], list) or not isinstance(receipt["assets"], list):
        raise BundleError("invalid receipt catalog")
    if "overrides" in receipt:
        overrides = receipt["overrides"]
        if not isinstance(overrides, dict):
            raise BundleError("invalid receipt overrides")
        for b_name, b_meta in overrides.items():
            if not (isinstance(b_name, str) and SLUG.fullmatch(b_name) and isinstance(b_meta, dict)):
                raise BundleError("invalid receipt overrides")
            for a_id, meta in b_meta.items():
                if (
                    not (isinstance(a_id, str) and SLUG.fullmatch(a_id))
                    or not isinstance(meta, dict)
                    or set(meta) != {"kind", "relative_path", "baseline_upstream_sha256", "override_sha256"}
                    or not isinstance(meta["kind"], str)
                    or not isinstance(meta["relative_path"], str)
                    or not (
                        isinstance(meta["baseline_upstream_sha256"], str)
                        and re.fullmatch(r"[0-9a-f]{64}", meta["baseline_upstream_sha256"])
                    )
                    or not (
                        isinstance(meta["override_sha256"], str)
                        and re.fullmatch(r"[0-9a-f]{64}", meta["override_sha256"])
                    )
                ):
                    raise BundleError("invalid receipt overrides")
    return receipt


def sync_project(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    dry_run: bool = False,
) -> dict[str, object]:
    """Deploy the bundles selected in ``config.toml``.

    ``agents``, ``presets`` (per-bundle replacements) and ``deselect`` layer
    one-run selections over the configuration; callers persist them separately.
    """
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    with project_lock(root):
        if snapshot(root, JOURNAL) is not None:
            raise BundleError("pending transaction; run devkit recover first")
        config = read_config(root)
        previous = read_receipt(root)
        active_agents = sorted(set(agents)) if agents is not None else config.agents
        active_presets = {**config.presets, **(presets or {})}
        for name in deselect:
            active_presets.pop(name, None)
        available = {item.bundle.name for item in installed}
        missing = sorted(set(active_presets) - available)
        if missing:
            raise BundleError(
                f"selected bundle is not installed: {missing}; install its package or run 'devkit remove <bundle>'"
            )
        active_presets = {name: sorted(set(values)) for name, values in sorted(active_presets.items())}
        selected = [item for item in installed if item.bundle.name in active_presets]
        desired, assets, packages, overrides_record, drift_list, unprojected = desired_inventory(
            selected,
            active_presets,
            active_agents,
            root=root,
            previous_overrides=previous.get("overrides"),
        )
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
        if overrides_record:
            receipt["overrides"] = overrides_record
        # Preserve exact receipt bytes on a no-op (including a fresh checkout restore).
        if receipt != previous:
            changes[RECEIPT] = json_content(receipt)
            actions.append({"path": RECEIPT, "action": "update" if previous else "create"})
        if not dry_run:
            apply_changes(root, changes)
        return {
            "dry_run": dry_run,
            "stray": stray_managed_files(root, old_files.keys() | desired.keys()),
            "selection": receipt["selection"],
            "packages": packages,
            "assets": assets,
            "actions": actions,
            "drift": drift_list,
            "unprojected": unprojected,
            "unselected": [
                {
                    "bundle": item.bundle.name,
                    "package": item.package,
                    "presets": item.bundle.preset_names,
                    "default_preset": item.bundle.default_preset,
                }
                for item in installed
                if item.bundle.name not in active_presets
            ],
        }


def recover_project(root: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    with project_lock(root):
        return recover_locked(root)
