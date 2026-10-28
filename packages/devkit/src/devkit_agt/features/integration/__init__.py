"""Methodology-neutral, approval-bound local integration on devkit worktree and host contracts."""

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
from devkit_agt.features.integration.repositories.snapshots import _snapshot_root as snapshot_root
from devkit_agt.features.integration.repositories.snapshots import build_snapshot, populate_managed_files
from devkit_agt.features.integration.usecases.project import check as check_project_readiness
from devkit_agt.features.integration.usecases.project import touched_workflow_units
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
