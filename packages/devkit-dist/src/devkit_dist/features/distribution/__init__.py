"""Devkit bundle distribution: validate and package bundles, synchronize them into projects.

The library surface below is what the ``devkit`` distribution commands use.
Results are frozen dataclasses whose ``to_dict()`` is the JSON object the
command prints (see ``installation.results``, ``installation.status`` and
``installation.plan``). Every operation raises an ``AdvisoryError``: a
``DistributionError`` subclass from ``devkit_dist.features.distribution.models.errors``
(``BUNDLE_INVALID``, ``SYNC_CONFLICT``, ``LOCK_HELD``, ...) or a
``devkit_dist.base.errors`` error it passes through (``RECEIPT_INVALID``,
``CONFIG_INVALID``, ``ARGUMENT_INVALID``). What a successful sync still
reports is collected as coded ``SyncNotice`` entries in
``SyncResult.notices``. The receipt model is ``devkit_dist.features.project.repositories.receipt``.
"""

from devkit_dist.features.distribution.models.errors import (
    BundleConflictError,
    BundleError,
    ConflictError,
    DistributionError,
    GuidanceBlockError,
    LockHeldError,
    NotSynchronizedError,
    OrphanLeftNotice,
    OverrideDriftError,
    PackageError,
    PendingTransactionError,
    PostSyncExtensionFailedNotice,
    PostSyncNotice,
    RecoveryError,
    SelectionError,
    SyncNotice,
    ToolVersionChangedNotice,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.models.results import (
    ContextResult,
    OverrideChange,
    OverrideDiff,
    OverrideStatus,
    PlaybookResult,
    SearchResult,
    SyncResult,
)
from devkit_dist.features.distribution.services.bundles import Asset, BuildResult, Bundle, build_bundle, load_bundle
from devkit_dist.features.distribution.services.installation.config import ProjectConfig, read_config, update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle, discover_bundles
from devkit_dist.features.distribution.services.installation.plan import BundlePlan, plan_bundle
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.usecases.context import get_context
from devkit_dist.features.distribution.usecases.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit_dist.features.distribution.usecases.playbook_get import get_playbook
from devkit_dist.features.distribution.usecases.playbook_search import search_playbooks
from devkit_dist.features.distribution.usecases.status import (
    ProjectListing,
    ProjectStatus,
    get_project_listing,
    get_project_status,
)
from devkit_dist.features.distribution.usecases.sync import recover_project, sync_project

__all__ = [
    "Asset",
    "BuildResult",
    "Bundle",
    "BundleConflictError",
    "BundleError",
    "BundlePlan",
    "ConflictError",
    "ContextResult",
    "DistributionError",
    "GuidanceBlockError",
    "InstalledBundle",
    "LockHeldError",
    "NotSynchronizedError",
    "OrphanLeftNotice",
    "OverrideChange",
    "OverrideDiff",
    "OverrideDriftError",
    "OverrideStatus",
    "PackageError",
    "PendingTransactionError",
    "PlaybookResult",
    "PostSyncExtensionFailedNotice",
    "PostSyncNotice",
    "ProjectConfig",
    "ProjectListing",
    "ProjectStatus",
    "RecoveryError",
    "SearchResult",
    "SelectionError",
    "SyncNotice",
    "SyncResult",
    "ToolVersionChangedNotice",
    "UnsafeWorkspaceError",
    "accept_override",
    "build_bundle",
    "create_override",
    "diff_override",
    "discover_bundles",
    "get_context",
    "get_playbook",
    "get_project_listing",
    "get_project_status",
    "list_overrides",
    "load_bundle",
    "plan_bundle",
    "read_config",
    "read_receipt",
    "recover_project",
    "remove_override",
    "search_playbooks",
    "sync_project",
    "update_config",
]
