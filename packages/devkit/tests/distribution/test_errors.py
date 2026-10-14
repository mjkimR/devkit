"""Every distribution error is an ``AdvisoryError`` with a stable code and the directive its condition needs."""

from __future__ import annotations

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode, Level
from devkit.distribution import errors


@pytest.mark.parametrize(
    ("cls", "code", "mode"),
    [
        (errors.DistributionError, "DISTRIBUTION_FAILED", ActionMode.MAINTENANCE),
        (errors.BundleError, "BUNDLE_INVALID", ActionMode.INPUT_ERROR),
        (errors.PackageError, "BUNDLE_PACKAGE_INVALID", ActionMode.MAINTENANCE),
        (errors.SelectionError, "SELECTION_INVALID", ActionMode.INPUT_ERROR),
        (errors.NotSynchronizedError, "NOT_SYNCHRONIZED", ActionMode.AUTO),
        (errors.ConflictError, "SYNC_CONFLICT", ActionMode.INTERACTION),
        (errors.BundleConflictError, "BUNDLE_CONFLICT", ActionMode.INTERACTION),
        (errors.GuidanceBlockError, "GUIDANCE_BLOCK_INVALID", ActionMode.INPUT_ERROR),
        (errors.OverrideDriftError, "OVERRIDE_DRIFT", ActionMode.BLOCKED),
        (errors.UnsafeWorkspaceError, "WORKSPACE_UNSAFE", ActionMode.BLOCKED),
        (errors.LockHeldError, "LOCK_HELD", ActionMode.DEFER),
        (errors.PendingTransactionError, "TRANSACTION_PENDING", ActionMode.AUTO),
        (errors.RecoveryError, "RECOVERY_BLOCKED", ActionMode.HALT),
    ],
)
def test_error_classes_carry_code_and_mode(cls: type[errors.DistributionError], code: str, mode: ActionMode) -> None:
    error = cls("x")
    assert isinstance(error, AdvisoryError) and not isinstance(error, ValueError)
    assert (error.code, error.mode, error.exit_code) == (code, mode, ExitCode.ERROR)


@pytest.mark.parametrize(
    ("cls", "code", "level"),
    [
        (errors.OrphanLeftNotice, "ORPHAN_LEFT", Level.WARNING),
        (errors.StrayFilesNotice, "MANAGED_FILE_STRAY", Level.WARNING),
        (errors.PostSyncExtensionFailedNotice, "POST_SYNC_EXTENSION_FAILED", Level.WARNING),
        (errors.UnprojectedNotice, "ASSET_UNPROJECTED", Level.NOTICE),
        (errors.BundleUnselectedNotice, "BUNDLE_UNSELECTED", Level.NOTICE),
        (errors.ToolVersionChangedNotice, "TOOL_VERSION_CHANGED", Level.NOTICE),
        (errors.PostSyncNotice, "POST_SYNC_NOTICE", Level.NOTICE),
    ],
)
def test_notices_are_coded_and_never_fail(cls: type[errors.SyncNotice], code: str, level: Level) -> None:
    notice = cls("x")
    mode = ActionMode.CONTINUE if level is Level.WARNING else ActionMode.NOTE
    assert (notice.code, notice.level, notice.mode, notice.exit_code) == (code, level, mode, ExitCode.OK)
    assert notice.lines()[0].startswith("[WARN]   " if level is Level.WARNING else "[NOTICE] ")


def test_fixes_name_the_command_that_repairs_the_state() -> None:
    assert errors.NotSynchronizedError("x").fix == "devkit sync"
    assert errors.PendingTransactionError("x").fix == "devkit recover"
    assert errors.LockHeldError("x").retry_after == errors.LOCK_RETRY_AFTER


def test_the_project_lock_error_is_also_the_core_lock_error() -> None:
    from devkit.core import LockHeldError as CoreLockHeldError

    error = errors.LockHeldError("x", what="waiting for the lock", seconds=10.0)
    assert isinstance(error, CoreLockHeldError) and isinstance(error, errors.DistributionError)
    assert (error.code, error.what, error.seconds, error.retry_after) == (
        "LOCK_HELD",
        "waiting for the lock",
        10.0,
        errors.LOCK_RETRY_AFTER,
    )
