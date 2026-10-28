"""Methodology-neutral, approval-bound local integration on devkit worktree and host contracts."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devkit_agt.features.integration.repositories.snapshots import _snapshot_root as snapshot_root
    from devkit_agt.features.integration.repositories.snapshots import build_snapshot, populate_managed_files
    from devkit_agt.features.integration.usecases.project import check as check_project_readiness
    from devkit_agt.features.integration.usecases.project import touched_workflow_units

from devkit_agt.features.integration.models.contracts import (
    CleanupResult,
    CleanupScope,
    CleanupTarget,
    Evidence,
    IntegrationContext,
    IntegrationRequest,
    IntegrationResult,
    Readiness,
    ReadinessProvider,
    ScopedCleanup,
    Task,
)
from devkit_agt.features.integration.models.errors import (
    AuthorityError,
    CleanupContractError,
    CleanupIncompleteWarning,
    IntegrationConfigError,
    IntegrationError,
    ProviderError,
    ReadinessError,
    ReceiptConflictError,
    ReceiptReaderChangedError,
    RuleRuntimeMismatchError,
    RuntimeLocationError,
    StaleRequestError,
    TargetMovedError,
)
from devkit_agt.features.integration.usecases.service import IntegrationService

__all__ = [
    "AuthorityError",
    "CleanupContractError",
    "CleanupIncompleteWarning",
    "CleanupResult",
    "CleanupScope",
    "CleanupTarget",
    "Evidence",
    "IntegrationConfigError",
    "IntegrationContext",
    "IntegrationError",
    "IntegrationRequest",
    "IntegrationResult",
    "IntegrationService",
    "ProviderError",
    "Readiness",
    "ReadinessError",
    "ReadinessProvider",
    "ReceiptConflictError",
    "ReceiptReaderChangedError",
    "RuleRuntimeMismatchError",
    "RuntimeLocationError",
    "ScopedCleanup",
    "StaleRequestError",
    "TargetMovedError",
    "Task",
    "build_snapshot",
    "check_project_readiness",
    "populate_managed_files",
    "snapshot_root",
    "touched_workflow_units",
]


def __getattr__(name: str):
    from importlib import import_module

    exports = {
        "build_snapshot": ("repositories.snapshots", "build_snapshot"),
        "populate_managed_files": ("repositories.snapshots", "populate_managed_files"),
        "snapshot_root": ("repositories.snapshots", "_snapshot_root"),
        "check_project_readiness": ("usecases.project", "check"),
        "touched_workflow_units": ("usecases.project", "touched_workflow_units"),
    }
    if name not in exports:
        raise AttributeError(name)
    module, symbol = exports[name]
    return getattr(import_module(f"{__name__}.{module}"), symbol)
