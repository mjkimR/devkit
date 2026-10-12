"""``devkit sync``: converge a workspace to its selection, all or nothing."""

from __future__ import annotations

import json
from importlib import metadata
from pathlib import Path
from types import MappingProxyType

from devkit.advisory import AdvisoryError, ExitCode, Level
from devkit.core.errors import ArgumentError
from devkit.core.receipt import (
    MANAGED_PATH,
    OVERRIDES_PATH,
    RECEIPT_PATH,
    FileRecord,
    OverrideRecord,
    Receipt,
    SeededRecord,
    Selection,
    ToolRecord,
)
from devkit.distribution.content import Content, same_content, signature
from devkit.distribution.errors import (
    BundleUnselectedNotice,
    ConflictError,
    OrphanLeftNotice,
    OverrideDriftError,
    SelectionError,
    StrayFilesNotice,
    SubagentUnprojectedNotice,
    ToolVersionChangedNotice,
    UnsafeWorkspaceError,
)
from devkit.distribution.installation import guidance_block
from devkit.distribution.installation.config import ProjectConfig, effective_selection, read_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.hooks import run_post_sync
from devkit.distribution.installation.inventory import GENERATED_SKILLS, Inventory, Seed, desired_inventory
from devkit.distribution.installation.overrides import Drift
from devkit.distribution.installation.receipt import read_receipt, receipt_content, receipt_json
from devkit.distribution.installation.results import Action, SyncResult, Unselected
from devkit.distribution.installation.transaction import (
    apply_changes,
    atomic_write,
    project_lock,
    recover_locked,
    require_no_journal,
)
from devkit.distribution.installation.workspace import AGENTS_FILE, SEEN_BUNDLES, checked_path, snapshot

TOOL_PACKAGE = "devkit"
EDITED_FILE_FIX = (
    "Keep the edit: copy it aside, run `devkit override create <bundle>:<asset>` and reapply it there;"
    " discard it: `git checkout -- <path>`"
)

Changes = dict[str, Content | None]


def tool_identity() -> ToolRecord:
    """The running distributor, recorded in the receipt whenever it is written."""
    try:
        version = metadata.version(TOOL_PACKAGE)
    except metadata.PackageNotFoundError:
        version = "unknown"
    return ToolRecord(TOOL_PACKAGE, version)


def require_project_dir(root: Path) -> Path:
    """``root`` resolved; ``ArgumentError`` unless it is an existing directory."""
    root = root.resolve()
    if not root.is_dir():
        raise ArgumentError(
            f"target must be an existing directory: {root}",
            target_files=["--workspace-root"],
            fix="Pass an existing project directory",
        )
    return root


def edited_files_error(message: str, names: list[str], *, exit_code: ExitCode | None = None) -> ConflictError:
    """The conflict of managed files edited by hand (content or execute bit) that devkit will not overwrite."""
    return ConflictError(
        message,
        target_files=names,
        what_to_report=f"Whether to keep the edits to {', '.join(names)} (as project overrides) or discard them",
        fix=EDITED_FILE_FIX,
        exit_code=exit_code,
    )


def stray_managed_files(root: Path, owned: set[str]) -> list[str]:
    """Files under the managed root that neither the receipt nor the desired inventory owns.

    The managed root is a regenerated cache; a file placed there by hand is
    never deployed, never removed, and may be picked up by consumers that scan
    the directory (such as rule loading). It is reported, not deleted.
    """
    managed = root / MANAGED_PATH
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


def _resolve_selection(
    installed: list[InstalledBundle],
    config: ProjectConfig,
    agents: list[str] | None,
    presets: dict[str, list[str]] | None,
    deselect: list[str] | tuple[str, ...],
) -> Selection:
    """The configuration's selection with the one-run ``agents``, ``presets`` and ``deselect`` layered over it."""
    active = {**effective_selection(installed, config), **(presets or {})}
    for name in deselect:
        active.pop(name, None)
    missing = sorted(set(active) - {item.bundle.name for item in installed})
    if missing:
        raise SelectionError(
            f"selected bundle is not installed: {missing}",
            fix="Install the content package that ships it, or deselect it with `devkit remove <bundle>`",
        )
    return Selection(
        tuple(sorted(set(agents)) if agents is not None else config.agents),
        MappingProxyType({name: tuple(sorted(set(values))) for name, values in sorted(active.items())}),
    )


def _override_drift(drift: list[Drift], *, blocked: bool) -> OverrideDriftError:
    """One advisory for every override whose upstream changed: the refusal under ``block``, else a warning."""
    listed = [f"{item.bundle}:{item.asset}" for item in drift]
    policy = ' (override_drift = "block")' if blocked else ""
    error = OverrideDriftError(
        f"upstream drift behind an override{policy}: {', '.join(listed)}",
        target_files=[item.path for item in drift],
        fix=f"Review with `devkit override diff {listed[0]}` and accept with `devkit override accept {listed[0]}`",
        what_to_report=(
            "Upstream changed an asset this project overrides; review the diff, then accept it or keep the override"
        ),
    )
    return error if blocked else error.with_level(Level.WARNING)


def _refuse_override_drift(drift: list[Drift]) -> None:
    """``override_drift = "block"``: refuse the sync while an override hides upstream changes."""
    if drift:
        raise _override_drift(drift, blocked=True)


def _plan_managed_files(
    root: Path, old_files: dict[str, FileRecord], desired: dict[str, Content], changes: Changes, actions: list[Action]
) -> list[AdvisoryError]:
    """Add every managed-file change; return an ``ORPHAN_LEFT`` notice per orphan.

    A managed file edited by hand that is still desired aborts the sync. One
    that is no longer desired is an orphan: left on disk, dropped from the
    receipt, reported. A file that exists without being owned is never
    overwritten.
    """
    orphans: list[AdvisoryError] = []
    for name in sorted(old_files.keys() | desired.keys()):
        current = snapshot(root, name)
        after = desired.get(name)
        if name in old_files:
            record = old_files[name]
            if current is not None and signature(current) != (record.sha256, record.mode):
                if after is None:
                    orphans.append(
                        OrphanLeftNotice(
                            f"left modified file in place: {name} (no longer managed)",
                            target_files=[name],
                            what_to_report=f"Whether to delete {name}; devkit never deletes an edited file",
                        )
                    )
                    continue
                raise edited_files_error(f"user-modified deployment file: {name}", [name])
        elif current is not None:
            raise ConflictError(
                f"unowned destination already exists: {name}",
                target_files=[name],
                what_to_report=f"Whether {name} may be replaced by the bundle's file; devkit does not overwrite files it does not own",
            )
        if not same_content(current, after):
            changes[name] = after
            action = "remove" if after is None else ("create" if current is None else "update")
            actions.append(Action(name, action))
    return orphans


def _plan_guidance_block(
    root: Path,
    changes: Changes,
    actions: list[Action],
    recorded: str | None,
    *,
    enabled: bool,
    bundles: list[str],
    entry_skills: list[str],
    fragments: list[str],
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
        raise UnsafeWorkspaceError(
            f"{AGENTS_FILE} is a symlink; devkit writes its guidance block only into a regular root {AGENTS_FILE}",
            target_files=[AGENTS_FILE],
            fix=f"Make {AGENTS_FILE} the regular file (and point CLAUDE.md or other names at it),"
            " or set guidance_block = false in .devkit/config.toml",
        )
    current = snapshot(root, AGENTS_FILE)
    text = guidance_block.decode(current.data if current else None)
    existing = guidance_block.extract(text)
    if existing is not None:
        if recorded is None:
            raise ConflictError(
                f"unowned guidance block already exists: {AGENTS_FILE}",
                target_files=[AGENTS_FILE],
                what_to_report=f"Whether to remove the devkit block markers that {AGENTS_FILE} already has, so sync can write its own",
            )
        if guidance_block.digest(existing) != recorded:
            raise ConflictError(
                f"user-modified guidance block: {AGENTS_FILE}",
                target_files=[AGENTS_FILE],
                what_to_report="Whether to discard the edit inside the devkit block markers",
                fix=f"Restore the block between the markers (for example `git checkout -- {AGENTS_FILE}`),"
                " keep project text outside them, then run `devkit sync`",
            )
    mode = current.mode if current else 0o644
    if not enabled:
        if existing is not None and text is not None:
            remainder = guidance_block.strip(text)
            changes[AGENTS_FILE] = None if remainder is None else Content(remainder.encode("utf-8"), mode)
            actions.append(Action(AGENTS_FILE, "remove" if remainder is None else "update"))
        return None
    desired = guidance_block.render(bundles, entry_skills, fragments)
    if existing is None or guidance_block.normalize(existing) != desired:
        changes[AGENTS_FILE] = Content(guidance_block.compose(text, desired).encode("utf-8"), mode)
        actions.append(Action(AGENTS_FILE, "create" if current is None else "update"))
    return guidance_block.digest(desired)


def _plan_seeds(
    root: Path, seeds: dict[str, Seed], changes: Changes, actions: list[Action]
) -> tuple[SeededRecord, ...]:
    """Add the seeded files that do not exist yet; return the receipt's ``seeded`` record.

    A seeded file is written only when its destination is absent. Afterwards it
    is project-owned: never compared, updated, removed or hash-checked. The
    record is informational (which selected asset seeded which path).
    """
    for dest in sorted(seeds):
        if snapshot(root, dest) is None:
            changes[dest] = seeds[dest].content
            actions.append(Action(dest, "seed"))
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
        if bundle not in selected and (root / OVERRIDES_PATH / bundle).is_dir()
    }


def _build_receipt(
    selection: Selection,
    inventory: Inventory,
    overrides: dict[str, dict[str, OverrideRecord]],
    seeded: tuple[SeededRecord, ...],
    block_hash: str | None,
) -> Receipt:
    def record(content: Content) -> FileRecord:
        return FileRecord(*signature(content))

    return Receipt(
        schema=1,
        packages=tuple(inventory.packages),
        selection=selection,
        asset_records=tuple(inventory.assets),
        file_records=MappingProxyType({name: record(content) for name, content in sorted(inventory.files.items())}),
        tool=tool_identity(),
        overrides=MappingProxyType(
            {bundle: MappingProxyType(records) for bundle, records in sorted(overrides.items())}
        ),
        seeded=seeded,
        guidance_block=block_hash,
    )


def _plan_receipt(
    previous: Receipt | None, receipt: Receipt, changes: Changes, actions: list[Action]
) -> list[AdvisoryError]:
    """Add the receipt write when anything but the writing tool changed; notice a tool version change it records."""
    if previous is not None and _without_tool(receipt) == _without_tool(previous):
        # The writing tool's version alone is not a change: a no-op keeps the exact receipt bytes.
        return []
    changes[RECEIPT_PATH] = receipt_content(receipt)
    actions.append(Action(RECEIPT_PATH, "update" if previous else "create"))
    before, after = previous.tool if previous is not None else None, receipt.tool
    if before is None or after is None or before == after:
        return []
    return [
        ToolVersionChangedNotice(
            f"{before.package} {before.version} -> {after.version}: the receipt now records the running version"
        )
    ]


def _without_tool(receipt: Receipt) -> dict[str, object]:
    value = receipt_json(receipt)
    value.pop("tool", None)
    return value


def _sync_result(
    root: Path,
    installed: list[InstalledBundle],
    selection: Selection,
    inventory: Inventory,
    owned: set[str],
    actions: list[Action],
    notices: list[AdvisoryError],
    *,
    opted_out: frozenset[str],
    seen: frozenset[str],
    dry_run: bool,
) -> SyncResult:
    stray = stray_managed_files(root, owned)
    unselected = [
        Unselected(
            item.bundle.name,
            item.package,
            item.bundle.preset_names,
            item.bundle.default_preset,
            opted_out=item.bundle.name in opted_out,
        )
        for item in installed
        if item.bundle.name not in selection.presets
    ]
    return SyncResult(
        dry_run=dry_run,
        selection=selection,
        packages=list(inventory.packages),
        assets=list(inventory.assets),
        actions=actions,
        drift=list(inventory.drift),
        stray=stray,
        unprojected=list(inventory.unprojected),
        unselected=unselected,
        notices=[
            *_state_notices(list(inventory.drift), stray),
            *notices,
            *_selection_notices(inventory, [item for item in unselected if item.bundle not in seen]),
        ],
    )


def _state_notices(drift: list[Drift], stray: list[str]) -> list[AdvisoryError]:
    """Warnings about the workspace the sync leaves: overrides behind upstream, unmanaged files in the managed root."""
    notices: list[AdvisoryError] = []
    if drift:
        notices.append(_override_drift(drift, blocked=False))
    if stray:
        notices.append(
            StrayFilesNotice(f"unmanaged files under .devkit/managed/: {', '.join(stray)}", target_files=stray)
        )
    return notices


def _selection_notices(inventory: Inventory, new: list[Unselected]) -> list[AdvisoryError]:
    """Notices about what the selection left out: subagents without a native variant, and installed bundles the
    project has not decided about (neither selected nor opted out) that this clone has not been told about yet."""
    notices: list[AdvisoryError] = []
    if inventory.unprojected:
        items = [f"{item.bundle}:{item.asset} ({item.agent})" for item in inventory.unprojected]
        notices.append(
            SubagentUnprojectedNotice(
                f"subagents without a native variant for a selected agent were not projected: {', '.join(items)}",
                "the bundle can add the variant or ship a role contract; "
                "the project can narrow `agents` in .devkit/config.toml",
            )
        )
    undecided = [item for item in new if not item.opted_out]
    if undecided:
        names = [item.bundle for item in undecided]
        notices.append(
            BundleUnselectedNotice(
                f"installed bundles not selected yet: {', '.join(names)}",
                *(_add_command(item) for item in undecided),
                fix=f"devkit add {names[0]}" if len(names) == 1 else "devkit list",
            )
        )
    return notices


def _add_command(item: Unselected) -> str:
    presets = ", ".join(item.presets) or "-"
    return (
        f"devkit add {item.bundle}  (package {item.package}; presets {presets}; default {item.default_preset or '-'})"
    )


def _read_seen_bundles(root: Path) -> frozenset[str]:
    """The installed bundles this clone was already told about; a missing or unreadable record means none."""
    path = checked_path(root, SEEN_BUNDLES)
    try:
        data = json.loads(path.read_text("utf-8"))
    except (OSError, ValueError):
        return frozenset()
    names = data.get("bundles") if isinstance(data, dict) else None
    return frozenset(name for name in names if isinstance(name, str)) if isinstance(names, list) else frozenset()


def _record_seen_bundles(root: Path, installed: list[InstalledBundle], seen: frozenset[str]) -> None:
    """Remember the installed bundles, so ``BUNDLE_UNSELECTED`` reports a bundle once, when it appears."""
    names = sorted({item.bundle.name for item in installed})
    if set(names) != seen:
        data = json.dumps({"bundles": names}, indent=2) + "\n"
        atomic_write(root, SEEN_BUNDLES, Content(data.encode("utf-8"), 0o644))


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
    root = require_project_dir(root)
    with project_lock(root):
        result = sync_locked(root, installed, agents=agents, presets=presets, deselect=deselect, dry_run=dry_run)
    if not dry_run:
        result.notices.extend(run_post_sync(root, result.to_dict()))
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
    selection = _resolve_selection(installed, config, agents, presets, deselect)
    inventory = desired_inventory(
        [item for item in installed if item.bundle.name in selection.presets],
        {name: list(values) for name, values in selection.presets.items()},
        list(selection.agents),
        root=root,
        previous_overrides={b: dict(r) for b, r in previous.overrides.items()} if previous else None,
    )
    if config.override_drift == "block":
        _refuse_override_drift(inventory.drift)
    old_files = dict(previous.file_records) if previous else {}
    changes: Changes = {}
    actions: list[Action] = []
    notices = _plan_managed_files(root, old_files, inventory.files, changes, actions)
    seeded = _plan_seeds(root, inventory.seeds, changes, actions)
    block_hash = _plan_guidance_block(
        root,
        changes,
        actions,
        previous.guidance_block if previous else None,
        enabled=config.guidance_block,
        bundles=list(selection.presets),
        entry_skills=[kind for kind in GENERATED_SKILLS if any(asset.kind == kind for asset in inventory.assets)],
        fragments=inventory.fragments(),
    )
    overrides = {**_carried_overrides(root, previous, set(selection.presets)), **inventory.overrides}
    receipt = _build_receipt(selection, inventory, overrides, seeded, block_hash)
    notices.extend(_plan_receipt(previous, receipt, changes, actions))
    seen = _read_seen_bundles(root)
    if not dry_run:
        apply_changes(root, changes)
        _record_seen_bundles(root, installed, seen)
    owned = old_files.keys() | inventory.files.keys()
    return _sync_result(
        root,
        installed,
        selection,
        inventory,
        owned,
        actions,
        notices,
        opted_out=config.opted_out,
        seen=seen,
        dry_run=dry_run,
    )


def recover_project(root: Path) -> int:
    """Roll back an interrupted synchronization; return the number of files restored."""
    root = require_project_dir(root)
    with project_lock(root):
        return recover_locked(root)
