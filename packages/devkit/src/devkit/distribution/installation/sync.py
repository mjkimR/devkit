"""``devkit sync``: converge a workspace to its selection, all or nothing."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from types import MappingProxyType

from devkit.core.receipt import FileRecord, OverrideRecord, Receipt, SeededRecord, Selection, ToolRecord

from ..bundles.common import BundleError
from . import guidance_block
from .config import effective_selection, read_config
from .discovery import InstalledBundle
from .hooks import run_post_sync
from .inventory import GENERATED_SKILLS, Seed, desired_inventory
from .receipt import read_receipt, receipt_content, receipt_json
from .results import ActionJSON, SyncResult, asset_json, package_json
from .transaction import apply_changes, project_lock, recover_locked, require_no_journal
from .workspace import AGENTS_FILE, MANAGED, OVERRIDES, RECEIPT, Content, same_content, signature, snapshot

TOOL_PACKAGE = "devkit"


def tool_identity() -> ToolRecord:
    """The running distributor, recorded in the receipt whenever it is written."""
    try:
        version = metadata.version(TOOL_PACKAGE)
    except metadata.PackageNotFoundError:
        version = "unknown"
    return ToolRecord(TOOL_PACKAGE, version)


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


def project_root(root: Path) -> Path:
    root = root.resolve()
    if not root.is_dir():
        raise BundleError("target must be an existing directory")
    return root


def _plan_guidance_block(
    root: Path,
    changes: dict[str, Content | None],
    actions: list[ActionJSON],
    recorded: str | None,
    *,
    enabled: bool,
    bundles: list[str],
    entry_skills: list[str],
) -> str | None:
    """Add the root ``AGENTS.md`` change for the managed block; return the hash to record.

    The block is owned like a managed file: a hand edit (digest differs from
    the receipt) stops the sync before any write, a removed block is written
    again, and the bytes outside the markers are never touched. With
    ``enabled`` off, a block whose digest still matches the receipt is removed
    and the receipt stops recording it; a project that never had the block is
    not read at all.
    """
    if not enabled and recorded is None:
        return None
    if (root / AGENTS_FILE).is_symlink():
        if not enabled:
            return None
        raise BundleError(
            f"{AGENTS_FILE} is a symlink; devkit writes its guidance block only into a regular root {AGENTS_FILE}."
            f" Make {AGENTS_FILE} the file (and point CLAUDE.md or other names at it), or set"
            " guidance_block = false in .devkit/config.toml"
        )
    current = snapshot(root, AGENTS_FILE)
    text = guidance_block.decode(current.data if current else None)
    existing = guidance_block.extract(text)
    if existing is not None:
        if recorded is None:
            raise BundleError(f"unowned guidance block already exists: {AGENTS_FILE}")
        if guidance_block.digest(existing) != recorded:
            raise BundleError(
                f"user-modified guidance block: {AGENTS_FILE}; restore the block between the markers"
                f" (for example 'git checkout -- {AGENTS_FILE}'), keep project text outside them,"
                " and rerun devkit sync"
            )
    mode = current.mode if current else 0o644
    if not enabled:
        if existing is not None and text is not None:
            remainder = guidance_block.strip(text)
            changes[AGENTS_FILE] = None if remainder is None else Content(remainder.encode("utf-8"), mode)
            actions.append({"path": AGENTS_FILE, "action": "remove" if remainder is None else "update"})
        return None
    desired = guidance_block.render(bundles, entry_skills)
    if existing is None or guidance_block.normalize(existing) != desired:
        changes[AGENTS_FILE] = Content(guidance_block.compose(text, desired).encode("utf-8"), mode)
        actions.append({"path": AGENTS_FILE, "action": "create" if current is None else "update"})
    return guidance_block.digest(desired)


def _plan_seeds(
    root: Path,
    seeds: dict[str, Seed],
    changes: dict[str, Content | None],
    actions: list[ActionJSON],
) -> tuple[SeededRecord, ...]:
    """Add the seeded files that do not exist yet; return the receipt's ``seeded`` record.

    A seeded file is written only when its destination is absent. Afterwards it
    is project-owned: never compared, updated, removed or hash-checked. The
    record is informational (which selected asset seeded which path).
    """
    for dest in sorted(seeds):
        if snapshot(root, dest) is None:
            changes[dest] = seeds[dest].content
            actions.append({"path": dest, "action": "seed"})
    return tuple(SeededRecord(seed.bundle, seed.asset, dest) for dest, seed in sorted(seeds.items()))


def _carried_overrides(
    root: Path, previous: Receipt | None, selected: set[str]
) -> dict[str, dict[str, OverrideRecord]]:
    """Override records of deselected bundles whose override files are still in the project.

    Keeping the baseline means drift that happens while a bundle is deselected
    is still reported when it is selected again.
    """
    if previous is None:
        return {}
    return {
        bundle: dict(records)
        for bundle, records in previous.overrides.items()
        if bundle not in selected and (root / OVERRIDES / bundle).is_dir()
    }


def sync_project(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    dry_run: bool = False,
) -> SyncResult:
    """Deploy the bundles selected in ``config.toml`` and the built-in bundles it does not opt out of.

    ``agents``, ``presets`` (per-bundle replacements) and ``deselect`` layer
    one-run selections over the configuration; callers persist them separately.
    Post-sync hooks run after the project lock is released.
    """
    root = project_root(root)
    with project_lock(root):
        result = sync_locked(root, installed, agents=agents, presets=presets, deselect=deselect, dry_run=dry_run)
    if not dry_run:
        result["notices"].extend(run_post_sync(root, dict(result)))
    return result


def sync_locked(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    dry_run: bool = False,
) -> SyncResult:
    """``sync_project`` for a caller that already holds the project lock; runs no hooks."""
    require_no_journal(root)
    config = read_config(root)
    previous = read_receipt(root)
    active_agents = sorted(set(agents)) if agents is not None else config.agents
    active_presets = {**effective_selection(installed, config), **(presets or {})}
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
    inventory = desired_inventory(
        selected,
        active_presets,
        active_agents,
        root=root,
        previous_overrides={b: dict(r) for b, r in previous.overrides.items()} if previous else None,
    )
    if config.override_drift == "block" and inventory.drift:
        listed = ", ".join(f"{item.bundle}:{item.asset}" for item in inventory.drift)
        raise BundleError(
            f'upstream drift behind an override (override_drift = "block"): {listed}; review with'
            " 'devkit override diff <bundle>:<asset>' and accept with 'devkit override accept <bundle>:<asset>'"
        )
    old_files = dict(previous.file_records) if previous else {}
    desired = inventory.files
    changes: dict[str, Content | None] = {}
    actions: list[ActionJSON] = []
    notices: list[str] = []
    # Managed files that were edited by hand and are no longer desired: left on disk,
    # dropped from the receipt, reported. A modified file that is still desired aborts.
    orphans: list[str] = []
    for name in sorted(old_files.keys() | desired.keys()):
        current = snapshot(root, name)
        after = desired.get(name)
        if name in old_files:
            record = old_files[name]
            if current is not None and signature(current) != (record.sha256, record.mode):
                if after is None:
                    orphans.append(name)
                    continue
                raise BundleError(f"user-modified deployment file: {name}")
        elif current is not None:
            raise BundleError(f"unowned destination already exists: {name}")
        if not same_content(current, after):
            changes[name] = after
            action = "remove" if after is None else ("create" if current is None else "update")
            actions.append({"path": name, "action": action})
    for name in orphans:
        notices.append(f"left modified file in place: {name} (no longer managed; delete it yourself)")
    overrides = {**_carried_overrides(root, previous, set(active_presets)), **inventory.overrides}
    seeded = _plan_seeds(root, inventory.seeds, changes, actions)
    block_hash = _plan_guidance_block(
        root,
        changes,
        actions,
        previous.guidance_block if previous else None,
        enabled=config.guidance_block,
        bundles=sorted(active_presets),
        entry_skills=[kind for kind in GENERATED_SKILLS if any(asset.kind == kind for asset in inventory.assets)],
    )
    tool = tool_identity()
    receipt = Receipt(
        schema=1,
        packages=tuple(inventory.packages),
        selection=Selection(
            tuple(active_agents), MappingProxyType({name: tuple(values) for name, values in active_presets.items()})
        ),
        asset_records=tuple(inventory.assets),
        file_records=MappingProxyType({name: _file_record(content) for name, content in sorted(desired.items())}),
        tool=tool,
        overrides=MappingProxyType(
            {bundle: MappingProxyType(records) for bundle, records in sorted(overrides.items())}
        ),
        seeded=seeded,
        guidance_block=block_hash,
    )
    # The writing tool's version alone is not a change: a no-op keeps the exact receipt bytes.
    if previous is None or _without_tool(receipt) != _without_tool(previous):
        changes[RECEIPT] = receipt_content(receipt)
        actions.append({"path": RECEIPT, "action": "update" if previous else "create"})
        if previous is not None and previous.tool is not None and previous.tool != tool:
            notices.append(f"{previous.tool.package} {previous.tool.version} -> {tool.version}")
    if not dry_run:
        apply_changes(root, changes)
    return {
        "dry_run": dry_run,
        "selection": {"agents": list(active_agents), "presets": active_presets},
        "packages": [package_json(item) for item in inventory.packages],
        "assets": [asset_json(asset) for asset in inventory.assets],
        "actions": actions,
        "drift": [
            {"bundle": item.bundle, "asset": item.asset, "path": item.path, "message": item.message}
            for item in inventory.drift
        ],
        "orphans": orphans,
        "stray": stray_managed_files(root, old_files.keys() | desired.keys()),
        "unprojected": [
            {"bundle": item.bundle, "asset": item.asset, "agent": item.agent} for item in inventory.unprojected
        ],
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
        "notices": notices,
    }


def _file_record(content: Content) -> FileRecord:
    sha, mode = signature(content)
    return FileRecord(sha, mode)


def _without_tool(receipt: Receipt) -> dict[str, object]:
    value = receipt_json(receipt)
    value.pop("tool", None)
    return value


def recover_project(root: Path) -> int:
    root = project_root(root)
    with project_lock(root):
        return recover_locked(root)
