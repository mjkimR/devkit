"""Application operations exposed to distribution command adapters."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_dist.features.distribution.models.errors import OverrideRetainedNotice, SelectionError
from devkit_dist.features.distribution.models.invocation import AGENT_INVOCATION
from devkit_dist.features.distribution.models.results import (
    ConfigurationReport,
    OverrideChange,
    OverrideDiff,
    OverrideStatus,
    SyncResult,
)
from devkit_dist.features.distribution.services.bundles import build_bundle, load_bundle
from devkit_dist.features.distribution.services.installation.config import (
    ConfigTemplateResult,
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
from devkit_dist.features.distribution.services.installation.plan import BundlePlan, plan_bundle
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.local_config import read_effective_config
from devkit_dist.features.project.repositories.receipt import OVERRIDES_PATH
from devkit_dist.features.project.services.presentation import language_notices, resolve_language

if TYPE_CHECKING:
    from .status import ProjectListing, ProjectStatus

ConfigEdit = Callable[[list[InstalledBundle], dict[str, list[str]]], dict[str, Any]]


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
    Without ``save`` the selection applies to this run only; on ``dry_run`` the edit is
    rendered and listed (``.devkit/config.toml``) but never written. ``deselect`` applies to the run in either case, so a bundle the edit cannot
    name (one the receipt keeps deployed without an installed package) leaves
    the receipt.
    """
    with discover_bundles() as installed:
        requested = resolve_selection(installed, presets or {})

        def selected() -> dict[str, list[str]]:
            return merge_selection(installed, read_config(root), requested) if merge else requested

        if save is not None:
            return sync_project(
                root,
                installed,
                deselect=deselect,
                dry_run=dry_run,
                environment=environment,
                save_environment=save_environment,
                save=lambda: prepare_config_update(root, **save(installed, selected())),
            )
        return sync_project(
            root,
            installed,
            agents=agents,
            presets=selected(),
            deselect=deselect,
            dry_run=dry_run,
            locked=locked,
            environment=environment,
            save_environment=save_environment,
        )


class SyncSelection(BaseUseCase):
    """Execute the sync selection application operation."""

    def execute(
        self,
        root: Path,
        *,
        agents: list[str] | None = None,
        presets: dict[str, list[str]] | None = None,
        save: bool = True,
        dry_run: bool = False,
        locked: bool = False,
        environment: str | None = None,
    ) -> SyncResult:
        """Replace requested selections and synchronize, persisting them unless ``save`` is false.

        Unspecified selections retain their configured values. An empty agent list
        explicitly clears agents. Configuration and outputs commit together under
        the project lock; a dry run previews the same operation without writing.
        """
        if locked and (agents is not None or presets or dry_run or not save):
            raise ArgumentError("locked synchronization cannot change selections or preview; use an ordinary sync")
        persist = save and (bool(presets) or agents is not None)
        return _sync_and_save(
            root,
            save=(lambda _installed, selected: {"agents": agents, "presets": selected}) if persist else None,
            agents=agents,
            presets=presets,
            dry_run=dry_run,
            locked=locked,
            environment=environment,
            save_environment=save,
        )


class AddSelection(BaseUseCase):
    """Execute the add selection application operation."""

    def execute(self, root: Path, presets: dict[str, list[str]], *, dry_run: bool = False) -> SyncResult:
        """Union requested presets with current selections and synchronize atomically."""
        return _sync_and_save(
            root,
            save=lambda _installed, selected: {"presets": selected},
            presets=presets,
            merge=True,
            dry_run=dry_run,
        )


class ListProject(BaseUseCase):
    """Execute the list project application operation."""

    def execute(self, root: Path) -> ProjectListing:
        """Discover installed content and read the project listing while resources are available."""
        from .status import get_project_listing

        with discover_bundles() as installed:
            return get_project_listing(root, installed)


class InspectProject(BaseUseCase):
    """Execute the inspect project application operation."""

    def execute(self, root: Path) -> ProjectStatus:
        """Discover installed content and inspect the project while resources are available."""
        from .status import get_project_status

        with discover_bundles() as installed:
            return get_project_status(root, installed)


class CreateProjectOverride(BaseUseCase):
    """Execute the create project override application operation."""

    def execute(self, root: Path, selector: str, *, force: bool = False) -> OverrideChange:
        """Discover upstream content and create an override within its resource lifetime."""
        from .override_commands import create_override

        with discover_bundles() as installed:
            return create_override(root, installed, selector, force=force)


class DiffProjectOverride(BaseUseCase):
    """Execute the diff project override application operation."""

    def execute(self, root: Path, selector: str) -> OverrideDiff:
        """Discover upstream content and compare the override before releasing it."""
        from .override_commands import diff_override

        with discover_bundles() as installed:
            return diff_override(root, installed, selector)


class AcceptProjectOverride(BaseUseCase):
    """Execute the accept project override application operation."""

    def execute(self, root: Path, selector: str) -> OverrideChange:
        """Discover upstream content and accept its baseline before releasing it."""
        from .override_commands import accept_override

        with discover_bundles() as installed:
            return accept_override(root, installed, selector)


class RemoveProjectOverride(BaseUseCase):
    """Execute the remove project override application operation."""

    def execute(self, root: Path, selector: str) -> OverrideChange:
        """Discover upstream content and restore it while removing the override."""
        from .override_commands import remove_override

        with discover_bundles() as installed:
            return remove_override(root, installed, selector)


class ListProjectOverrides(BaseUseCase):
    """Execute the list project overrides application operation."""

    def execute(self, root: Path) -> list[OverrideStatus]:
        """Discover upstream content and collect override drift before releasing it."""
        from .override_commands import list_overrides

        with discover_bundles() as installed:
            return list_overrides(root, installed)


class ValidateSource(BaseUseCase):
    """Execute the validate source application operation."""

    def execute(self, source: Path) -> dict[str, object]:
        loaded = load_bundle(source)
        return {"name": loaded.name, "version": loaded.version, "assets": len(loaded.assets)}


class PlanSource(BaseUseCase):
    """Execute the plan source application operation."""

    def execute(self, source: Path, preset: str | None, agents: tuple[str, ...]) -> BundlePlan:
        return plan_bundle(load_bundle(source), preset, list(agents) or None)


def build_source(source: Path, output: Path):
    return build_bundle(load_bundle(source), output)


class ShowConfiguration(BaseUseCase):
    """Execute the show configuration application operation."""

    def execute(self, root: Path) -> ConfigurationReport:
        with project_lock(root, shared=True):
            read_config(root)
            result = read_effective_config(root)
            language = resolve_language(root)
            notices = language_notices(root)
        return ConfigurationReport(
            configuration=result.values,
            sources=result.sources,
            execution_environment=result.values["execution"]["environment"],
            presentation_language=asdict(language),
            notices=notices,
        )


class RemoveSelection(BaseUseCase):
    """Execute the remove selection application operation."""

    def execute(self, root: Path, bundles: tuple[str, ...], *, dry_run: bool = False) -> SyncResult:
        def save(installed: list[InstalledBundle], _selected: dict[str, list[str]]) -> dict[str, Any]:
            config = read_config(root)
            selected = effective_selection(installed, config, read_receipt(root))
            missing = sorted(set(bundles) - set(selected))
            if missing:
                raise SelectionError(
                    f"bundle is not selected: {missing}", fix=f"List selected bundles with `{AGENT_INVOCATION} list`"
                )
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

        result = _sync_and_save(root, save=save, deselect=bundles, dry_run=dry_run)
        retained = [
            f"{OVERRIDES_PATH}/{name}/" for name in sorted(set(bundles)) if (root / OVERRIDES_PATH / name).is_dir()
        ]
        if retained:
            result.notices.append(
                OverrideRetainedNotice(
                    f"overrides of removed bundles stay in place: {', '.join(retained)}",
                    target_files=retained,
                    fix=f"Delete {', '.join(retained)} to drop them, or `{AGENT_INVOCATION} add <bundle>` to apply them"
                    " again",
                )
            )
        return result


class PreviewConfigTemplate(BaseUseCase):
    """Execute the preview config template application operation."""

    def execute(self, root: Path) -> ConfigTemplateResult:
        """Preview the project configuration template without mutation."""
        from devkit_dist.features.distribution.services.installation.config import preview_config_template as preview

        return preview(root)


class RefreshConfigTemplate(BaseUseCase):
    """Execute the refresh config template application operation."""

    def execute(self, root: Path) -> ConfigTemplateResult:
        """Apply missing configuration template keys under the project lock."""
        from devkit_dist.features.distribution.services.installation.config import refresh_config_template as refresh

        return refresh(root)
