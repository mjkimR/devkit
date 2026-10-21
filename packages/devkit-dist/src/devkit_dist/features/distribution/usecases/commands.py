"""Application operations exposed to distribution command adapters."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from devkit_core.base.errors import ArgumentError

from devkit_dist.features.distribution.models.errors import SelectionError
from devkit_dist.features.distribution.models.results import SyncResult
from devkit_dist.features.distribution.models.settings import DEFAULT_PRESET, SLUG
from devkit_dist.features.distribution.services.bundles import build_bundle, load_bundle
from devkit_dist.features.distribution.services.installation.config import (
    effective_selection,
    merge_selection,
    prepare_config_update,
    read_config,
    resolve_selection,
)
from devkit_dist.features.distribution.services.installation.discovery import (
    InstalledBundle,
    discover_bundles,
    unusable_bundles,
)
from devkit_dist.features.distribution.services.installation.plan import plan_bundle
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.local_config import read_effective_config
from devkit_dist.features.project.services.presentation import resolve_language

ConfigEdit = Callable[[list[InstalledBundle], dict[str, list[str]]], dict[str, Any]]


def _parse_selections(values: tuple[str, ...], param_hint: str) -> dict[str, list[str]]:
    """Parse ``bundle[:preset]`` values; repeating a bundle selects a union, a bare bundle its default preset.

    A bare bundle is recorded as ``DEFAULT_PRESET``, so ``starter starter:extra`` keeps the default preset.
    """
    selected: dict[str, list[str]] = {}
    for value in values:
        name, separator, preset = value.partition(":")
        if not SLUG.fullmatch(name) or (separator and not SLUG.fullmatch(preset)):
            raise ArgumentError(
                f"{param_hint}: expected bundle[:preset] slugs: {value}",
                target_files=[param_hint],
                fix="Pass lowercase bundle slugs, optionally with :<preset>",
            )
        presets = selected.setdefault(name, [])
        entry = preset if separator else DEFAULT_PRESET
        if entry not in presets:
            presets.append(entry)
    return selected


def _sync_and_save(
    root: Path,
    *,
    save: ConfigEdit | None,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    merge: bool = False,
    deselect: tuple[str, ...] = (),
    dry_run: bool = False,
    locked: bool = False,
    environment: str | None = None,
    save_environment: bool = True,
) -> SyncResult:
    """Synchronize; ``save`` builds a configuration edit that the sync renders and writes under the project lock.

    ``merge`` joins ``presets`` with what each bundle already deploys, read
    from the configuration when the edit is rendered, instead of replacing it.
    Without ``save``, or on ``dry_run``, the selection applies to this run only.
    ``deselect`` applies to the run in either case, so a bundle the edit cannot
    name (one the receipt keeps deployed without an installed package) leaves
    the receipt.
    """
    with discover_bundles() as installed:
        requested = resolve_selection(installed, presets or {})

        def selected() -> dict[str, list[str]]:
            return merge_selection(installed, read_config(root), requested) if merge else requested

        if save is not None and not dry_run:
            return sync_project(
                root,
                installed,
                deselect=deselect,
                environment=environment,
                save_environment=save_environment,
                save=lambda: prepare_config_update(root, **save(installed, selected())),
            )
        selection = selected()
        if save is not None:
            save(installed, selection)  # a preview refuses what the command would refuse
        return sync_project(
            root,
            installed,
            agents=agents,
            presets=selection,
            deselect=deselect,
            dry_run=dry_run,
            locked=locked,
            environment=environment,
            save_environment=save_environment,
        )


def validate_source(source: Path) -> dict[str, object]:
    loaded = load_bundle(source)
    return {"name": loaded.name, "version": loaded.version, "assets": len(loaded.assets)}


def plan_source(source: Path, preset: str | None, agents: tuple[str, ...]):
    return plan_bundle(load_bundle(source), preset, list(agents) or None)


def build_source(source: Path, output: Path):
    return build_bundle(load_bundle(source), output)


def show_configuration(root: Path) -> dict[str, object]:
    with project_lock(root, shared=True):
        read_config(root)
        result = read_effective_config(root)
        language = resolve_language(root)
    return {
        "configuration": result.values,
        "sources": result.sources,
        "execution_environment": result.values["execution"]["environment"],
        "presentation_language": asdict(language),
    }


def remove_selection(root: Path, bundles: tuple[str, ...], *, dry_run: bool = False) -> SyncResult:
    def save(installed: list[InstalledBundle], _selected: dict[str, list[str]]) -> dict[str, Any]:
        config = read_config(root)
        selected = effective_selection(installed, config, read_receipt(root))
        missing = sorted(set(bundles) - set(selected))
        if missing:
            raise SelectionError(f"bundle is not selected: {missing}", fix="List selected bundles with `devkit list`")
        # Deleting an entry would not deselect a bundle selected without one (auto-selected, or kept deployed
        # because its package no longer loads), so those are opted out. One kept deployed without an installed
        # package needs no entry: the run's deselection drops it from the receipt, and nothing selects it again.
        absent = set(selected) - set(config.presets) - {item.bundle.name for item in installed}
        absent -= unusable_bundles(installed).keys()
        automatic = {item.bundle.name for item in installed if item.auto_selected} | (
            set(selected) - set(config.presets) - absent
        )
        return {
            "deselect": [name for name in bundles if name not in automatic | absent],
            "opt_out": [name for name in bundles if name in automatic],
        }

    return _sync_and_save(root, save=save, deselect=bundles, dry_run=dry_run)


def preview_config_template(root: Path):
    """Preview the project configuration template without mutation."""
    from devkit_dist.features.distribution.services.installation.config import preview_config_template as preview

    return preview(root)


def refresh_config_template(root: Path):
    """Apply missing configuration template keys under the project lock."""
    from devkit_dist.features.distribution.services.installation.config import refresh_config_template as refresh

    return refresh(root)
