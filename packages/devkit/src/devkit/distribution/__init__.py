"""Devkit bundle distribution: validate and package bundles, synchronize them into projects.

The library surface below is what the ``devkit`` distribution commands use;
results are JSON-shaped ``TypedDict`` values (see ``installation.results``).
Every operation raises an ``AdvisoryError``: a ``DistributionError`` subclass
from ``devkit.distribution.errors`` (``BUNDLE_INVALID``, ``SYNC_CONFLICT``,
``LOCK_HELD``, ...) or a ``devkit.core`` error it passes through
(``RECEIPT_INVALID``, ``CONFIG_INVALID``). The receipt model is
``devkit.core.receipt``.
"""

from .bundles import Asset, Bundle, build_bundle, load_bundle
from .errors import (
    ArgumentError,
    BundleError,
    ConflictError,
    DistributionError,
    LockHeldError,
    NotSynchronizedError,
    OverrideDriftError,
    PackageError,
    PendingTransactionError,
    RecoveryError,
    SelectionError,
    UnsafeWorkspaceError,
)
from .installation.config import ProjectConfig, read_config, update_config
from .installation.context import get_context
from .installation.discovery import InstalledBundle, discover_bundles
from .installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from .installation.plan import BundlePlan, plan_bundle
from .installation.playbook_search import search_playbooks
from .installation.receipt import read_receipt
from .installation.results import (
    ContextResult,
    OverrideChange,
    OverrideDiff,
    OverrideStatus,
    SearchResult,
    SyncResult,
)
from .installation.status import ProjectListing, ProjectStatus, project_listing, project_status
from .installation.sync import recover_project, sync_project

__all__ = [
    "ArgumentError",
    "Asset",
    "Bundle",
    "BundleError",
    "BundlePlan",
    "ConflictError",
    "ContextResult",
    "DistributionError",
    "InstalledBundle",
    "LockHeldError",
    "NotSynchronizedError",
    "OverrideChange",
    "OverrideDiff",
    "OverrideDriftError",
    "OverrideStatus",
    "PackageError",
    "PendingTransactionError",
    "ProjectConfig",
    "ProjectListing",
    "ProjectStatus",
    "RecoveryError",
    "SearchResult",
    "SelectionError",
    "SyncResult",
    "UnsafeWorkspaceError",
    "accept_override",
    "build_bundle",
    "create_override",
    "diff_override",
    "discover_bundles",
    "get_context",
    "list_overrides",
    "load_bundle",
    "plan_bundle",
    "project_listing",
    "project_status",
    "read_config",
    "read_receipt",
    "recover_project",
    "remove_override",
    "search_playbooks",
    "sync_project",
    "update_config",
]
