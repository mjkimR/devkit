"""``devkit sync``: converge a workspace to its selection, all or nothing."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from types import MappingProxyType

from devkit.advisory import AdvisoryError, ExitCode, Level
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core.git import run_git

from devkit_dist.features.distribution.models.content import Content, json_content, same_content, signature
from devkit_dist.features.distribution.models.errors import (
    BundleAutoSelectedNotice,
    BundleUnselectedNotice,
    ConflictError,
    OrphanLeftNotice,
    OverrideDriftError,
    ReceiptStaleError,
    StrayFilesNotice,
    ToolVersionChangedNotice,
    UnprojectedNotice,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.models.results import Action, SyncResult, Unselected
from devkit_dist.features.distribution.services.installation import guidance_block, local_render
from devkit_dist.features.distribution.services.installation.config import (
    ConfigUpdate,
    ProjectConfig,
    default_selection,
    effective_selection,
    missing_selection_error,
    parse_config,
    read_config,
)
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle, unusable_notices
from devkit_dist.features.distribution.services.installation.engines import engine_notices
from devkit_dist.features.distribution.services.installation.extensions import run_post_sync
from devkit_dist.features.distribution.services.installation.host_hooks import plan_host_hooks
from devkit_dist.features.distribution.services.installation.inventory import (
    GENERATED_SKILLS,
    Inventory,
    Seed,
    desired_inventory,
)
from devkit_dist.features.distribution.services.installation.overrides import Drift, overridden_files
from devkit_dist.features.distribution.services.installation.receipt import read_receipt, receipt_content, receipt_json
from devkit_dist.features.distribution.services.installation.transaction import (
    apply_changes,
    atomic_write,
    project_lock,
    recover_locked,
    require_no_journal,
    require_writable,
)
from devkit_dist.features.distribution.services.installation.workspace import (
    AGENTS_FILE,
    DEPLOYED,
    DEVKIT_GITIGNORE,
    DEVKIT_GITIGNORE_TEXT,
    METADATA,
    SEEN_BUNDLES,
    checked_path,
    directory_at,
    occupied,
    owned_prefix,
    snapshot,
)
from devkit_dist.features.host.usecases import registrations
from devkit_dist.features.project.repositories.invocation import guard_execution
from devkit_dist.features.project.repositories.local_config import LOCAL_CONFIG_PATH, read_effective_config
from devkit_dist.features.project.repositories.project import git_toplevel, require_devkit_root
from devkit_dist.features.project.repositories.receipt import (
    CONFIG_PATH,
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
from devkit_dist.features.project.services.presentation import resolve_language

TOOL_PACKAGE = "devkit-dist"
EDITED_FILE_FIX = (
    "Keep the edit: copy it aside, run `devkit override create <bundle>:<asset>` and reapply it there;"
    " discard it: delete the file and run `devkit sync`"
)
UNOWNED_FILE_FIX = "Move each unowned file out of the way (or delete it), then run `devkit sync`"

Changes = dict[str, Content | None]

# Per guidance block conflict state (``modified``, ``unowned``): the message, fix and what to report.
BLOCK_CONFLICTS: Mapping[str, tuple[str, str, str]] = MappingProxyType(
    {
        "modified": (
            f"user-modified guidance block: {AGENTS_FILE}",
            f"Restore the block between the markers (for example `git checkout -- {AGENTS_FILE}`),"
            " keep project text outside them, then run `devkit sync`",
            "Whether to discard the edit inside the devkit block markers",
        ),
        "unowned": (
            f"unowned guidance block already exists: {AGENTS_FILE}",
            f"Remove the devkit block markers from {AGENTS_FILE}, then run `devkit sync`",
            f"Whether to remove the devkit block markers that {AGENTS_FILE} already has, so sync can write its own",
        ),
    }
)


def tool_identity() -> ToolRecord:
    """The running distributor, recorded in the receipt whenever it is written."""
    try:
        version = metadata.version(TOOL_PACKAGE)
    except metadata.PackageNotFoundError:
        version = "unknown"
    return ToolRecord(TOOL_PACKAGE, version)


def require_project_dir(root: Path) -> Path:
    """``root`` resolved; ``ArgumentError`` unless it is an existing directory that can be a devkit root
    (``require_devkit_root``)."""
    root = root.resolve()
    if not root.is_dir():
        raise ArgumentError(
            f"target must be an existing directory: {root}",
            target_files=["--workspace-root"],
            fix="Pass an existing project directory",
        )
    return require_devkit_root(root)


def edited_files_error(message: str, names: list[str], *, exit_code: ExitCode | None = None) -> ConflictError:
    """The conflict of managed files edited by hand (content or execute bit) that devkit will not overwrite."""
    return ConflictError(
        message,
        target_files=names,
        what_to_report=f"Whether to keep the edits to {', '.join(names)} (as project overrides) or discard them",
        fix=EDITED_FILE_FIX,
        exit_code=exit_code,
    )


def guidance_block_error(state: str, *, exit_code: ExitCode | None = None) -> ConflictError:
    """The ``SYNC_CONFLICT`` a sync raises for a ``modified`` or ``unowned`` root ``AGENTS.md`` block."""
    message, fix, report = BLOCK_CONFLICTS[state]
    return ConflictError(message, target_files=[AGENTS_FILE], fix=fix, what_to_report=report, exit_code=exit_code)


def stray_managed_files(root: Path, owned: set[str]) -> list[str]:
    """Files under the managed root that neither the receipt nor the desired inventory owns.

    The managed root is a regenerated cache; a file placed there by hand is
    never deployed, never removed, and may be picked up by consumers that scan
    the directory (such as rule loading). It is reported, not deleted.
    Python bytecode caches (``__pycache__``) are not reported: nothing reads them as content.
    """
    managed = root / MANAGED_PATH
    if not managed.is_dir():
        return []
    stray = []
    for path in sorted(managed.rglob("*")):
        if path.is_symlink() or not path.is_file() or "__pycache__" in path.relative_to(managed).parts:
            continue
        rel = path.relative_to(root).as_posix()
        if rel not in owned:
            stray.append(rel)
    return stray


def _resolve_selection(
    installed: list[InstalledBundle],
    config: ProjectConfig,
    previous: Receipt | None,
    agents: list[str] | None,
    presets: dict[str, list[str]] | None,
    deselect: list[str] | tuple[str, ...],
) -> Selection:
    """The configuration's selection with the one-run ``agents``, ``presets`` and ``deselect`` layered over it."""
    active = {**effective_selection(installed, config, previous), **(presets or {})}
    for name in deselect:
        active.pop(name, None)
    # A selected bundle that failed to load stops the sync, as does a deployed one whose package no longer loads.
    unusable_notices(installed, active)
    missing = sorted(set(active) - {item.bundle.name for item in installed})
    if missing:
        # A bundle selected only by the receipt is deployed, so a sync would delete its committed files.
        deployed = [name for name in missing if name not in config.presets and name not in (presets or {})]
        raise missing_selection_error(missing, deployed)
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


@dataclass
class _Conflicts:
    """Everything a sync would overwrite without owning it, raised together as one ``SYNC_CONFLICT``."""

    edited: list[str] = field(default_factory=list)
    unowned: list[str] = field(default_factory=list)
    # ``"modified"`` or ``"unowned"`` when the root ``AGENTS.md`` block is in conflict.
    block: str | None = None

    def check(self) -> None:
        """Raise the ``ConflictError`` naming every conflicting path; nothing to do without one."""
        parts: list[tuple[str, str, str]] = []  # (message, fix, what to report)
        if self.edited:
            names = ", ".join(self.edited)
            parts.append(
                (
                    f"user-modified deployment files: {names}",
                    EDITED_FILE_FIX,
                    f"Whether to keep the edits to {names} (as project overrides) or discard them",
                )
            )
        if self.unowned:
            names = ", ".join(self.unowned)
            parts.append(
                (
                    f"unowned destinations already exist: {names}",
                    UNOWNED_FILE_FIX,
                    f"Whether {names} may be replaced by the bundle's files; devkit does not overwrite files it"
                    " does not own",
                )
            )
        if self.block is not None:
            parts.append(BLOCK_CONFLICTS[self.block])
        if parts:
            raise ConflictError(
                "; ".join(message for message, _, _ in parts),
                target_files=[*self.edited, *self.unowned, *([AGENTS_FILE] if self.block else [])],
                fix="; ".join(fix for _, fix, _ in parts),
                what_to_report="; ".join(report for _, _, report in parts),
            )


def _plan_managed_files(
    root: Path,
    old_files: dict[str, FileRecord],
    deployed: dict[str, FileRecord],
    desired: dict[str, Content],
    changes: Changes,
    actions: list[Action],
    conflicts: _Conflicts,
) -> list[AdvisoryError]:
    """Add every managed-file change; return an ``ORPHAN_LEFT`` notice per orphan.

    A file is devkit's own when it matches its receipt signature or the one
    this clone's last sync left (``deployed``): a pull can move the committed
    receipt while the Git-ignored file stays as that sync wrote it. A file
    already identical to the desired content (bytes and execute bit) needs no
    write and is never a conflict. Any other recorded file was edited by hand:
    a conflict while it is still desired, an orphan (left on disk, dropped from
    the receipt, reported) once it is not. A file that exists without being
    owned is never overwritten: one identical to the desired content is adopted
    into the receipt without a write, any other is a conflict. A file only the
    local record knows and nothing desires any more is removed while it is
    unchanged.
    """
    orphans: list[AdvisoryError] = []
    for name in sorted(old_files.keys() | desired.keys() | deployed.keys()):
        after = desired.get(name)
        # A directory where a file goes reads as absent: ``require_writable`` admits it only when this sync empties it.
        current = None if after is not None and directory_at(root, name) else snapshot(root, name)
        if current is not None and not same_content(current, after):
            records = [record for record in (old_files.get(name), deployed.get(name)) if record is not None]
            if not records:
                conflicts.unowned.append(name)
                continue
            if all(signature(current) != (record.sha256, record.mode) for record in records):
                if after is not None:
                    conflicts.edited.append(name)
                elif name in old_files:
                    orphans.append(
                        OrphanLeftNotice(
                            f"left modified file in place: {name} (no longer managed)",
                            target_files=[name],
                            what_to_report=f"Whether to delete {name}; devkit never deletes an edited file",
                        )
                    )
                continue
        if not same_content(current, after):
            changes[name] = after
            action = "remove" if after is None else ("create" if current is None else "update")
            actions.append(Action(name, action))
    return orphans


def block_conflict(existing: str, recorded: str | None, desired: str | None) -> str | None:
    """The ``BLOCK_CONFLICTS`` state a sync raises for the guidance block ``existing``; ``None`` when there is none.

    ``"modified"``: the block's digest differs from the receipt's ``recorded``
    one. ``"unowned"``: the receipt records no block and ``existing`` is not
    exactly ``desired``, the block the sync writes; that one is adopted.
    ``desired`` is consulted only without ``recorded``; ``None`` (the sync
    could not be planned) decides nothing.
    """
    if recorded is not None:
        return "modified" if guidance_block.digest(existing) != recorded else None
    if desired is None or guidance_block.normalize(existing) == desired:
        return None
    return "unowned"


def _plan_inventory(
    root: Path,
    installed: list[InstalledBundle],
    selection: Selection,
    previous_overrides: dict[str, dict[str, OverrideRecord]],
    *,
    effective: bool = False,
    environment: str | None = None,
) -> Inventory:
    """What the selection deploys: the inventory of the selected bundles' assets."""
    return desired_inventory(
        [item for item in installed if item.bundle.name in selection.presets],
        {name: list(values) for name, values in selection.presets.items()},
        list(selection.agents),
        root=root,
        previous_overrides=previous_overrides,
        variables=read_config(root, effective=effective).variables,
        language=resolve_language(root, effective=effective).resolved,
        environment=environment or read_effective_config(root).values["execution"]["environment"],
    )


def _render_block(selection: Selection, inventory: Inventory) -> str:
    """The guidance block a sync of ``selection`` writes."""
    return guidance_block.render(
        list(selection.presets),
        [kind for kind in GENERATED_SKILLS if any(asset.kind == kind for asset in inventory.assets)],
        inventory.fragments(),
    )


def planned_guidance_block(
    root: Path, installed: list[InstalledBundle], config: ProjectConfig, previous: Receipt | None
) -> str:
    """The guidance block a plain ``devkit sync`` would write now; raises what planning that sync raises."""
    selection = _resolve_selection(installed, config, previous, None, None, ())
    overrides = {bundle: dict(records) for bundle, records in previous.overrides.items()} if previous else {}
    return _render_block(selection, _plan_inventory(root, installed, selection, overrides))


def _plan_guidance_block(
    root: Path,
    changes: Changes,
    actions: list[Action],
    conflicts: _Conflicts,
    recorded: str | None,
    desired: str,
    *,
    enabled: bool,
) -> tuple[str | None, list[AdvisoryError]]:
    """Add the root ``AGENTS.md`` change for the managed block (``desired``); return the hash to record and any notice.

    The block is owned like a managed file: a hand edit (digest differs from
    the receipt) is a conflict, a removed block is written again, and the bytes
    outside the markers are never touched. Markers the receipt does not know
    are a conflict, unless the block is exactly the one sync writes: that one
    is adopted (``block_conflict``). With ``enabled`` off the receipt stops recording the block: one
    whose digest still matches is removed, an edited one is left in place with
    an ``ORPHAN_LEFT`` warning; a project that never had the block is not read
    at all.
    """
    if not enabled and recorded is None:
        return None, []
    if (root / AGENTS_FILE).is_symlink():
        if not enabled:
            return None, []
        raise UnsafeWorkspaceError(
            f"{AGENTS_FILE} is a symlink; devkit writes its guidance block only into a regular root {AGENTS_FILE}",
            target_files=[AGENTS_FILE],
            fix=f"Make {AGENTS_FILE} the regular file (and point CLAUDE.md or other names at it),"
            " or set guidance_block = false in .devkit/config.toml",
        )
    current = snapshot(root, AGENTS_FILE)
    text = guidance_block.decode(current.data if current else None)
    existing = guidance_block.extract(text)
    mode = current.mode if current else 0o644
    if not enabled:
        if existing is None or text is None:
            return None, []
        if guidance_block.digest(existing) != recorded:
            return None, [
                OrphanLeftNotice(
                    f"left modified guidance block in place: {AGENTS_FILE} (guidance_block = false)",
                    target_files=[AGENTS_FILE],
                    what_to_report=f"Whether to delete the devkit block from {AGENTS_FILE};"
                    " devkit never removes an edited block",
                )
            ]
        remainder = guidance_block.strip(text)
        changes[AGENTS_FILE] = None if remainder is None else Content(remainder.encode("utf-8"), mode)
        actions.append(Action(AGENTS_FILE, "remove" if remainder is None else "update"))
        return None, []
    if existing is not None:
        conflicts.block = block_conflict(existing, recorded, desired)
    if existing is None or guidance_block.normalize(existing) != desired:
        changes[AGENTS_FILE] = Content(guidance_block.compose(text, desired).encode("utf-8"), mode)
        actions.append(Action(AGENTS_FILE, "create" if current is None else "update"))
    return guidance_block.digest(desired), []


def _plan_seeds(
    root: Path,
    seeds: dict[str, Seed],
    recorded: frozenset[str],
    changes: Changes,
    actions: list[Action],
    *,
    locked: bool,
) -> tuple[SeededRecord, ...]:
    """Add the seeded files that do not exist yet; return the receipt's ``seeded`` record.

    A seeded file is written only when its destination is absent. Afterwards it
    is project-owned: never compared, updated, removed or hash-checked. The
    record is informational (which selected asset seeded which path). A path the
    previous receipt records as seeded (``recorded``) is only tested for
    presence, so whatever the project put there (a symlink, a directory) is
    left alone; one the project deleted is seeded again, except under
    ``locked``, which never writes a seeded file and leaves a missing one
    missing. A path seeded for the first time must be absent or a regular file.
    """
    for dest in sorted(seeds):
        if dest in recorded and (locked or occupied(root, dest)):
            continue
        if snapshot(root, dest) is None:
            changes[dest] = seeds[dest].content
            actions.append(Action(dest, "seed"))
    return tuple(SeededRecord(seed.bundle, seed.asset, dest) for dest, seed in sorted(seeds.items()))


def _plan_devkit_gitignore(root: Path, changes: Changes, actions: list[Action]) -> None:
    """Preserve project rules and manage only the local-configuration entry."""
    before = snapshot(root, DEVKIT_GITIGNORE)
    text = before.data.decode("utf-8") if before else DEVKIT_GITIGNORE_TEXT
    added = "/config.local.toml" not in text.splitlines()
    if added:
        text += ("" if text.endswith("\n") else "\n") + "/config.local.toml\n"
    if before is None or added:
        changes[DEVKIT_GITIGNORE] = Content(text.encode(), before.mode if before else 0o644)
        actions.append(Action(DEVKIT_GITIGNORE, "update" if before else "seed"))
    local_render.require_ignored(root, LOCAL_CONFIG_PATH, planned_ignore=added)


def _carried_overrides(
    root: Path,
    installed: list[InstalledBundle],
    previous: Receipt | None,
    tracked: dict[str, dict[str, OverrideRecord]],
) -> dict[str, dict[str, OverrideRecord]]:
    """``tracked`` plus the previous records of assets this sync does not deploy whose override files remain.

    Keeping the baseline means drift that happens while an asset is not
    deployed (its bundle deselected, its preset narrowed) is still reported
    when it is selected again. A bundle that is no longer installed keeps its
    records while it has override files at all.
    """
    overrides = {bundle: dict(records) for bundle, records in tracked.items()}
    if previous is None:
        return overrides
    bundles = {item.bundle.name: item.bundle for item in installed}
    for name, records in previous.overrides.items():
        bundle = bundles.get(name)
        for asset_id, record in records.items():
            if asset_id in tracked.get(name, {}):
                continue
            asset = bundle.asset(asset_id) if bundle is not None else None
            if bundle is not None and asset is not None:
                present = bool(overridden_files(root, bundle, asset))
            else:
                present = (root / OVERRIDES_PATH / name).is_dir()
            if present:
                overrides.setdefault(name, {})[asset_id] = record
    return overrides


def _build_receipt(
    selection: Selection,
    inventory: Inventory,
    overrides: dict[str, dict[str, OverrideRecord]],
    seeded: tuple[SeededRecord, ...],
    block_hash: str | None,
    environment: str,
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
        host_hooks=tuple(inventory.host_hooks),
        execution_environment=environment,
    )


def _plan_receipt(
    previous: Receipt | None, receipt: Receipt, changes: Changes, actions: list[Action]
) -> list[AdvisoryError]:
    """Add the receipt write when anything else changes; notice a tool version change it records."""
    if (
        previous is not None
        and _without_tool(receipt) == _without_tool(previous)
        and (not changes or receipt.tool == previous.tool)
    ):
        # The writing tool's version alone is not a change: a no-op keeps the exact receipt bytes;
        # a sync that writes anything else records the running version.
        return []
    changes[RECEIPT_PATH] = receipt_content(receipt)
    actions.append(Action(RECEIPT_PATH, "update" if previous else "create"))
    before, after = previous.tool if previous is not None else None, receipt.tool
    if before is None or after is None or before == after:
        return []
    # The package is named on both sides when it changed (``devkit-agt 0.1.1 -> devkit-dist 0.1.1``).
    running = after.version if after.package == before.package else f"{after.package} {after.version}"
    return [
        ToolVersionChangedNotice(
            f"{before.package} {before.version} -> {running}: the receipt now records the running version"
        )
    ]


def _without_tool(receipt: Receipt) -> dict[str, object]:
    value = receipt_json(receipt)
    value.pop("tool", None)
    return value


def _restores(item: Action, recorded: Mapping[str, FileRecord], deployed: Mapping[str, FileRecord]) -> bool:
    """Whether a planned write only brings a Git-ignored copy back to the committed receipt (``recorded``).

    With the receipt unchanged, a ``create`` of a recorded path writes the
    missing file as recorded, and an ``update`` of one replaces the copy this
    clone's last sync left (``deployed``) after a pull moved the receipt: any
    other content there is a conflict before this point. A ``remove`` of a path
    only ``deployed`` knows deletes such an unchanged copy of a file the
    receipt no longer records.
    """
    if item.action == "create":
        return item.path in recorded
    if item.action == "update":
        return item.path in recorded and item.path in deployed
    return item.action == "remove" and item.path not in recorded and item.path in deployed


def _restores_only(
    previous: Receipt | None, receipt: Receipt, actions: list[Action], deployed: Mapping[str, FileRecord]
) -> bool:
    """Whether the sync only restores files to what the committed receipt records (``--locked``).

    The receipt must be unchanged (the writing tool's version aside), so each
    written file gets the recorded signature, and every action must be a
    restore (``_restores``); anything else (a seed, the guidance block,
    ``.devkit/.gitignore``, a new receipt) changes committed state.
    """
    return (
        previous is not None
        and _without_tool(receipt) == _without_tool(previous)
        and all(
            _restores(item, previous.file_records, deployed)
            or (
                item.action == "create"
                and item.path in {".codex/hooks.json" for record in previous.host_hooks if record.host == "codex"}
            )
            for item in actions
        )
    )


STALE_DETAILS = 20  # planned writes listed in a RECEIPT_STALE refusal


def _receipt_stale(
    previous: Receipt | None, receipt: Receipt, actions: list[Action], deployed: Mapping[str, FileRecord]
) -> ReceiptStaleError:
    """The ``--locked`` refusal: why the committed state is out of date, and what a plain sync would write.

    ``target_files`` names only committed state: the receipt when it would change, and the planned paths that
    neither receipt nor this clone's ``deployed`` record knows as a managed or projected file (the root
    ``AGENTS.md``, seeded files, ``.devkit/.gitignore``). Managed and projected files are listed in the details
    with the other planned writes: committed state first, then the other changes, then the restores ``--locked``
    would have made, so the cap never hides the reason.
    """
    recorded = previous.file_records if previous is not None else {}
    unrecorded = [
        item.path
        for item in actions
        if item.path not in recorded and item.path not in receipt.file_records and item.path not in deployed
    ]
    if previous is None:
        reason, targets = "there is no committed receipt to restore from", [RECEIPT_PATH, *unrecorded]
    elif _without_tool(receipt) != _without_tool(previous):
        reason, targets = "the installed bundles no longer match the committed receipt", [RECEIPT_PATH, *unrecorded]
    else:
        reason, targets = "committed files no longer match the receipt", unrecorded
    committed = set(unrecorded)
    ordered = sorted(
        actions,
        key=lambda item: 0 if item.path in committed else 2 if _restores(item, recorded, deployed) else 1,
    )
    planned = [f"would {item.action} {item.path}" for item in ordered[:STALE_DETAILS]]
    if len(actions) > STALE_DETAILS:
        planned.append(f"and {len(actions) - STALE_DETAILS} more (`devkit sync --dry-run` lists them all)")
    return ReceiptStaleError(
        f"{reason}; devkit sync --locked only restores what the receipt records, so it wrote nothing",
        *planned,
        target_files=targets,
        what_to_report=(
            f"Whether to run `devkit sync` and commit what it changes: {reason}"
            " (a bundle source, the lock or the selection changed without the receipt it produces)"
        ),
    )


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
    auto_selected: list[InstalledBundle],
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
            *_selection_notices(inventory, [item for item in unselected if item.bundle not in seen], auto_selected),
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


def _new_auto_selected(
    installed: list[InstalledBundle],
    config: ProjectConfig,
    previous: Receipt | None,
    selection: Selection,
    presets: dict[str, list[str]],
) -> list[InstalledBundle]:
    """Auto-selected bundles of packages other than devkit that this sync deploys by default and the receipt lacks."""
    defaults = default_selection(installed, config)
    recorded = previous.selection.presets if previous is not None else {}
    return [
        item
        for item in installed
        if not item.builtin
        and item.bundle.name in defaults
        and item.bundle.name in selection.presets
        and item.bundle.name not in presets
        and item.bundle.name not in recorded
    ]


def _selection_notices(
    inventory: Inventory, new: list[Unselected], auto_selected: list[InstalledBundle]
) -> list[AdvisoryError]:
    """Notices about the selection: skills and subagents without a variant for a selected agent, bundles of other
    packages deployed by default for the first time, and installed bundles the project has not decided about (neither
    selected nor opted out) that this clone has not been told about yet."""
    notices: list[AdvisoryError] = []
    if inventory.unprojected:
        items = [f"{item.bundle}:{item.asset} ({item.agent})" for item in inventory.unprojected]
        notices.append(
            UnprojectedNotice(
                f"skills and subagents without a variant for a selected agent were not projected: {', '.join(items)}",
                "the bundle can add the variant (or, for a subagent, ship a role contract); "
                "the project can narrow `agents` in .devkit/config.toml",
            )
        )
    if auto_selected:
        names = [item.bundle.name for item in auto_selected]
        notices.append(
            BundleAutoSelectedNotice(
                f"installed bundles deployed with their default preset: {', '.join(names)}",
                *(
                    f"{item.bundle.name}  (package {item.package}; preset {item.bundle.default_preset}; "
                    f"opt out: devkit remove {item.bundle.name})"
                    for item in auto_selected
                ),
                fix=f"devkit remove {names[0]}" if len(names) == 1 else "devkit list",
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


def read_deployed(root: Path) -> dict[str, FileRecord]:
    """The signatures this clone's last sync left (``DEPLOYED``); a missing or unreadable record means none.

    Only paths the receipt may own are taken, so the record can never name a file outside devkit's destinations.
    """
    path = checked_path(root, DEPLOYED)
    try:
        data = json.loads(path.read_text("utf-8"))
    except (OSError, ValueError):
        return {}
    files = data.get("files") if isinstance(data, dict) else None
    if not isinstance(files, dict):
        return {}
    deployed: dict[str, FileRecord] = {}
    for name, record in files.items():
        if not isinstance(name, str) or not isinstance(record, dict) or owned_prefix(name) is None or name in METADATA:
            continue
        sha, mode = record.get("sha256"), record.get("mode")
        if isinstance(sha, str) and isinstance(mode, int) and not isinstance(mode, bool):
            deployed[name] = FileRecord(sha, mode)
    return deployed


def _deployed_personal(root: Path, deployed: Mapping[str, FileRecord], canonical: Mapping[str, FileRecord]) -> set[str]:
    """Personal provenance survives loss of the render ledger; unknown provenance fails closed."""
    try:
        data = json.loads(checked_path(root, DEPLOYED).read_bytes())
        personal = data.get("personal") if isinstance(data, dict) else None
    except (OSError, ValueError):
        personal = None
    if isinstance(personal, list) and all(isinstance(name, str) for name in personal):
        return set(personal) & deployed.keys()
    return {name for name in canonical if name in deployed and deployed[name] != canonical[name]}


def _record_deployed(
    root: Path, files: Mapping[str, FileRecord], recorded: dict[str, FileRecord], personal: set[str]
) -> None:
    """Remember actual signatures and personal provenance, including an explicit empty set."""
    data = {
        "files": {name: {"sha256": r.sha256, "mode": r.mode} for name, r in sorted(files.items())},
        "personal": sorted(personal),
    }
    content = json_content(data)
    if dict(files) != recorded or snapshot(root, DEPLOYED) != content:
        atomic_write(root, DEPLOYED, content)


def sync_project(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    dry_run: bool = False,
    locked: bool = False,
    save: Callable[[], ConfigUpdate] | None = None,
    environment: str | None = None,
    save_environment: bool = True,
) -> SyncResult:
    """Deploy the bundles selected in ``config.toml`` and the built-in bundles it does not opt out of.

    ``agents``, ``presets`` (per-bundle replacements) and ``deselect`` layer
    one-run selections over the configuration. ``save`` persists a selection
    instead: it renders the configuration edit under the project lock, from the
    configuration as it is then, so concurrent selection commands never lose
    an edit; the rendered edit is planned in memory and journaled with outputs,
    and post-sync extensions see the committed configuration. ``save`` is never
    called on ``dry_run``. ``locked`` keeps the committed state: the sync only
    restores the Git-ignored files to what the receipt records, or raises ``ReceiptStaleError``
    (``RECEIPT_STALE``) without writing anything. Post-sync extensions run after
    the project lock is released, except on a dry run.
    """
    if environment is not None and environment not in ("local", "cloud"):
        raise ArgumentError("environment must be local or cloud")
    root = require_project_dir(root)
    if not dry_run:
        guard_execution()
    # A dry run (``--dry-run``, ``--check``) writes nothing, so it reads under the shared lock like any reader.
    with registrations.clone_lock(root, dry_run=dry_run), project_lock(root, shared=dry_run):
        if not dry_run:
            guard_execution()
        if not dry_run and not locked:
            registrations.recover(root)
        captured = local_render.inputs(root)
        update = save() if save is not None and not dry_run else None
        selected_config = (
            parse_config(tomllib.loads(update.text))
            if update is not None and update.text is not None
            else read_config(root)
        )
        registration = registrations.plan(
            root, agents if agents is not None else selected_config.agents, environment=environment
        )
        if locked and registration.changes:
            if any(
                registration.before.get(key) is not None
                for key in (*registrations.DESTINATIONS.values(), registrations.LEDGER)
            ):
                raise registrations.RegistrationError(
                    "locked sync requires ordinary sync to reconcile local MCP registration"
                )
            # A fresh checkout has no registration to validate. Asset restoration stays
            # locked; lifecycle initialization runs separately after this succeeds.
            registration.after.clear()
        finish = commit_locked(
            root,
            installed,
            agents=agents,
            presets=presets,
            deselect=deselect,
            dry_run=dry_run,
            locked=locked,
            environment=environment,
            save_environment=save_environment,
            config_update=update,
            captured_inputs=captured,
        )
        result = finish()
        result.notices.extend(registration.notices)
        result.actions.extend(Action(path, "update") for path in registration.changes)
        if not dry_run:
            registrations.apply(registration, locked=locked)
    if update is not None:
        result.notices.extend(update.notices)
    if not dry_run:
        result.notices.extend(run_post_sync(root, result.to_dict()))
    return result


def commit_locked(
    root: Path,
    installed: list[InstalledBundle],
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    dry_run: bool = False,
    locked: bool = False,
    rebaseline: tuple[str, str] | None = None,
    environment: str | None = None,
    save_environment: bool = True,
    config_update: ConfigUpdate | None = None,
    captured_inputs: dict[str, bytes | None] | None = None,
) -> Callable[[], SyncResult]:
    """Plan a sync and, unless ``dry_run``, commit it; the caller holds the project lock. Runs no post-sync extension.

    Returns the step that follows the commit (recording the installed bundles,
    scanning for stray files, building the result). A failure there leaves the
    committed files in place, so a caller that undoes its own writes when the
    sync fails calls it outside that scope. ``rebaseline`` (``bundle, asset``)
    takes the current upstream as the baseline of that asset's override, for
    ``devkit override create``, which has just written the baseline copies.
    ``locked`` commits only when the sync restores files exactly as the receipt
    records them (``_restores_only``), without writing the receipt or a
    seeded file; otherwise it raises ``ReceiptStaleError`` before any write.
    A ``dry_run`` writes nothing, so the caller may hold the shared lock.
    """
    require_no_journal(root)
    captured = captured_inputs if captured_inputs is not None else local_render.inputs(root)
    local_render.unchanged(root, captured)
    config = read_config(root, effective=False)
    if config_update is not None and config_update.text is not None:
        config = parse_config(tomllib.loads(config_update.text))
    previous = read_receipt(root)
    selection = _resolve_selection(installed, config, previous, agents, presets, deselect)
    auto_selected = _new_auto_selected(installed, config, previous, selection, presets or {})
    previous_overrides = {b: dict(r) for b, r in previous.overrides.items()} if previous else {}
    if rebaseline is not None:
        previous_overrides.get(rebaseline[0], {}).pop(rebaseline[1], None)
    selected_environment = environment or read_effective_config(root).values["execution"]["environment"]
    inventory = _plan_inventory(root, installed, selection, previous_overrides, environment=selected_environment)
    effective = _plan_inventory(
        root, installed, selection, previous_overrides, effective=True, environment=selected_environment
    )
    personal = local_render.personal_files(root, inventory, effective)
    if config.override_drift == "block":
        _refuse_override_drift(inventory.drift)
    old_files = dict(previous.file_records) if previous else {}
    changes: Changes = {}
    actions: list[Action] = []
    conflicts = _Conflicts()
    notices = unusable_notices(installed, selection.presets)
    deployed = read_deployed(root)
    plan_host_hooks(root, previous.host_hooks if previous else (), inventory.host_hooks, changes, actions)
    notices.extend(_plan_managed_files(root, old_files, deployed, effective.files, changes, actions, conflicts))
    recorded_seeds = frozenset(entry.path for entry in previous.seeded) if previous else frozenset()
    seeded = _plan_seeds(root, inventory.seeds, recorded_seeds, changes, actions, locked=locked)
    _plan_devkit_gitignore(root, changes, actions)
    fresh_ignore = not (root / DEVKIT_GITIGNORE).exists()
    prior_personal = (
        local_render.recorded_paths(root) | _deployed_personal(root, deployed, old_files)
    ) & old_files.keys()
    for name in set(personal) | (prior_personal & changes.keys()):
        local_render.require_ignored(root, name, planned_ignore=fresh_ignore and name.startswith(".devkit/managed/"))
    block_hash, block_notices = _plan_guidance_block(
        root,
        changes,
        actions,
        conflicts,
        previous.guidance_block if previous else None,
        _render_block(selection, inventory),
        enabled=config.guidance_block,
    )
    conflicts.check()
    # A file where a destination's directory must be stops the sync in planning, ``--dry-run`` included.
    require_writable(root, changes)
    notices.extend(block_notices)
    overrides = _carried_overrides(root, installed, previous, inventory.overrides)
    receipt = _build_receipt(selection, inventory, overrides, seeded, block_hash, selected_environment)
    notices.extend(engine_notices(receipt.asset_records))
    if config_update is not None and config_update.text is not None:
        changes[CONFIG_PATH] = Content(
            config_update.text.encode(), config_update.before.mode if config_update.before else 0o644
        )
    if save_environment:
        local_render.plan_environment(root, environment, changes, actions)
    if not locked:
        # A personal-only update never rewrites the canonical receipt for the running tool version.
        personalized = set(personal) | prior_personal
        canonical_changes = {
            name: value for name, value in changes.items() if name != LOCAL_CONFIG_PATH and name not in personalized
        }
        receipt_changes: Changes = dict(canonical_changes)
        notices.extend(_plan_receipt(previous, receipt, receipt_changes, actions))
        if RECEIPT_PATH in receipt_changes:
            changes[RECEIPT_PATH] = receipt_changes[RECEIPT_PATH]
    pending_receipt = changes.get(RECEIPT_PATH)
    receipt_bytes = (
        pending_receipt.data
        if pending_receipt
        else ((root / RECEIPT_PATH).read_bytes() if previous is not None else receipt_content(receipt).data)
    )
    local_render.plan_ledger(root, personal, receipt_bytes, changes, actions, environment=selected_environment)
    if local_render.LOCAL_RENDER in changes or (root / local_render.LOCAL_RENDER).exists():
        local_render.require_ignored(root, local_render.LOCAL_RENDER, planned_ignore=fresh_ignore)
    if locked:
        locked_actions = [a for a in actions if a.path not in (LOCAL_CONFIG_PATH, local_render.LOCAL_RENDER)]
        tracked_changes = (
            bool(changes) and git_toplevel(root) is not None and bool(run_git(root, "ls-files", "--", *changes).strip())
        )
        if tracked_changes or not _restores_only(previous, receipt, locked_actions, deployed):
            raise _receipt_stale(previous, receipt, actions, deployed)
    require_writable(root, changes)
    local_render.unchanged(root, captured)
    seen = _read_seen_bundles(root)
    if not dry_run:
        apply_changes(root, changes)

    def finish() -> SyncResult:
        if not dry_run:
            _record_seen_bundles(root, installed, seen)
            _record_deployed(
                root,
                {name: FileRecord(*signature(content)) for name, content in effective.files.items()},
                deployed,
                set(personal),
            )
        result = _sync_result(
            root,
            installed,
            selection,
            inventory,
            old_files.keys() | inventory.files.keys(),
            actions,
            notices,
            opted_out=config.opted_out,
            seen=seen,
            auto_selected=auto_selected,
            dry_run=dry_run,
        )

        result.execution_environment = selected_environment
        return result

    return finish


class RecoverProject(BaseUseCase):
    """Execute the recover project application operation."""

    def execute(self, root: Path) -> int:
        """Roll back an interrupted synchronization; return the number of files restored."""
        root = require_project_dir(root)
        with project_lock(root):
            return recover_locked(root)


class SyncRegistrations(BaseUseCase):
    """Execute the sync registrations application operation."""

    def execute(self, root: Path) -> registrations.RegistrationPlan:
        """Reconcile only optional local registrations after locked worktree asset restoration."""
        root = require_project_dir(root)
        guard_execution()
        with registrations.clone_lock(root), project_lock(root):
            guard_execution()
            registrations.recover(root)
            result = registrations.plan(root, read_config(root).agents)
            registrations.apply(result)
        return result
