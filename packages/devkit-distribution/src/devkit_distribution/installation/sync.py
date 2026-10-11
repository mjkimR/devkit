from __future__ import annotations

import re
import tomllib
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG

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
    if not isinstance(presets, dict) or not all(
        isinstance(k, str) and SLUG.fullmatch(k) and isinstance(v, str) and SLUG.fullmatch(v)
        for k, v in presets.items()
    ):
        raise BundleError("invalid receipt presets")
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


def read_config(root: Path) -> tuple[list[str] | None, dict[str, str] | None]:
    path = root / CONFIG
    if not path.is_file():
        return None, None
    try:
        data = tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BundleError(f"invalid config: {exc}") from exc
    if not isinstance(data, dict):
        raise BundleError("config: expected a table")
    allowed = {"schema", "agents", "presets", "selection"}
    unknown = set(data) - allowed
    if unknown:
        raise BundleError(f"config: unknown fields: {sorted(unknown)}")
    if "schema" in data and (type(data["schema"]) is not int or data["schema"] != 1):
        raise BundleError("unsupported config schema")
    agents = data.get("agents")
    presets = data.get("presets")
    if "selection" in data:
        selection = data["selection"]
        if not isinstance(selection, dict):
            raise BundleError("config selection: expected a table")
        unknown_sel = set(selection) - {"agents", "presets"}
        if unknown_sel:
            raise BundleError(f"config selection: unknown fields: {sorted(unknown_sel)}")
        if agents is None and "agents" in selection:
            agents = selection["agents"]
        if presets is None and "presets" in selection:
            presets = selection["presets"]
    parsed_agents: list[str] | None = None
    if agents is not None:
        if not isinstance(agents, list) or not all(isinstance(v, str) and v in AGENTS for v in agents):
            raise BundleError("config: invalid agents")
        parsed_agents = sorted(set(agents))
    parsed_presets: dict[str, str] | None = None
    if presets is not None:
        if not isinstance(presets, dict) or not all(
            isinstance(k, str) and SLUG.fullmatch(k) and isinstance(v, str) and SLUG.fullmatch(v)
            for k, v in presets.items()
        ):
            raise BundleError("config: invalid presets")
        parsed_presets = dict(presets)
    return parsed_agents, parsed_presets


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
        config_agents, config_presets = read_config(root)
        previous = read_receipt(root)
        selection = previous.get("selection", {"agents": [], "presets": {}})
        if agents is not None:
            active_agents = sorted(set(agents))
        elif config_agents is not None:
            active_agents = config_agents
        else:
            active_agents = sorted(set(selection["agents"]))
        names = {item.bundle.name for item in installed}
        if all_assets:
            active_presets = {}
        else:
            if config_presets is not None:
                active_presets = {k: v for k, v in config_presets.items() if k in names}
            else:
                active_presets = {k: v for k, v in selection["presets"].items() if k in names}
            active_presets.update(presets or {})
        desired, assets, packages, overrides_record, drift_list = desired_inventory(
            installed,
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
            "packages": packages,
            "assets": assets,
            "actions": actions,
            "drift": drift_list,
        }


def recover_project(root: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    with project_lock(root):
        return recover_locked(root)
