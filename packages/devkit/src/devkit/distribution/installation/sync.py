"""``devkit sync``: converge a workspace to its selection, all or nothing."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
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
from devkit.distribution.content import Content, json_content, same_content, signature
from devkit.distribution.errors import (
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
from devkit.distribution.installation import guidance_block
from devkit.distribution.installation.config import (
    ConfigUpdate,
    ProjectConfig,
    default_selection,
    effective_selection,
    missing_selection_error,
    read_config,
)
from devkit.distribution.installation.discovery import InstalledBundle, unusable_notices
from devkit.distribution.installation.extensions import run_post_sync
from devkit.distribution.installation.inventory import GENERATED_SKILLS, Inventory, Seed, desired_inventory
from devkit.distribution.installation.overrides import Drift, overridden_files
from devkit.distribution.installation.receipt import read_receipt, receipt_content, receipt_json
from devkit.distribution.installation.results import Action, SyncResult, Unselected
from devkit.distribution.installation.transaction import (
    apply_changes,
    atomic_write,
    project_lock,
    recover_locked,
    require_no_journal,
)
from devkit.distribution.installation.workspace import (
    AGENTS_FILE,
    DEPLOYED,
    DEVKIT_GITIGNORE,
    DEVKIT_GITIGNORE_TEXT,
    METADATA,
    SEEN_BUNDLES,
    checked_path,
    owned_prefix,
    snapshot,
)

TOOL_PACKAGE = "devkit-agt"
EDITED_FILE_FIX = (
    "Keep the edit: copy it aside, run `devkit override create <bundle>:<asset>` and reapply it there;"
    " discard it: delete the file and run `devkit sync`"
)
UNOWNED_FILE_FIX = "Move each unowned file out of the way (or delete it), then run `devkit sync`"

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
        if self.block == "modified":
            parts.append(
                (
                    f"user-modified guidance block: {AGENTS_FILE}",
                    f"Restore the block between the markers (for example `git checkout -- {AGENTS_FILE}`),"
                    " keep project text outside them, then run `devkit sync`",
                    "Whether to discard the edit inside the devkit block markers",
                )
            )
        elif self.block == "unowned":
            parts.append(
                (
                    f"unowned guidance block already exists: {AGENTS_FILE}",
                    f"Remove the devkit block markers from {AGENTS_FILE}, then run `devkit sync`",
                    f"Whether to remove the devkit block markers that {AGENTS_FILE} already has,"
                    " so sync can write its own",
                )
            )
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
        current = snapshot(root, name)
        after = desired.get(name)
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


def _plan_guidance_block(
    root: Path,
    changes: Changes,
    actions: list[Action],
    conflicts: _Conflicts,
    recorded: str | None,
    *,
    enabled: bool,
    bundles: list[str],
    entry_skills: list[str],
    fragments: list[str],
) -> tuple[str | None, list[AdvisoryError]]:
    """Add the root ``AGENTS.md`` change for the managed block; return the hash to record and any notice.

    The block is owned like a managed file: a hand edit (digest differs from
    the receipt) is a conflict, a removed block is written again, and the bytes
    outside the markers are never touched. Markers the receipt does not know
    are a conflict, unless the block is exactly the one sync writes: that one
    is adopted. With ``enabled`` off the receipt stops recording the block: one
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
    desired = guidance_block.render(bundles, entry_skills, fragments)
    if existing is not None:
        if recorded is None and guidance_block.normalize(existing) != desired:
            conflicts.block = "unowned"
        elif recorded is not None and guidance_block.digest(existing) != recorded:
            conflicts.block = "modified"
    if existing is None or guidance_block.normalize(existing) != desired:
        changes[AGENTS_FILE] = Content(guidance_block.compose(text, desired).encode("utf-8"), mode)
        actions.append(Action(AGENTS_FILE, "create" if current is None else "update"))
    return guidance_block.digest(desired), []


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


def _plan_devkit_gitignore(root: Path, changes: Changes, actions: list[Action]) -> None:
    """Seed ``.devkit/.gitignore`` (managed copies, transient state) when it is absent; never touch an existing one.

    A bundle that seeds the same path takes precedence.
    """
    if DEVKIT_GITIGNORE not in changes and snapshot(root, DEVKIT_GITIGNORE) is None:
        changes[DEVKIT_GITIGNORE] = Content(DEVKIT_GITIGNORE_TEXT.encode("utf-8"), 0o644)
        actions.append(Action(DEVKIT_GITIGNORE, "seed"))


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
    return [
        ToolVersionChangedNotice(
            f"{before.package} {before.version} -> {after.version}: the receipt now records the running version"
        )
    ]


def _without_tool(receipt: Receipt) -> dict[str, object]:
    value = receipt_json(receipt)
    value.pop("tool", None)
    return value


def _restores_only(previous: Receipt | None, receipt: Receipt, actions: list[Action]) -> bool:
    """Whether the sync only creates missing files exactly as the committed receipt records them (``--locked``).

    The receipt must be unchanged (the writing tool's version aside), so each
    created file has the recorded signature; anything else (an update, a
    removal, a seed, the guidance block, a new receipt) changes committed state.
    """
    return (
        previous is not None
        and _without_tool(receipt) == _without_tool(previous)
        and all(item.action == "create" and item.path in previous.file_records for item in actions)
    )


STALE_DETAILS = 20  # planned writes listed in a RECEIPT_STALE refusal


def _receipt_stale(previous: Receipt | None, receipt: Receipt, actions: list[Action]) -> ReceiptStaleError:
    """The ``--locked`` refusal: why the committed state is out of date, and what a plain sync would write.

    ``target_files`` names only committed state: the receipt when it would change, and the planned paths that no
    receipt records as a managed or projected file (the root ``AGENTS.md``, seeded files, ``.devkit/.gitignore``).
    Managed and projected files are listed in the details with the other planned writes: committed state first,
    then the other changes, then the restores ``--locked`` would have made, so the cap never hides the reason.
    """
    recorded = previous.file_records if previous is not None else {}
    unrecorded = [item.path for item in actions if item.path not in recorded and item.path not in receipt.file_records]
    if previous is None:
        reason, targets = "there is no committed receipt to restore from", [RECEIPT_PATH, *unrecorded]
    elif _without_tool(receipt) != _without_tool(previous):
        reason, targets = "the installed bundles no longer match the committed receipt", [RECEIPT_PATH, *unrecorded]
    else:
        reason, targets = "committed files no longer match the receipt", unrecorded
    committed = set(unrecorded)
    ordered = sorted(
        actions,
        key=lambda item: 0 if item.path in committed else 2 if item.action == "create" and item.path in recorded else 1,
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


def _record_deployed(root: Path, files: Mapping[str, FileRecord], recorded: dict[str, FileRecord]) -> None:
    """Remember the signatures the sync left: after a commit every file the receipt records matches it."""
    if dict(files) != recorded:
        data = {"files": {name: {"sha256": r.sha256, "mode": r.mode} for name, r in sorted(files.items())}}
        atomic_write(root, DEPLOYED, json_content(data))


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
) -> SyncResult:
    """Deploy the bundles selected in ``config.toml`` and the built-in bundles it does not opt out of.

    ``agents``, ``presets`` (per-bundle replacements) and ``deselect`` layer
    one-run selections over the configuration. ``save`` persists a selection
    instead: it renders the configuration edit under the project lock, from the
    configuration as it is then, so concurrent selection commands never lose
    an edit; the edit is written before the sync reads the configuration and
    put back when the sync fails, and post-sync extensions see it. ``save`` is never
    called on ``dry_run``. ``locked`` keeps the committed state: the sync only
    restores files the receipt records, or raises ``ReceiptStaleError``
    (``RECEIPT_STALE``) without writing anything. Post-sync extensions run after
    the project lock is released, except on a dry run.
    """
    root = require_project_dir(root)
    with project_lock(root):
        update = save() if save is not None and not dry_run else None
        if update is not None:
            update.apply()
        try:
            finish = commit_locked(
                root, installed, agents=agents, presets=presets, deselect=deselect, dry_run=dry_run, locked=locked
            )
        except BaseException:
            if update is not None:
                update.revert()
            raise
        result = finish()
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
) -> Callable[[], SyncResult]:
    """Plan a sync and, unless ``dry_run``, commit it; the caller holds the project lock. Runs no post-sync extension.

    Returns the step that follows the commit (recording the installed bundles,
    scanning for stray files, building the result). A failure there leaves the
    committed files in place, so a caller that undoes its own writes when the
    sync fails calls it outside that scope. ``rebaseline`` (``bundle, asset``)
    takes the current upstream as the baseline of that asset's override, for
    ``devkit override create``, which has just written the baseline copies.
    ``locked`` commits only when the sync restores files exactly as the receipt
    records them (``_restores_only``), without writing the receipt; otherwise
    it raises ``ReceiptStaleError`` before any write.
    """
    require_no_journal(root)
    config = read_config(root)
    previous = read_receipt(root)
    selection = _resolve_selection(installed, config, previous, agents, presets, deselect)
    auto_selected = _new_auto_selected(installed, config, previous, selection, presets or {})
    previous_overrides = {b: dict(r) for b, r in previous.overrides.items()} if previous else {}
    if rebaseline is not None:
        previous_overrides.get(rebaseline[0], {}).pop(rebaseline[1], None)
    inventory = desired_inventory(
        [item for item in installed if item.bundle.name in selection.presets],
        {name: list(values) for name, values in selection.presets.items()},
        list(selection.agents),
        root=root,
        previous_overrides=previous_overrides,
    )
    if config.override_drift == "block":
        _refuse_override_drift(inventory.drift)
    old_files = dict(previous.file_records) if previous else {}
    changes: Changes = {}
    actions: list[Action] = []
    conflicts = _Conflicts()
    notices = unusable_notices(installed, selection.presets)
    deployed = read_deployed(root)
    notices.extend(_plan_managed_files(root, old_files, deployed, inventory.files, changes, actions, conflicts))
    seeded = _plan_seeds(root, inventory.seeds, changes, actions)
    _plan_devkit_gitignore(root, changes, actions)
    block_hash, block_notices = _plan_guidance_block(
        root,
        changes,
        actions,
        conflicts,
        previous.guidance_block if previous else None,
        enabled=config.guidance_block,
        bundles=list(selection.presets),
        entry_skills=[kind for kind in GENERATED_SKILLS if any(asset.kind == kind for asset in inventory.assets)],
        fragments=inventory.fragments(),
    )
    conflicts.check()
    notices.extend(block_notices)
    overrides = _carried_overrides(root, installed, previous, inventory.overrides)
    receipt = _build_receipt(selection, inventory, overrides, seeded, block_hash)
    if locked:
        if not _restores_only(previous, receipt, actions):
            raise _receipt_stale(previous, receipt, actions)
    else:
        notices.extend(_plan_receipt(previous, receipt, changes, actions))
    seen = _read_seen_bundles(root)
    if not dry_run:
        apply_changes(root, changes)

    def finish() -> SyncResult:
        if not dry_run:
            _record_seen_bundles(root, installed, seen)
            _record_deployed(root, receipt.file_records, deployed)
        return _sync_result(
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

    return finish


def recover_project(root: Path) -> int:
    """Roll back an interrupted synchronization; return the number of files restored."""
    root = require_project_dir(root)
    with project_lock(root):
        return recover_locked(root)
